import unittest
from doctor_lives.tower_web import scene,_HTML,BrowserExpressionSink
from doctor_lives.speech_emission import SpeechEmissionUncertain,digest

class TowerWebTests(unittest.TestCase):
    def test_only_first_person_scene_exposed(self):
        self.assertEqual(scene({"narrative":["I am in my kitchen.","I can see the hearth."],
                                "busy":False,"deceased":False,"secret":123}),
            {"narrative":["I am in my kitchen.","I can see the hearth."],"occupied":False,"deceased":False})
        with self.assertRaises(PermissionError):
            scene({"narrative":["world coordinates: 2,4"],"busy":False,"deceased":False})
        self.assertIn("localService",_HTML)
        self.assertIn("Review the transcript before sending",_HTML)

    def test_browser_expression_ack_requires_successful_exact_write(self):
        writes=[]
        sink=BrowserExpressionSink(lambda status, payload: writes.append((status,payload)))
        ack=sink("I have finished my tea.","turn-one")
        self.assertEqual(writes,[(200,{"text":"I have finished my tea.",
                                      "host_write_acknowledged":True,"audible":False})])
        self.assertEqual(ack.delivery_key,"turn-one")
        self.assertEqual(ack.sink_id,"tower-loopback-http")
        self.assertEqual(ack.content_sha256,digest("I have finished my tea."))
        with self.assertRaises(SpeechEmissionUncertain):
            sink("I have finished my tea.","turn-one")
        self.assertEqual(len(writes),1)

    def test_uncertain_browser_write_is_not_acknowledged_or_retried(self):
        def broken(*args):
            raise BrokenPipeError("connection interrupted")
        sink=BrowserExpressionSink(broken)
        with self.assertRaises(BrokenPipeError):
            sink("My reply.","turn-two")
        self.assertTrue(sink.attempted)
        with self.assertRaises(SpeechEmissionUncertain):
            sink("My reply.","turn-two")
