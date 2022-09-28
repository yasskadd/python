import pytest
from mock import patch
from unittest.mock import MagicMock, patch
from ipinfo import Handler
from ipinfo.exceptions import RequestQuotaExceededError



def test_init_mutant1():
    token = "mytesttoken"
    dictMock = {"request_options": {"test": 1}}
    handler = Handler(token, **dictMock)
    assert handler.request_options["timeout"] == 2

def test_getDetails_mutant2():
    token = "mytesttoken"
    handler = Handler(token)
    with patch('requests.get') as mock_request:
        mock_request.return_value.status_code = 429
        with pytest.raises(RequestQuotaExceededError):
            handler.getDetails()



