from ipaddress import IPv4Address
import json
import os

from ipinfo.cache.default import DefaultCache
from ipinfo.details import Details
from ipinfo.handler import Handler
from ipinfo import handler_utils
import ipinfo
import pytest


def test_init():
    token = "mytesttoken"
    handler = Handler(token)
    assert handler.access_token == token
    assert isinstance(handler.cache, DefaultCache)
    assert "US" in handler.countries


def test_headers():
    token = "mytesttoken"
    handler = Handler(token)
    headers = handler_utils.get_headers(token)

    assert "user-agent" in headers
    assert "accept" in headers
    assert "authorization" in headers


def test_get_details():
    token = os.environ.get("IPINFO_TOKEN", "")
    handler = Handler(token)
    details = handler.getDetails("8.8.8.8")
    assert isinstance(details, Details)
    assert details.ip == "8.8.8.8"
    assert details.hostname == "dns.google"
    assert details.city == "Mountain View"
    assert details.region == "California"
    assert details.country == "US"
    assert details.country_name == "United States"
    assert details.isEU == False
    assert details.loc == "37.4056,-122.0775"
    assert details.latitude == "37.4056"
    assert details.longitude == "-122.0775"
    assert details.postal == "94043"
    assert details.timezone == "America/Los_Angeles"
    if token:
        asn = details.asn
        assert asn["asn"] == "AS15169"
        assert asn["name"] == "Google LLC"
        assert asn["domain"] == "google.com"
        assert asn["route"] == "8.8.8.0/24"
        assert asn["type"] == "business"

        company = details.company
        assert company["name"] == "Google LLC"
        assert company["domain"] == "google.com"
        assert company["type"] == "business"

        privacy = details.privacy
        assert privacy["vpn"] == False
        assert privacy["proxy"] == False
        assert privacy["tor"] == False
        assert privacy["relay"] == False
        assert privacy["hosting"] == False
        assert privacy["service"] == ""

        abuse = details.abuse
        assert (
            abuse["address"]
            == "US, CA, Mountain View, 1600 Amphitheatre Parkway, 94043"
        )
        assert abuse["country"] == "US"
        assert abuse["email"] == "network-abuse@google.com"
        assert abuse["name"] == "Abuse"
        assert abuse["network"] == "8.8.8.0/24"
        assert abuse["phone"] == "+1-650-253-0000"

        domains = details.domains
        assert domains["ip"] == "8.8.8.8"
        # NOTE: actual number changes too much
        assert "total" in domains
        assert len(domains["domains"]) == 5


#############
# BATCH TESTS
#############

_batch_ip_addrs = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]


def _prepare_batch_test():
    """Helper for preparing batch test cases."""
    token = os.environ.get("IPINFO_TOKEN", "")
    if not token:
        pytest.skip("token required for batch tests")
    handler = Handler(token)
    return handler, token, _batch_ip_addrs


def _check_batch_details(ips, details, token):
    """Helper for batch tests."""
    for ip in ips:
        assert ip in details
        d = details[ip]
        assert d["ip"] == ip
        assert "country" in d
        assert "country_name" in d
        if token:
            assert "asn" in d
            assert "company" in d
            assert "privacy" in d
            assert "abuse" in d
            assert "domains" in d


@pytest.mark.parametrize("batch_size", [None, 1, 2, 3])
def test_get_batch_details(batch_size):
    handler, token, ips = _prepare_batch_test()
    details = handler.getBatchDetails(ips, batch_size=batch_size)
    _check_batch_details(ips, details, token)


@pytest.mark.parametrize("batch_size", [1, 2])
def test_get_batch_details_total_timeout(batch_size):
    handler, token, ips = _prepare_batch_test()
    with pytest.raises(ipinfo.exceptions.TimeoutExceededError):
        handler.getBatchDetails(
            ips, batch_size=batch_size, timeout_total=0.001
        )


#############
# MAP TESTS
#############


def test_get_map():
    handler = Handler()
    mapUrl = handler.getMap(open("tests/map-ips.txt").read().splitlines())
    print(f"got URL={mapUrl}")
