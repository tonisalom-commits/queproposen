#!/usr/bin/env python3
"""Proves dels senyals de títols, independents de la mostra aleatòria."""
import unittest
from scripts.prioritza_omissions_fora_cua_xv import title_signals, calculate


class PistesForaCuaTests(unittest.TestCase):
    def test_inclou_pistes_omissions_ja_detectades(self):
        self.assertIn("contaminacio_acustica",
                      title_signals("Instalación de barreras acústicas")["pistes_fortes"])
        self.assertIn("energia_i_electrificacio",
                      title_signals("Paralizar la línea de alta tensión")["pistes_fortes"])
        self.assertIn("energia_i_electrificacio",
                      title_signals("Apoyo al vehículo eléctrico")["pistes_fortes"])
        self.assertIn("riscos_i_emergencia",
                      title_signals("Daños por la DANA de Valencia")["pistes_fortes"])

    def test_senyals_indirectes_no_es_devenen_decisions(self):
        a = title_signals("Mejora integral del aeropuerto")
        self.assertEqual(a["pistes_fortes"], [])
        self.assertIn("transport_i_infraestructura", a["pistes_indirectes"])
        self.assertEqual(title_signals("Reforma de la justicia")["prioritat_lectura"], 0)

    def test_particio_amb_exclusions_previament_auditades(self):
        r = [
            {"id": "161/000001", "serie": "161",
             "titol_oficial": "Línea de alta tensión",
             "autor_oficial": "Grupo", "url_expedient": "https://www.congreso.es/"},
            {"id": "161/000002", "serie": "161",
             "titol_oficial": "Aprobación de un servicio de ayuda social",
             "autor_oficial": "Grupo", "url_expedient": "https://www.congreso.es/"},
            {"id": "161/000003", "serie": "161",
             "titol_oficial": "Movilidad eléctrica",
             "autor_oficial": "Grupo", "url_expedient": "https://www.congreso.es/"},
        ]
        all_rows, queue, s = calculate(
            r, {"161/000003": {"decisio_ambiental": "FRONTERER"}},
            max_queue=250,
        )
        self.assertEqual(len(all_rows), 1)
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0]["id"], "161/000001")
        self.assertEqual(s["ja_revisats_fora_cua"], 1)
        self.assertEqual(s["sense_pistes_noves_i_sense_revisar"], 1)
        self.assertEqual(s["suma_verificada"], 3)

    def test_duplicat_falla(self):
        row = {"id": "161/000001", "serie": "161",
               "titol_oficial": "Aigua", "url_expedient": "https://www.congreso.es/"}
        with self.assertRaisesRegex(ValueError, "Duplicats"):
            calculate([row, row], {})


if __name__ == "__main__":
    unittest.main()
