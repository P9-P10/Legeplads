import socket, ssl
import sys
from _thread import *
from random import randint


# Adapted implementation from : https://github.com/anapeksha/python-proxy-server
class Proxy:
    def __init__(self, port, max_connections=10, buffer_size=8192):
        self.port = port
        self.max_connections = max_connections
        self.buffer_size = buffer_size

    def start(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Binds Host and Port
            sock.bind(('', self.port))
            sock.listen(self.max_connections)
            print("Socket started successfully")
        except:
            print(Exception)
            sys.exit(2)

        while True:
            try:
                connection, local_address = sock.accept()  # Accepts incoming connections
                received_data = connection.recv(self.buffer_size)
                parsed_address, parsed_port = self.connection_string_parser(received_data)
                start_new_thread(self.proxy_server, (parsed_address, parsed_port, connection, received_data))

            except KeyboardInterrupt:
                sock.close()
                print("\n \n Shutting down \n \n")
                sys.exit(1)

    def proxy_server(self, parsed_address, parsed_port, connection, received_data):
        test_id = randint(1, 10000)
        try:
            print("Id: " + str(test_id) + " Connection attempt started on: " + str(parsed_address) + " : " + str(
                parsed_port))
            socket_handler = socket.create_connection((parsed_address,parsed_port))
            secure_context = ssl.create_default_context()
            secure_socket = secure_context.wrap_socket(socket_handler, server_hostname=parsed_address)
            #secure_socket.connect((parsed_address, parsed_port))
            secure_socket.send(received_data)
            while True:
                reply = secure_socket.recv(self.buffer_size)
                if reply:
                    connection.send(reply)
                else:
                    break
            secure_socket.close()
            connection.close()

        except socket.error as current_error:
            secure_socket.close()
            connection.close()
            print("Id: " + str(test_id) + str(current_error))
            sys.exit(1)

    def get_connection_information_from_data(self, received_data: bytes):
        print(received_data)
        data_lines = received_data.split(b'\n')
        line_with_url = str(self.get_host_section(data_lines).strip())
        url = line_with_url.split("Host:")[1].strip().replace("'", "")
        return url

    def connection_string_parser(self, received_data):
        url = self.get_connection_information_from_data(received_data)
        if ":" in url:
            print(url)
            address, port = url.split(':')
            port = int(port)

        else:
            address = url
            port = 443
        return address, int(port)

    def get_host_section(self, data_sections: [bytes]):
        for section in data_sections:
            if b'Host' in section:
                return section


if __name__ == "__main__":
    proxy = Proxy(2560)
    proxy.start()
