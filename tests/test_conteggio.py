"""Il conteggio statico di una sezione deve usare il singolare con un solo articolo.

Il contatore dinamico (assets/app.js) gia' gestisce il singolare via
data-unita-singolare; le due stringhe statiche di build.sezione_index
(badge .archivio-conteggio e span [data-conteggio]) devono concordare.
"""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import build as B  # noqa: E402


def articolo(n, sezione="ai"):
    return {
        "slug": "pezzo-%d" % n,
        "titolo": "Pezzo %d" % n,
        "sommario": "Sommario %d" % n,
        "tema": "Strumenti e agenti",
        "formato": "Prova pratica",
        "data": "2026-11-19",
        "sezione": sezione,
    }


class ConteggioSezione(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = json.loads((ROOT / "content" / "site.json").read_text(encoding="utf-8"))
        cls.sez = [s for s in cls.site["sezioni"] if s["id"] == "ai"][0]

    def indice(self, quanti):
        articoli = [articolo(i) for i in range(quanti)]
        return B.sezione_index(self.site, self.sez, articoli, {})

    def test_un_articolo_usa_il_singolare(self):
        html = self.indice(1)
        self.assertIn('archivio-conteggio">1 articolo<', html)
        self.assertIn('data-conteggio aria-live="polite">1 articolo<', html)
        self.assertNotIn("1 articoli", html)

    def test_piu_articoli_restano_plurale(self):
        html = self.indice(3)
        self.assertIn('archivio-conteggio">3 articoli<', html)
        self.assertIn('data-conteggio aria-live="polite">3 articoli<', html)

    def test_sezione_vuota_resta_plurale(self):
        html = self.indice(0)
        self.assertIn('archivio-conteggio">0 articoli<', html)

    def test_home_con_un_articolo_usa_il_singolare(self):
        inchieste = json.loads((ROOT / "content" / "inchieste.json").read_text(encoding="utf-8"))["inchieste"]
        atlante = json.loads((ROOT / "content" / "atlante.json").read_text(encoding="utf-8"))
        articoli = [articolo(0, "ai")] + [articolo(i, "finanza") for i in range(3)]
        html = B.home(self.site, inchieste, articoli, atlante)
        self.assertIn('sezione-conteggio">1 articolo<', html)
        self.assertIn('sezione-conteggio">3 articoli<', html)
        self.assertIn('sezione-conteggio">%d inchieste<' % len(inchieste), html)
        self.assertNotIn("1 articoli", html)

    def test_home_con_un_inchiesta_usa_il_singolare(self):
        inchieste = json.loads((ROOT / "content" / "inchieste.json").read_text(encoding="utf-8"))["inchieste"][:1]
        atlante = json.loads((ROOT / "content" / "atlante.json").read_text(encoding="utf-8"))
        html = B.home(self.site, inchieste, [articolo(0, "ai")], atlante)
        self.assertIn('sezione-conteggio">1 inchiesta<', html)
        self.assertIn('sezione-conteggio">1 articolo<', html)


if __name__ == "__main__":
    unittest.main()
