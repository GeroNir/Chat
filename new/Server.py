import threading
import socket
HOST = "127.0.0.1"
PORT = 5002



class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.dict_of_sockets = {}
        self.client_count = 0
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
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address, data.decode()))
            client_thread.start()

    def handle_client(self, client_socket, address, user):
        while True:
            #try:
                data = self.dict_of_sockets[user].recv(1024)
                print("data" + str(data.decode()))
                dest = str(data.decode()).split(":")[4]
                data = str(data.decode()).split(":")[0] + ":" + str(data.decode()).split(":")[1] + ":" + str(data.decode()).split(":")[2] + ":" + str(data.decode()).split(":")[3]
                print(data)
                if data:
                    for client in self.dict_of_sockets.keys():
                        if client == dest:
                            self.dict_of_sockets[client].send(data.encode())
                else:
                    raise Exception("No data received")
            # except Exception as e:
            #     print("Client disconnected: {}".format(address))
            #     self.dict_of_sockets[user].close()
            #     del self.dict_of_sockets[user]
            #     self.client_count -= 1
            #     break


    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def get_dict_of_users(self):
        return self.dict_of_users

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

if __name__ == '__main__':

    server = Server(HOST, PORT)
    print(server)
    server.accept_clients()
    print("Server started")