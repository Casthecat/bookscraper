import unittest
from unittest.mock import Mock, patch
from requests.exceptions import RequestException   
from scraper.src.fetcher import fetch_page


class TestFetcher(unittest.TestCase):

    def test_fetch_success(self):
        with patch.object(fetch_page.__globals__['requests'], 'get') as mock_get:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.text = "<html>OK</html>"
            mock_get.return_value = mock_resp

            html = fetch_page("http://example.com", delay_ms=0)
            self.assertEqual(html, "<html>OK</html>")

    def test_fetch_retry_fail(self):
        with patch.object(fetch_page.__globals__['requests'], 'get') as mock_get:
            mock_get.side_effect = RequestException("Network error")

            html = fetch_page("http://example.com", delay_ms=0)
            self.assertIsNone(html)


if __name__ == "__main__":
    unittest.main()
