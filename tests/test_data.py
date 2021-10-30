import unittest

from wpilib_ws import WPILibWsServer


class TestData(unittest.TestCase):
    def setUp(self):
        self.server = WPILibWsServer()

    def test_verify_data(self):
        """
        As per the WPILib protocol, the server should ignore messages that:
        - Are not a dict
        - Have no 'type' key, 'device' key, or 'data' key
        - Have a 'type' or 'device' key that is not a string
        - Have a 'data' value that is not a dict
        - Have a 'type' value that the client or server does not recognize
        """

        cases = [
            ({}, False),
            ({"type": "SimDevice", "device": "bar", "data": {"foo": "bar"}}, True),
            ({"type": 1, "device": "bar", "data": {"foo": "bar"}}, False),
            ({"type": "SimDevice", "data": {"foo": "bar"}}, False),
            ({"type": "SimDevice", "device": "bar", "data": 1}, False),
            ({"type": "NotASimDevice", "device": "bar", "data": {"foo": "bar"}}, False),
            ("not an object", False),
        ]

        for case, expected in cases:
            self.assertEqual(
                self.server.verify_data(case), expected, f"Failed on case: {case}"
            )
