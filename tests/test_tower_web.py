import unittest
from doctor_lives.tower_web import scene,_HTML

class TowerWebTests(unittest.TestCase):
    def test_only_first_person_scene_exposed(self):
        self.assertEqual(scene({"narrative":["I am in my kitchen.","I can see the hearth."],
                                "busy":False,"deceased":False,"secret":123}),
            {"narrative":["I am in my kitchen.","I can see the hearth."],"occupied":False,"deceased":False})
        with self.assertRaises(PermissionError):
            scene({"narrative":["world coordinates: 2,4"],"busy":False,"deceased":False})
        self.assertIn("localService",_HTML)
        self.assertIn("Review the transcript before sending",_HTML)
