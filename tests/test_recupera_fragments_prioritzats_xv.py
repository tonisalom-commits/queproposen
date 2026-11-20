import unittest
from scripts.recupera_fragments_prioritzats_xv import snippet, find_bulletin, possible_dispositive


class FragmentsPrioritzatsTests(unittest.TestCase):
    def test_passatge_no_es_dispositiu_validat(self):
        text = (
            "Índice 161/000269 asunto inicial "
            "sección 161/000269 Se insta al Gobierno a mejorar la eficiencia"
            " energética en los edificios. Fin de la proposición."
        )
        fragment, n = snippet(text, "161/000269")
        self.assertEqual(n, 2)
        self.assertIn("eficiencia", fragment)
        self.assertNotIn("Índice", fragment)

    def test_locates_dispositive_beyond_first_four_thousand_characters(self):
        text = ("161/000473 " + "justificació general " * 310 +
                "El Congreso de los Diputados insta al Gobierno a: "
                "1. Revisar la planificación eléctrica para integrar renovables. "
                "2. Coordinar los operadores de la red. " +
                "161/000474 un altre expedient")
        marker, window = possible_dispositive(text, "161/000473")
        self.assertEqual(marker, "CONGRES_INSTA")
        self.assertIn("integrar renovables", window)
        self.assertNotIn("161/000474", window)

    def test_does_not_infer_dispositive_from_title(self):
        marker, window = possible_dispositive(
            "161/000533 Proposición no de Ley sobre energía.", "161/000533")
        self.assertEqual((marker, window), ("", ""))

    def test_busca_font_oficial(self):
        page = {
            "url": "https://www.congreso.es/es/busqueda-de-iniciativas",
            "links": [
                ("https://untrusted.example/BOCG-15-D-114", "texto íntegro"),
                ("/busqueda-de-publicaciones?_publicaciones_id_texto=(BOCG-15-D-114.CODI.)",
                 "texto íntegro"),
            ],
        }
        result = find_bulletin(page)
        self.assertTrue(result.startswith("https://www.congreso.es/"))
        self.assertIn("BOCG-15-D-114", result)

    def test_no_deixa_sortir_de_domini(self):
        page = {
            "url": "https://www.congreso.es/es/iniciativa",
            "links": [("https://evil.example/BOCG-15-D-114", "texto íntegro")],
        }
        self.assertIsNone(find_bulletin(page))


if __name__ == "__main__":
    unittest.main()
