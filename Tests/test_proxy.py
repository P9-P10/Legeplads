from Proxy.proxy import Proxy


def test_get_port_and_url_from_received_data_get_request():
    proxy = Proxy(0)
    data = b'GET / HTTP/1.1\r\nHost: localhost:9999\r\n'
    url, port = proxy.connection_string_parser(data)
    assert url == "localhost"
    assert port == 9999

def test_get_port_and_url_from_received_data_connect_request():
    proxy = Proxy(0)
    data = b'CONNECT duckduckgo.com:443 HTTP/1.1\r\nHost: duckduckgo.com:443\r\n\r\n'
    url, port = proxy.connection_string_parser(data)
    assert url == "duckduckgo.com"
    assert port == 443