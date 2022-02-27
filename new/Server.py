import threading
import socket
import time
from os import listdir
from os.path import isfile, join

HOST = "127.0.0.1"
PORT = 5002
BUFFER_SIZE = 50000


# TODO: flow control
# TODO: unit tests
# TODO: duplicate users

class Server:
    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.dict_of_sockets = {}
        self.client_count = 0
        self.list_of_files = []
        self.dict_of_users = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind((self.host, self.port))

    def accept_clients(self):
        print("Waiting for clients...")
        while True:
            client_socket, address = self.server_socket.accept()
            data = client_socket.recv(1024)
            print(data.decode())
            while data.decode() in self.dict_of_sockets.keys():
                print("duplicate user")
                client_socket.send("username already taken".encode())
                data = client_socket.recv(1024)
                print("hey", data.decode())
            print("new user")
            client_socket.send("username accepted".encode())
            self.dict_of_sockets[data.decode()] = client_socket
            self.dict_of_users[data.decode()] = address
            print(self.dict_of_sockets)
            self.client_count += 1
            if self.client_count > 5:
                print("Max number of clients reached")
                client_socket.send("Max number of clients reached".encode())
                client_socket.close()
            else:
                print("Client connected: {}".format(address))
                client_socket.send("<connected>".encode())
                client_thread = threading.Thread(target=self.handle_client, args=(address, data.decode()))
                client_thread.daemon = True
                client_thread.start()
                udp_thread = threading.Thread(target=self.handle_udp, args=(client_socket, data.decode()))
                udp_thread.daemon = True
                udp_thread.start()


    def handle_udp(self, client_socket, username):
        while True:
            try:
                d, addr = self.udpSocket.recvfrom(1024)
                d = d.decode()
                print("d", d)
                if d == "<proceed>":
                    d = None
                    print("None")
                else:
                    d = d.split("~")
                    if len(d) == 2:
                        print("d", d)
                        username = d[1]
                        print("username", username)
                    d = d[0]
                    if d[:10] == "<download>":
                        print("downloading file")
                        # send_thread = threading.Thread(target=self.send_file, args=(client_socket, addr, d[11:-1]))
                        # send_thread.daemon = True
                        # send_thread.start()
                        self.send_file(client_socket, addr, d[11:-1], username)
            except:
                pass
            time.sleep(1)


    def handle_client(self, address, user):
        while True:
            try:
                data = self.dict_of_sockets[user].recv(1024)
                if data:
                    if data.decode() == "<get_users>":
                        self.dict_of_sockets[user].send(str(self.dict_of_users).encode())
                        data = None

                    if data.decode() == "<disconnect>":
                        self.dict_of_sockets[user].send("<disconnected>".encode())
                        print("Client disconnected: {}".format(address))
                        self.dict_of_sockets[user].close()
                        del self.dict_of_sockets[user]
                        self.client_count -= 1
                        data = None
                        break

                    if data.decode() == "<get_files>":
                        self.dict_of_sockets[user].send(str(self.get_list_of_files()).encode())
                        data = None

                    if data.decode()[:10] == "<download>" or data.decode() == "<proceed>":
                        data = None

                # tmp = data.decode()
                # print(tmp)
                # tmp = tmp[:10]

                if data:
                    print("data", data.decode())
                    dest = str(data.decode()).split(":")[4]
                    data = str(data.decode()).split(":")[0] + ":" + str(data.decode()).split(":")[1] + ":" + \
                           str(data.decode()).split(":")[2] + ":" + str(data.decode()).split(":")[3]
                    if dest == "all":
                        for key in self.dict_of_sockets.keys():
                            if key != user:
                                self.dict_of_sockets[key].send(data.encode())
                    else:
                        for client in self.dict_of_sockets.keys():
                            if client == dest:
                                self.dict_of_sockets[client].send(data.encode())

            except Exception as e:
                print("Client disconnected: {}".format(address))
                self.dict_of_sockets[user].close()
                del self.dict_of_sockets[user]
                self.client_count -= 1
                break

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def get_dict_of_users(self):
        return self.dict_of_users

    def send_file(self, socket, addr, filename, user):
        print("user: {}", user)
        print("socket: {}".format(socket))
        self.dict_of_sockets[user].send("Sending file...".encode())
        window_size = 4
        # print("addr", addr)
        data, size = self.split(filename)
        count = 0
        self.udpSocket.sendto(str(size).encode(), addr)
        expectedData = []
        for i in range(size):
            expectedData.append(i)
        self.udpSocket.settimeout(0.2)
        try:
            while count < size and count < window_size:
                self.udpSocket.sendto(data[count], addr)
                # time.sleep(0.1)
                print("sent packet #", count)
                count += 1
            flag = True
            # TODO: saparte thread for receiving acks
            while len(expectedData) > 0 and flag:
                ack = self.udpSocket.recvfrom(32)[0].decode()
                if ack:
                    if ack == "end":
                        flag = False
                if ack:
                    print(ack)
                    if ack[:3] == "ACK":
                        # print("ack in", ack[3])
                        if int(ack[3:]) == size / 2:
                            print("half done, wait for proceeding")
                            b = True
                            while b:
                                try:
                                    proc = self.udpSocket.recvfrom(32)[0].decode()
                                    print(proc, "wait for proceeding")
                                    if proc == "<proceed>":
                                        print("proceeding")
                                        self.dict_of_sockets[user].send("<proceeding>".encode())
                                        for i in range(window_size):
                                            self.udpSocket.sendto(data[count], addr)
                                            count += 1
                                            print("sent packet #", count)
                                        b = False
                                except Exception as e:
                                    pass
                        if int(ack[3:] == str(expectedData[0])):
                            expectedData.remove(int(ack[3:]))
                            if count < size:
                                self.udpSocket.sendto(data[count], addr)
                                print("sent packet #", count)
                                count += 1
                        else:
                            if len(expectedData) > 1:
                                self.udpSocket.sendto(data[expectedData[0]], addr)
                                self.udpSocket.sendto(data[expectedData[1]], addr)
                                expectedData.remove(int(ack[3:]))
                                # print("Sepical sent", str(data[expectedData[0]]))
                                print("Sepical sent #", int(expectedData[0]))
                    if ack[:4] == "NACK":
                        self.udpSocket.sendto(data[int(ack[4:])], addr)
                    # print(expectedData)
            print(filename + " sent")
        except Exception as e:
            print("timeout")
            #print(e)
            self.udpSocket.sendto(data[expectedData[0]], addr)

    def get_list_of_files(self):
        mypath = "files"
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        return onlyfiles

    def check_username(self):
        available = True
        while available:
            user = input("Enter username: ")
            for name in self.dict_of_users:
                if name == user:
                    available = False
                    print("this user name is not available, please try again:")
                    break
            if available == True:
                return user
            available = True
        return None

    def __repr__(self):
        return "Server(host={}, port={})".format(self.host, self.port)

    # <download><text.txt>
    def calculate_checksum(self, data):
        checksum = 0
        for byte in data:
            checksum += byte
        checksum = checksum % 256
        return checksum

    def split(self, path):
        path = "files/" + path
        buffer = BUFFER_SIZE - 100
        list = []
        f = open(path, "rb")
        l = f.read(buffer)
        i = 0
        while l:
            l = str(i).encode() + "~".encode() + str(self.calculate_checksum(l)).encode() + "~".encode() + l
            # print("l", l)
            list.append(l)
            l = f.read(buffer)
            i += 1
        f.close()
        return list, len(list)


if __name__ == '__main__':

    server = Server(HOST, PORT)
    server.accept_clients()
