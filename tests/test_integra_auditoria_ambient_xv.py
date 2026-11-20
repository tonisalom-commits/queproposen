#!/usr/bin/env python3
"""Proves de la capa d'auditoria amb dades sintètiques, sense Internet."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.integra_auditoria_ambient_xv import (
    load_decisions, process, signal_title, official_source,
)


def dump(path, headers, rows, delimiter=","):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        w = csv.DictWriter(stream, fieldnames=headers, delimiter=delimiter)
        w.writeheader()
        w.writerows(rows)


class AuditoriaXvTests(unittest.TestCase):
    def test_fonts_i_pistes(self):
        self.assertTrue(official_source("https://www.congreso.es/public_oficiales/L15/CONG/BOCG/D/"))
        self.assertFalse(official_source("http://www.congreso.es/iniciatives"))
        self.assertFalse(official_source("https://congreso.es.malicious.example/"))
        self.assertIn("zones de baixes emissions",
                      signal_title("Revisión de las Zonas de Bajas Emisiones"))
        self.assertEqual(signal_title("Acceso a la justicia"), [])

    def test_integra_quatre_decisions_i_manté_tots_els_pendents(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            ids = [f"161/{i:06d}" for i in range(1, 5095)]
            queue = []
            univ = []
            outside = []
            for i, code in enumerate(ids):
                title = "Proposición sobre biodiversidad" if i == 900 else "Reforma administrativa"
                entry = {
                    "id": code, "serie": "161", "titol_oficial": title,
                    "autor_oficial": "Grup", "url_expedient": "https://www.congreso.es/iniciativa",
                }
                univ.append(entry)
                if i < 830:
                    queue.append({
                        "expedient": code, "serie": "161", "tipus": "PNL",
                        "titol_index": "Propuesta medioambiental" if i < 10 else title,
                        "autor_index": "Grup", "text_BOCG_localitzat": "SI",
                        "url_expedient": "https://www.congreso.es/iniciativa",
                        "url_primera_publicacio": "https://www.congreso.es/bocg",
                        "decisio_ambiental": "PENDENT",
                    })
                else:
                    outside.append(entry)
            dump(path / "cua_ambient_xv_830_conciliada.csv", list(queue[0]), queue)
            dump(path / "univers_congres_xv_5094.csv", list(univ[0]), univ)
            dump(path / "fora_cua_xv_4264.csv", list(outside[0]), outside)
            audit = []
            for i in range(4):
                audit.append({
                    "expedient": ids[i], "decisio_ambiental": "INCLOURE",
                    "grau_revision": "TEXT_ORIGINAL_I_RESULTAT", "instrument": "PNL",
                    "subtemes": "Biodiversitat", "mesures_identificades": "Mesura contrastada",
                    "font_text_inicial": "https://www.congreso.es/bocg/original",
                    "font_resultat_o_tramit": "https://www.congreso.es/bocg/final",
                    "data_auditoria": "2026-11-20",
                })
            dump(path / "auditoria_mediambient_lot01.csv", list(audit[0]), audit, ";")
            report = process(path)
            self.assertEqual(report["univers"], 5094)
            self.assertEqual(report["cua"], 830)
            self.assertEqual(report["inclusions_identificades"], 4)
            self.assertEqual(report["cua_pendent_de_decisio"], 826)
            self.assertEqual(report["mostra_fora_cua_per_llegir"], 100)
            rows = list(csv.DictReader((path / "inventari_ambient_xv_revisat.csv").open(encoding="utf-8-sig")))
            self.assertEqual(len(rows), 830)
            self.assertTrue(all(x["decisio_auditoria"] == "INCLOURE" for x in rows[:4]))
            self.assertEqual(rows[4]["decisio_auditoria"], "")
            self.assertEqual(rows[4]["decisio_ambiental"], "PENDENT")
            check = list(csv.DictReader((path / "control_omissions_fora_cua_xv.csv").open(encoding="utf-8-sig")))
            self.assertEqual(len(check), 4264)
            self.assertIn("biodiversitat", check[70]["pistes_pel_titol"]
                          if False else next(x["pistes_pel_titol"] for x in check if x["id"] == ids[900]))
            self.assertEqual(len(list(csv.DictReader((path / "cua_lot02_40.csv").open(encoding="utf-8-sig")))), 40)
            self.assertEqual(json.loads((path / "resum_auditoria_ambient_xv.json").read_text())["inclusions_identificades"], 4)

    def test_impedeix_decisions_repetides_i_fonts_no_oficials(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            row = {
                "expedient": "161/000001", "decisio_ambiental": "INCLOURE",
                "grau_revision": "TEXT_ORIGINAL_I_RESULTAT", "instrument": "PNL",
                "subtemes": "Aigua", "mesures_identificades": "Mesures",
                "font_text_inicial": "https://www.congreso.es/BOCG",
                "font_resultat_o_tramit": "https://www.congreso.es/resultat",
                "data_auditoria": "2026-11-20",
            }
            for name in ("auditoria_mediambient_lot01.csv", "auditoria_mediambient_lot02.csv"):
                dump(p / name, list(row), [row], ";")
            with self.assertRaisesRegex(ValueError, "duplicat"):
                load_decisions(p)
            (p / "auditoria_mediambient_lot02.csv").unlink()
            row["font_text_inicial"] = "https://example.com/suposa"
            dump(p / "auditoria_mediambient_lot01.csv", list(row), [row], ";")
            with self.assertRaisesRegex(ValueError, "no oficial"):
                load_decisions(p)


if __name__ == "__main__":
    unittest.main()
