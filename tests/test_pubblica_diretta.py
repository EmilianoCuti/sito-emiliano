"""Test di pubblica_diretta.py — orchestrazione feed + build + commit locale.

Esegui:  python -m unittest discover -s tests -v
La pipeline gira in UNA copia del progetto dentro un repo git temporaneo
(setUpClass: una sola copia, per non ripetere git init/add su Windows).
Il push di rete NON è testato qui (push=False): si verifica a parte con un
dry-run sul repo reale. Parser/feed sono già coperti da test_diretta.py.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

POST_ESEMPIO = """📌 FINANZA OGGI — giovedì 19 novembre 2026, 18:00 (CET) — finestra 14:00-18:00

• Anthropic ha debuttato al Nasdaq: valutazione di 1.500 miliardi di dollari. (15:30, Guardian Tech)

• Apertura indicata del 25% sopra il prezzo di collocamento. (15:43, Bloomberg Markets)

📊 SINTESI MERCATO
• Anthropic esordisce al Nasdaq; l'oro resta sotto pressione.

🔮 PROSPETTIVA
• Da seguire la prima seduta di Anthropic e la tenuta del mercato obbligazionario.

— Fonti: Guardian Tech, Bloomberg Markets
"""


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def feed(tmp):
    with open(os.path.join(tmp, "content", "diretta.json"), encoding="utf-8") as fh:
        return json.load(fh)["diretta"]


class TestLogica(unittest.TestCase):
    """Nessun repo necessario: logica pura e guardia sul post mancante."""

    def test_msg_commit(self):
        import pubblica_diretta as P
        self.assertEqual(P.msg_commit({"data": "2026-11-19", "ora": "18:00"}),
                         "diretta: Finanza Oggi 2026-11-19 18:00")

    def test_post_mancante(self):
        import pubblica_diretta as P
        # la guardia scatta prima di qualsiasi feed/build/git: nessun effetto collaterale
        code, msg = P.pubblica(os.path.join(ROOT, "non_esiste.txt"), ROOT, push=False)
        self.assertEqual(code, 1)
        self.assertIn("FAIL", msg)


class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="sito-pubdiretta-")
        shutil.copytree(ROOT, cls.tmp, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(".git", "sito", "__pycache__",
                                                      "*.pyc", "*.gif", "odd", "tests", "verifica"))
        git(cls.tmp, "init", "-b", "main")
        git(cls.tmp, "config", "user.email", "test@example.com")
        git(cls.tmp, "config", "user.name", "Test")
        git(cls.tmp, "add", "-A")
        git(cls.tmp, "commit", "-m", "baseline")
        cls.post = os.path.join(cls.tmp, "post_fixture.txt")
        with open(cls.post, "w", encoding="utf-8") as fh:
            fh.write(POST_ESEMPIO)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_pipeline_e_dedup(self):
        import pubblica_diretta as P
        # 1) prima pubblicazione: feed + build + commit locale
        code, msg = P.pubblica(self.post, self.tmp, push=False)
        self.assertEqual(code, 0, msg)
        self.assertIn("OK", msg)
        edizioni = feed(self.tmp)
        self.assertEqual(len(edizioni), 1)
        self.assertEqual(edizioni[0]["data"], "2026-11-19")
        self.assertEqual(edizioni[0]["ora"], "18:00")
        with open(os.path.join(self.tmp, "sito", "finanza", "index.html"), encoding="utf-8") as fh:
            self.assertIn("1.500 miliardi", fh.read())
        self.assertIn("diretta: Finanza Oggi 2026-11-19 18:00", git(self.tmp, "log", "--oneline").stdout)
        n1 = git(self.tmp, "rev-list", "--count", "HEAD").stdout.strip()
        # 2) seconda pubblicazione della stessa edizione: dedup, nessun commit nuovo
        code, msg = P.pubblica(self.post, self.tmp, push=False)
        self.assertEqual(code, 0, msg)
        self.assertIn("nessuna modifica", msg)
        self.assertEqual(len(feed(self.tmp)), 1)
        n2 = git(self.tmp, "rev-list", "--count", "HEAD").stdout.strip()
        self.assertEqual(n1, n2)


if __name__ == "__main__":
    unittest.main()