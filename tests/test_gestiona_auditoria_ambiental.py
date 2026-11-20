"""Proves sense xarxa per al registre de revisió ambiental."""
from __future__ import annotations
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from gestiona_auditoria_ambiental import (
    keywords, official_url, load_decisions, unique, make_plan
)


class AuditoriaAmbientalTests(unittest.TestCase):
    def test_prioritat_no_es_pertinencia(self):
        self.assertGreater(keywords("Canvi climàtic i emissions")[0], 0)
        self.assertEqual(keywords("matèria completament aliena")[0], 0)
        self.assertEqual(keywords("tragua")[0], 0)

    def test_només_font_parlamentaria_o_normativa(self):
        self.assertTrue(official_url("https://www.congreso.es/es/busqueda-de-iniciativas"))
        self.assertTrue(official_url("https://www.boe.es/"))
        self.assertFalse(official_url("https://congreso.es.example.com"))
        self.assertFalse(official_url("http://www.congreso.es/"))

    def test_duplicat_individual_rebutjat(self):
        with self.assertRaisesRegex(ValueError, "duplicat"):
            unique([{"expedient": "161/000001"}, {"expedient": "161/000001"}],
                   "expedient", "prova")

    def test_registre_complet_i_control_negatius(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            ids = [f"161/{i:06d}" for i in range(1, 5095)]
            with (work / "univers_congres_xv_5094.csv").open("w", encoding="utf-8",
                                                             newline="") as f:
                writer = csv.DictWriter(f, ["id", "serie", "titol_oficial",
                                             "autor_oficial", "resultat_oficial",
                                             "url_expedient"])
                writer.writeheader()
                for i, code in enumerate(ids):
                    writer.writerow({"id": code, "serie": "161",
                                     "titol_oficial": ("Biodiversitat i clima" if i == 830
                                                       else f"Proposta {i}"),
                                     "autor_oficial": "Grup de prova",
                                     "resultat_oficial": "Caducat",
                                     "url_expedient": "https://www.congreso.es/"})
            with (work / "inventari_ambient_xv_830.csv").open("w", encoding="utf-8",
                                                             newline="") as f:
                writer = csv.DictWriter(f, ["expedient", "titol_index",
                                             "incidencia", "text_BOCG_localitzat"])
                writer.writeheader()
                for code in ids[:830]:
                    writer.writerow({"expedient": code, "titol_index": "Revisió general",
                                     "incidencia": "", "text_BOCG_localitzat": "SI"})
            cols = ["expedient", "decisio_ambiental", "grau_revision",
                    "instrument", "subtemes", "mesures_identificades",
                    "observacions", "font_text_inicial",
                    "font_resultat_o_tramit", "data_auditoria"]
            with (work / "auditoria_mediambient_lot01.csv").open(
                    "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, cols, delimiter=";")
                writer.writeheader()
                writer.writerow({
                    "expedient": "161/000001", "decisio_ambiental": "INCLOURE",
                    "grau_revision": "PARCIAL", "instrument": "PNL",
                    "subtemes": "Clima", "mesures_identificades": "Mesura",
                    "observacions": "Pendent text final",
                    "font_text_inicial": "https://www.congreso.es/",
                    "font_resultat_o_tramit": "https://www.congreso.es/",
                    "data_auditoria": "2026-11-20",
                })
            summary = make_plan(work)
            self.assertEqual(summary["univers"], 5094)
            self.assertEqual(summary["cua"], 830)
            self.assertEqual(summary["decisions_amb_id"], 1)
            self.assertEqual(summary["inclusions_documentades"], 1)
            self.assertEqual(summary["pendents_cua"], 829)
            self.assertEqual(summary["lots_pendents"], 21)
            self.assertGreater(summary["controls_omissions_seleccionats"], 0)
            with (work / "registre_auditoria_ambient_xv.csv").open(
                    encoding="utf-8-sig", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(rows[0]["decisio_ambiental"], "INCLOURE")
            self.assertEqual(sum(x["decisio_ambiental"] == "PENDENT" for x in rows), 829)
            with (work / "control_omissions_ambient_xv.csv").open(
                    encoding="utf-8-sig", newline="") as f:
                control = list(csv.DictReader(f))
            self.assertTrue(all(x["estat"].startswith("PENDENT") for x in control))
            self.assertTrue(any(x["expedient"] == "161/000831" for x in control))


if __name__ == "__main__":
    unittest.main()
