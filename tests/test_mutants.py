import pytest
import unittest
import mock
from ipinfo import Handler
from ipinfo.exceptions import RequestQuotaExceededError
from ipinfo.handler_utils import get_headers, CACHE_TTL


class Test_Mutants(unittest.TestCase):
    def setUp(self):
        self.token = "mytesttoken"

    def test_init_mutant1(self):
        dictMock = {"request_options": {"test": 1}}
        handler = Handler(self.token, **dictMock)
        self.assertEqual(handler.request_options["timeout"], 2)

    @mock.patch('requests.get')
    def test_get_details_mutant2(self, mock_requests):
        handler = Handler(self.token)
        mock_requests.return_value.status_code = 429
        with pytest.raises(RequestQuotaExceededError):
            handler.getDetails()

    def test_cache_ttl_mutant3(self):
        expected = 60 * 60 * 24
        self.assertEqual(CACHE_TTL, expected)

    def test_get_headers_mutant4(self):
        expected = 'Bearer ' + self.token
        self.assertEqual(get_headers(self.token)['authorization'], expected)


