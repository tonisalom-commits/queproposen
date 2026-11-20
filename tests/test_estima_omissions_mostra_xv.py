#!/usr/bin/env python3
"""Proves dels escenaris de mostreig amb dades sintètiques."""
import unittest
from scripts.estima_omissions_mostra_xv import assess


class MostraOmissionsTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {
            "mida": 3, "marc_mostral": "3 controls a fora de cua", "llavor": 42,
            "estrats": {
                "120": {"poblacio": 10, "seleccionats": 1},
                "161": {"poblacio": 20, "seleccionats": 2},
            },
        }
        self.sample = [
            {"id": "120/000001", "serie": "120",
             "estat_revision": "PENDENT: no hi ha articulat"},
            {"id": "161/000001", "serie": "161",
             "estat_revision": "AUDITAT: INCLOURE"},
            {"id": "161/000002", "serie": "161",
             "estat_revision": "AUDITAT: FRONTERER"},
        ]

    def test_ponderacio_i_incertesa(self):
        x = assess(self.sample, self.manifest)
        self.assertEqual(x["mostra_total"], 3)
        self.assertEqual(x["mostra_revisada"], 2)
        self.assertEqual(x["repartiment"], {
            "incloses": 1, "excloses": 0, "frontereres": 1, "pendents": 1,
        })
        y = x["escenaris_d_expansio_condicional"]
        self.assertEqual(y["si_totes_les_ambigues_i_pendents_fossin_excloses"], 10)
        self.assertEqual(y["si_totes_les_ambigues_i_pendents_fossin_incloses"], 30)
        self.assertFalse(x["estrats"]["120"]["variancia_dins_estrat_estimable"])

    def test_duplicat_fail(self):
        with self.assertRaisesRegex(ValueError, "repetits"):
            assess(self.sample[:1] * 3, self.manifest)

    def test_estrat_incorrecte_fail(self):
        self.sample[1]["serie"] = "162"
        with self.assertRaisesRegex(ValueError, "Estrats discordants"):
            assess(self.sample, self.manifest)


if __name__ == "__main__":
    unittest.main()
