import base64
import socket
import sys
from _thread import *
from threading import Thread
from time import sleep

from mysql.connector import connect, Error


class Proxy:
    proxy_id = 0

    def __init__(self, port, max_connections=50, buffer_size=1024):
        self.port = port
        self.max_connections = max_connections
        self.buffer_size = buffer_size

    def start(self):
        threads = []
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Binds Host and Port
            sock.bind(('', self.port))
            sock.listen(self.max_connections)
            print("Socket started successfully")
        except socket.error:
            print(Exception)
            sys.exit(2)
        while True:
            try:
                connection, local_address = sock.accept()  # Accepts incoming connections
                t = Thread(target=self.proxy_thread, args=(connection,))
                t.start()
                threads.append(t)
            except KeyboardInterrupt:
                sock.close()
                for thread in threads:
                    thread.join()

    def proxy_thread(self, connection):
        connection.settimeout(2)
        received_data = self.receive_message(connection)
        if received_data:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # If we receive a CONNECT request
            if "connect" in str(received_data).lower():
                # Connect to port 443
                try:
                    parsed_address, parsed_port = self.connection_string_parser(received_data)
                    # If successful, send 200 code response
                    print("Now connecting to: " + parsed_address + " On port: " + str(parsed_port))
                    client.connect((parsed_address, parsed_port))
                    reply = "HTTP/1.0 200 Connection established\r\n"
                    reply += "Proxy-agent: Pyx\r\n"
                    reply += "\r\n"
                    connection.sendall(reply.encode())
                except socket.error as err:
                    # If the connection could not be established, exit
                    # Should properly handle the exit with http error code here
                    print(err)

                # Indiscriminately forward bytes
                connection.setblocking(False)
                client.setblocking(False)
                while True:
                    try:
                        request = connection.recv(self.buffer_size)
                        parsed_utf = request.decode("ascii", "ignore")

                        if parsed_utf and parsed_utf != "":
                            print(parsed_utf)
                            print(request.decode("utf-8"))
                        else:
                            print(request)
                        print("\n")

                        client.sendall(request)
                    except socket.error as err:

                        pass
                    try:
                        reply = client.recv(self.buffer_size)
                        connection.sendall(reply)
                    except socket.error as err:
                        pass

    def receive_message(self, connection):
        try:
            msg = connection.recv(self.buffer_size)
        except socket.timeout as e:
            err = e.args[0]
            # Handles timout errors, to ensure that the program does not freeze when it does not receive data.
            if err == 'timed out':
                return None

            else:
                print(e)
                return None
        except socket.error as e:
            # Something else happened, handle error, exit, etc.
            print(e)
            sys.exit(1)
        else:
            if len(msg) == 0:
                print('No message received \n')
                return None
            else:
                return msg

    def get_connection_information_from_data(self, received_data: bytes):

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


def mysql_connection_emulator():
    print("MysQL thread ")
    try:
        with connect(
                host="localhost",
                user="test",
                password="test",
                port=2560
        ) as connection:
            print(connection)
    except Error as e:
        print(e)


if __name__ == "__main__":
    proxy = Proxy(2560)
    t = Thread(target=proxy.start)
    t.start()
    sleep(2)
    start_new_thread(mysql_connection_emulator, ())

    t.join()
