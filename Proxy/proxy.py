import socket
import sys
from _thread import *
from random import randint
from threading import Thread
from time import sleep
import errno
from mysql.connector import connect, Error


class Proxy:
    proxy_id = 0

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
        except socket.error:
            print(Exception)
            sys.exit(2)

        while True:
            try:
                connection, local_address = sock.accept()  # Accepts incoming connections
                connection.settimeout(2)
                print("Received data from: " + local_address[0])
                received_data = self.receive_message(connection)
                if not received_data:
                    print("Issue has arrised, bummer.")
                    continue
                parsed_address, parsed_port = self.connection_string_parser(received_data)
                start_new_thread(self.proxy_server, (parsed_address, parsed_port, connection, received_data))

            except KeyboardInterrupt:
                sock.close()
                print("\n \n Shutting down \n \n")
                sys.exit(1)

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

    def proxy_server(self, parsed_address, parsed_port, connection, received_data):
        self.proxy_id += 1
        local_id = self.proxy_id
        try:
            print("Id: " + str(local_id) + " Connection attempt started on: " + str(parsed_address) + " : " + str(
                parsed_port))
            proxy_socket = socket.create_connection((parsed_address, parsed_port))
            proxy_socket.send(received_data)
            while True:
                reply = self.receive_message(proxy_socket)
                if reply:
                    connection.send(reply)
                else:
                    break
            proxy_socket.close()
            connection.close()

        except socket.error as current_error:
            connection.close()
            print("Id: " + str(local_id) + " " + str(current_error))
            sys.exit(1)

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
