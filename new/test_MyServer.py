import threading
import time
from unittest import TestCase

from new.Client import Client
from new.MyServer import MyServer


class TestMyServer(TestCase):
    def test_MyServer(self):
        global c1
        time.sleep(0.2)
        c1 = Client()
        c1.listen_for_messages()

    def test_accept_clients(self):
        self.fail()

    def test_handle_udp(self):

        HOST = '127.0.0.1'
        PORT = 5002
        s = MyServer(HOST, PORT)
        s.accept_clients()
        c1 = Client()
        c1.listen_for_messages()
        data = c1.sock.recv(1024).decode()
        self.assertEqual(data, 'username accepted')


    def test_handle_client(self):

        t = threading.Thread(target=self.test_MyServer())
        t.daemon = True
        t.start()
        HOST = "127.0.0.1"
        PORT = 5002
        s = MyServer(HOST, PORT)
        s.accept_clients()
        data = c1.sock.recv(1024).decode()
        self.assertEqual(data, 'username accepted')

    def test_get_host(self):
        self.fail()

    def test_get_port(self):
        self.fail()

    def test_get_dict_of_users(self):
        self.fail()

    def test_send_file(self):
        self.fail()

    def test_get_list_of_files(self):
        self.fail()

    def test_split(self):

        HOST = '127.0.0.1'
        PORT = 5000
        path = 'files/test.txt'
        s = MyServer(HOST, PORT)
        ans = s.split(path, 1)
        print(ans)
        self.assertEqual(s.split(path, 1)[0], ['a', 'b', 'c', 'd'])
