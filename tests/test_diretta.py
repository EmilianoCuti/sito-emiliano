"""Test della sezione "News in diretta" (post dei cron finanza) in Finanza.

Esegui:  python -m unittest discover -s tests -v
Il parser/importer usa fixture temporanee; il test di build copia il progetto
in una cartella temporanea e scrive solo lì (--out / sito/).
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


class TestParser(unittest.TestCase):
    def test_parse_campi(self):
        import add_diretta as D
        v = D.parse_post(POST_ESEMPIO, data="2026-11-19", ora="18:00")
        self.assertEqual(v["data"], "2026-11-19")
        self.assertEqual(v["ora"], "18:00")
        self.assertEqual(v["finestra"], "14:00-18:00")
        self.assertEqual(len(v["voci"]), 2)
        self.assertEqual(v["voci"][0]["ora"], "15:30")
        self.assertEqual(v["voci"][0]["fonte"], "Guardian Tech")
        self.assertIn("1.500 miliardi", v["voci"][0]["testo"])
        self.assertNotIn("(15:30", v["voci"][0]["testo"])
        self.assertIn("Anthropic esordisce", v["sintesi"])
        self.assertIn("prima seduta", v["prospettiva"])
        self.assertEqual(v["fonti"], ["Guardian Tech", "Bloomberg Markets"])
        self.assertEqual(v["slug"], "2026-11-19-1800")

    def test_parse_senza_orario_filename(self):
        import add_diretta as D
        v = D.parse_post(POST_ESEMPIO)
        self.assertEqual(v["ora"], "18:00")
        self.assertEqual(v["data"], "2026-11-19")

    def test_nome_file(self):
        import add_diretta as D
        self.assertEqual(D.da_nome_file("fb_post_2026-11-19_1800.txt"),
                         ("2026-11-19", "18:00"))
        self.assertIsNone(D.da_nome_file("fb_post_text_backup_pre18_20261119.txt"))


class TestUnione(unittest.TestCase):
    def test_dedup_per_data_ora(self):
        import add_diretta as D
        a = D.parse_post(POST_ESEMPIO, data="2026-11-19", ora="18:00")
        b = D.parse_post(POST_ESEMPIO, data="2026-11-19", ora="18:00")
        c = D.parse_post(POST_ESEMPIO, data="2026-11-19", ora="14:00")
        out = D.unisci([], a)
        out = D.unisci(out, b)  # stessa edizione: non duplica
        out = D.unisci(out, c)
        self.assertEqual(len(out), 2)
        # ordinamento: più recente in testa
        self.assertEqual(out[0]["ora"], "18:00")
        self.assertEqual(out[1]["ora"], "14:00")


class TestRender(unittest.TestCase):
    def test_block_e_index(self):
        import add_diretta as D
        import build as B
        notizie = [D.parse_post(POST_ESEMPIO, data="2026-11-19", ora="18:00")]
        block = B.diretta_block(notizie, "../", limite=6)
        self.assertIn("News in diretta", block)
        self.assertIn("1.500 miliardi", block)
        self.assertIn("diretta.html", block)
        site = B.leggi_json("content/site.json")
        page = B.diretta_index(site, notizie)
        self.assertIn("News in diretta", page)
        self.assertIn("Guardian Tech", page)


class TestBuildFinanza(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="sito-diretta-")
        shutil.copytree(ROOT, self.tmp, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(".git", "sito", "__pycache__", "*.pyc"))
        import add_diretta as D
        notizie = [D.parse_post(POST_ESEMPIO, data="2026-11-19", ora="18:00")]
        with open(os.path.join(self.tmp, "content", "diretta.json"), "w", encoding="utf-8") as fh:
            json.dump({"diretta": notizie}, fh, ensure_ascii=False)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_diretta_in_finanza_non_altrove(self):
        out = os.path.join(self.tmp, "sito")
        r = subprocess.run([sys.executable, os.path.join(self.tmp, "build.py"), "--out", out],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(out, "finanza", "index.html"), encoding="utf-8") as fh:
            fin = fh.read()
        self.assertIn("News in diretta", fin)
        self.assertIn("1.500 miliardi", fin)
        self.assertTrue(os.path.exists(os.path.join(out, "finanza", "diretta.html")))
        for sez in ("ai", "informatica"):
            with open(os.path.join(out, sez, "index.html"), encoding="utf-8") as fh:
                self.assertNotIn("News in diretta", fh.read(), sez)


class TestBuildVuoto(unittest.TestCase):
    """Condizione reale iniziale: nessuna edizione, sezione preparata ma vuota."""

    def test_sezione_preparata_vuota(self):
        out = tempfile.mkdtemp(prefix="sito-diretta-vuoto-")
        try:
            r = subprocess.run([sys.executable, os.path.join(ROOT, "build.py"), "--out", out],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(os.path.join(out, "finanza", "index.html"), encoding="utf-8") as fh:
                fin = fh.read()
            self.assertIn("News in diretta", fin)
            self.assertIn("diretta-vuoto", fin)
            self.assertTrue(os.path.exists(os.path.join(out, "finanza", "diretta.html")))
            for sez in ("ai", "informatica"):
                with open(os.path.join(out, sez, "index.html"), encoding="utf-8") as fh:
                    self.assertNotIn("News in diretta", fh.read(), sez)
        finally:
            shutil.rmtree(out, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
