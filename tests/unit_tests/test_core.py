from core.utils import camel_case_to_snake_case
import pytest


@pytest.mark.parametrize(
    "string, expected",
    [
        ("CamelCase", "camel_case"),
        ("enumNumberFish", "enum_number_fish"),
        ("UserDAOObject", "user_dao_object"),
        ("addSSLServer", "add_ssl_server"),
        ("SystemD", "system_d"),
        ("AgentSSLOrTLSCertificate", "agent_ssl_or_tls_certificate"),
        ("W", "w"),
        ("w", "w"),
        ("test", "test"),
        ("TEST", "test"),
        ("QwErTASDzxcBD", "qw_er_tas_dzxc_bd"),
    ],
)
def test_camel_case_to_snake_case(string, expected):
    assert camel_case_to_snake_case(string) == expected


@pytest.mark.parametrize(
    "string",
    [
        450,
        3.14,
        {4, 5},
        {"key": "value"},
        None,
        True,
        False,
        [],
        ["qwe", "asd"],
        int,
    ],
)
def test_camel_case_to_snake_case_exc_type(string):
    with pytest.raises(
        TypeError, match=f"Expected an str, got {type(string).__name__} instead"
    ):
        camel_case_to_snake_case(string)


def test_camel_case_to_snake_case_empty_string():
    with pytest.raises(ValueError, match="Expected non-empty string"):
        camel_case_to_snake_case("")
