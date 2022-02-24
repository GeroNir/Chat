import threading
import socket
import time

import Packet

HOST = "127.0.0.1"
PORT = 5002


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

    def accept_clients(self):
        print("Waiting for clients...")
        while True:
            client_socket, address = self.server_socket.accept()
            data = client_socket.recv(1024)
            print(data.decode())
            self.dict_of_sockets[data.decode()] = client_socket
            self.dict_of_users[data.decode()] = address
            print(self.dict_of_users)
            self.client_count += 1
            print("Client connected: {}".format(address))
            client_socket.send("<connected>".encode())
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address, data.decode()))
            client_thread.start()

    def handle_client(self, client_socket, address, user):
        while True:
            try:
                data = self.dict_of_sockets[user].recv(1024)
                if data.decode() == "<get_users>":
                    self.dict_of_sockets[user].send(str(self.dict_of_users).encode())
                    break
                if data.decode() == "<disconnect>":
                    self.dict_of_sockets[user].send("<disconnected>".encode())
                    print("Client disconnected: {}".format(address))
                    self.dict_of_sockets[user].close()
                    del self.dict_of_sockets[user]
                    self.client_count -= 1
                    break
                #print("data" + data.decode())
                tmp = data.decode()
                tmp = tmp[:10]
                #print("tmp" + tmp)
                if tmp == "<download>":
                    #print("check" + data.decode()[11:-1])
                    self.send_file(self.dict_of_sockets[user], data.decode()[11:-1])
                # print("data" + str(data.decode()))
                dest = str(data.decode()).split(":")[4]
                data = str(data.decode()).split(":")[0] + ":" + str(data.decode()).split(":")[1] + ":" + \
                       str(data.decode()).split(":")[2] + ":" + str(data.decode()).split(":")[3]
                # print(data)
                if data:
                    if dest == "all":
                        for key in self.dict_of_sockets.keys():
                            if key != user:
                                self.dict_of_sockets[key].send(data.encode())
                    else:
                        for client in self.dict_of_sockets.keys():
                            if client == dest:
                                self.dict_of_sockets[client].send(data.encode())
                else:
                    raise Exception("No data received")
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

    def send_file(self, socket, filename):
        socket.send("Sending file...".encode())
        data, len = split(filename)
        count = 0
        socket.send(str(len).encode())
        while count < len and count < 4:
            print("entered")
            #TODO: handle the header
            socket.send(data[count])
            time.sleep(0.1)
            count += 1
        while count < len:
            print("entered2")
            ack = socket.recv(16)
            if ack:
                ack = ack.decode()
                print("ack " + ack)
                print("ack " + str(ack[:3]))
                if ack[:3] == "ACK":
                    #TODO: check num of ACK
                    socket.send(data[count])
                    count += 1
                if ack[:4] == "NACK":
                    ack[4] = int(ack[4])
                    socket.send(data[ack[4]])
                    count += ack[4]

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
def calculate_checksum(data):
    checksum = 0
    for byte in data:
        checksum += byte
    checksum = checksum % 256
    return checksum


def split(path):
    buffer = 16
    list = []
    f = open(path, "rb")
    l = f.read(buffer)
    i = 0
    while l:
        l = str(i).encode() + "~".encode() + str(calculate_checksum(l)).encode() + "~".encode() + l
        print("l", l)
        list.append(l)
        l = f.read(buffer)
        i += 1
    f.close()
    return list, len(list)


if __name__ == '__main__':
    server = Server(HOST, PORT)
    server.accept_clients()
