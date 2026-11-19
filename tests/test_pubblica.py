"""Test del pubblicatore add_articolo.py e del build multisezione.

Esegui:  python -m unittest discover -s tests -v
I test di pubblicazione usano una fixture temporanea (non toccano i contenuti
reali); il test di build scrive solo in una cartella temporanea (--out).
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


def fixture(root):
    os.makedirs(os.path.join(root, "content"))
    os.makedirs(os.path.join(root, "data", "raw"))
    site = {
        "autore": {"nome": "Emiliano Cuti"},
        "sezioni": [
            {"id": "inchieste", "titolo": "Cronaca", "url": "inchieste/"},
            {"id": "finanza", "titolo": "Finanza", "url": "finanza/"},
            {"id": "ai", "titolo": "AI", "url": "ai/"},
            {"id": "informatica", "titolo": "Informatica", "url": "informatica/"},
        ],
    }
    with open(os.path.join(root, "content", "site.json"), "w", encoding="utf-8") as fh:
        json.dump(site, fh, ensure_ascii=False)
    with open(os.path.join(root, "content", "inchieste.json"), "w", encoding="utf-8") as fh:
        json.dump({"inchieste": [{"slug": "case-vuote", "titolo": "Case vuote"}], "articoli": []}, fh, ensure_ascii=False)


class TestSlug(unittest.TestCase):
    def test_slugify(self):
        import add_articolo as A
        self.assertEqual(A.slugify("Finanza: ETF & mercati!"), "finanza-etf-mercati")
        self.assertEqual(A.slugify("Perché l'AI cambia il lavoro"), "perche-l-ai-cambia-il-lavoro")

    def test_slug_univoco(self):
        import add_articolo as A
        self.assertEqual(A.prossimo_slug("etf", {"etf"}), "etf-2")
        self.assertEqual(A.prossimo_slug("etf", {"etf", "etf-2"}), "etf-3")


class TestPubblica(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="sito-test-")
        fixture(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _add(self, **kw):
        import add_articolo as A
        base = dict(sezione="finanza", titolo="ETF e mercati", sommario="Sommario.",
                    tema="Mercati", formato="Articolo", data="2026-11-19",
                    markdown="# Titolo\n\nCorpo.")
        base.update(kw)
        return A.aggiungi_articolo(self.tmp, **base)

    def test_articolo_finanza(self):
        e = self._add()
        self.assertEqual(e["sezione"], "finanza")
        self.assertEqual(e["slug"], "etf-e-mercati")
        with open(os.path.join(self.tmp, "content", "inchieste.json"), encoding="utf-8") as fh:
            dati = json.load(fh)
        self.assertEqual(len(dati["articoli"]), 1)
        fonte = os.path.join(self.tmp, "data", "raw", e["fonte"])
        self.assertTrue(os.path.exists(fonte))
        with open(fonte, encoding="utf-8") as fh:
            self.assertIn("Corpo.", fh.read())

    def test_due_stesso_titolo(self):
        a = self._add()
        b = self._add()
        self.assertNotEqual(a["slug"], b["slug"])

    def test_sezione_non_valida(self):
        with self.assertRaises(ValueError):
            self._add(sezione="sport")

    def test_inchiesta_non_valida(self):
        with self.assertRaises(ValueError):
            self._add(sezione="inchieste", inchiesta="inesistente")


class TestBuild(unittest.TestCase):
    def test_build_multisezione(self):
        out = tempfile.mkdtemp(prefix="sito-out-")
        try:
            r = subprocess.run([sys.executable, os.path.join(ROOT, "build.py"), "--out", out],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            for sez in ("finanza", "ai", "informatica"):
                self.assertTrue(os.path.exists(os.path.join(out, sez, "index.html")), sez)
            with open(os.path.join(out, "index.html"), encoding="utf-8") as fh:
                home = fh.read()
            self.assertIn("intro3d-canvas", home)
            self.assertIn("linkedin.com/in/emiliano-cuti-31554819a", home)
            self.assertIn("emiliano-cuti.jpg", home)
            with open(os.path.join(out, "chi-sono", "index.html"), encoding="utf-8") as fh:
                chi = fh.read()
            self.assertIn("mailto:emilianocuti@outlook.it", chi)
            self.assertIn('class="contatti"', chi)
        finally:
            shutil.rmtree(out, ignore_errors=True)


class TestEndToEnd(unittest.TestCase):
    """Regressione: un articolo libero (senza inchiesta) non deve rompere il build."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="sito-e2e-")
        shutil.copytree(ROOT, self.tmp, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(".git", "sito", "__pycache__", "*.pyc"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_pubblica_libero_e_build(self):
        r = subprocess.run([sys.executable, "add_articolo.py", "--sezione", "finanza",
                            "--titolo", "Prova pubblicazione da Hermes",
                            "--sommario", "Articolo di prova.", "--tema", "Mercati",
                            "--data", "2026-11-19", "--testo", "# Prova\n\nCorpo."],
                           cwd=self.tmp, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(self.tmp, "sito", "finanza", "index.html"), encoding="utf-8") as fh:
            self.assertIn("Prova pubblicazione da Hermes", fh.read())
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "sito", "articoli", "prova-pubblicazione-da-hermes.html")))
        with open(os.path.join(self.tmp, "sito", "articoli", "index.html"), encoding="utf-8") as fh:
            self.assertIn('data-tema="finanza"', fh.read())
        # i dossier esistenti devono continuare a compilare (nessun KeyError inchiesta)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "sito", "inchieste", "case-vuote-sudmilano.html")))


if __name__ == "__main__":
    unittest.main()