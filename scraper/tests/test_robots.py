import unittest
from unittest.mock import patch, MagicMock
from scraper.src.robots import RobotsChecker

class TestRobots(unittest.TestCase):

    @patch("urllib.robotparser.RobotFileParser")
    def test_allow(self, mock_rp_class):
        mock_rp = MagicMock()
        mock_rp.can_fetch.return_value = True
        mock_rp_class.return_value = mock_rp

        rc = RobotsChecker("TestAgent")
        self.assertTrue(rc.is_url_allowed("http://example.com/allowed"))

    @patch("urllib.robotparser.RobotFileParser")
    def test_disallow(self, mock_rp_class):
        mock_rp = MagicMock()
        mock_rp.can_fetch.return_value = False  # FORCE DISALLOW
        mock_rp_class.return_value = mock_rp

        rc = RobotsChecker("TestAgent")
        self.assertFalse(rc.is_url_allowed("http://example.com/test"))
