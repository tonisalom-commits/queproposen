#!/usr/bin/env python3
"""Proves amb dades fictícies: no es confonen amb documents parlamentaris reals."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from scripts.recull_index_congres import candidate, extract, official_url, prepare, record_url


class IndexTest(unittest.TestCase):
    def setUp(self):
        self.raw = {
            "iniciativa0": {
                "id_iniciativa": "161/123456",
                "titulo": "Sobre la protección de los humedales y acuíferos",
                "autor": "Grupo Parlamentario de prueba",
                "resultado_tram": "Retirada",
                "fecha_presentado": "02/02/2024",
            },
            "iniciativa1": {
                "id_iniciativa": "161/123457/0000",
                "titulo": "Sobre la organización interna de un servicio",
                "autor": "Otro grupo ficticio",
            },
            "iniciativa2": {
                "id_iniciativa": "161/123456",
                "titulo": "Sobre la protección de los humedales y acuíferos",
            },
            "conteo": 3,
        }

    def test_extract_dedupe(self):
        items = extract(self.raw)
        self.assertEqual([x["id"] for x in items], ["161/123456", "161/123457"])
        self.assertEqual(items[0]["autor_oficial"], "Grupo Parlamentario de prueba")

    def test_candidates_are_not_evidence(self):
        self.assertTrue(candidate(extract(self.raw)[0]))
        self.assertFalse(candidate(extract(self.raw)[1]))

    def test_url_bound_to_official_domain(self):
        self.assertIn("_iniciativas_tipo=161", official_url("161"))
        self.assertIn("161%2F123456", record_url("161/123456"))
        with self.assertRaises(ValueError):
            official_url("999")

    def test_export_is_staging_not_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = root / "dades_originals.json"
            raw.write_text(json.dumps(self.raw), encoding="utf-8")
            result = prepare([("161", raw)], root / "revisio")
            self.assertEqual(result["expedients_indexats"], 2)
            self.assertEqual(result["candidats_per_titol"], 1)
            self.assertFalse(result["univers_exhaustiu_verificat"])
            self.assertTrue((root / "revisio" / "inventari_index.csv").is_file())
            queued = json.loads((root / "revisio" / "candidats_ambientals.json").read_text())
            self.assertEqual(len(queued), 1)
            self.assertIn("PENDENT", queued[0]["verificacio"])
            self.assertFalse((root / "data" / "iniciatives.json").exists())


if __name__ == "__main__":
    unittest.main()
