import socket
import time
from datetime import datetime
from colorama import Fore, init, Back
import random
import threading

HOST = "127.0.0.1"
PORT = 5002
BUFFER_SIZE = 50000
init()

# set the available colors
colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX,
          Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX,
          Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX,
          Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW
          ]

saprate = ":"


class Client:

    def __init__(self):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[*] Connecting to {HOST}:{PORT}...")
        self.sock.connect((HOST, PORT))
        self.client_color = random.choice(colors)
        self.username = input("Please enter your username: ")
        self.sock.send(self.username.encode())
        self.currAddr = None
        recv = self.sock.recv(BUFFER_SIZE).decode()
        #print(recv)
        while recv == "username already taken":
            print("username already taken")
            self.username = input("Please choose another username: ")
            self.sock.send(self.username.encode())
            recv = self.sock.recv(BUFFER_SIZE).decode()
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        t = threading.Thread(target=self.listen_for_messages)
        t.daemon = True
        t.start()

    def send_message(self):

        while True:
            # input message we want to send to the server
            command = input("Enter command: ")
            if command == "<get_users>" or command == "<disconnect>" or command == "<get_files>" or command == "<proceed>" or command[:10] == "<download>":
                self.sock.send(command.encode())
                if command == "<disconnect>":
                    exit()

                if command == "<proceed>":
                    print("[*] proceeding..")
                    self.udpSocket.sendto(command.encode(), self.currAddr)

                if command[:10] == "<download>":
                    print("[*] Sending file...")
                    cmd = command + "~" + self.username
                    self.udpSocket.sendto(cmd.encode(), (HOST, PORT))
            else:
                message = input("Enter message: ")
                date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                message = f"{self.client_color}[{date_now}] {self.username}{saprate}{message}{Fore.RESET}{saprate}{command}"
                self.sock.send(message.encode())

    def listen_for_messages(self):
        while True:
            try:
                message = self.sock.recv(50000).decode()
                if message:
                    if message == "Sending file...":
                        # t = threading.Thread(target=self.get_file())
                        # t.daemon = True
                        # t.start()
                        # time.sleep(1)
                        self.get_file()
                    else:
                        print(message)
            except Exception as e:
                print(e)
                break

    def get_file(self):

        try:
            b = True
            while b:
                size, addr = self.udpSocket.recvfrom(BUFFER_SIZE)
                if len(size.decode().split("~")) == 1:
                    b = False
            self.currAddr = addr
            print(f"[*] File size: {size}")
            size = int(size)
            expectedData = []
            receivedData = []
            count = 0
            print("Receiving file...")
            print("len: ", size)
            for i in range(size):
                expectedData.append(i)
            # print("expectedData: ", expectedData)
            while len(expectedData) > 0:
                data = self.udpSocket.recvfrom(50000)[0]
                if data:
                    # print("data", data)
                    # data = data.decode()
                    # print("data" + data)
                    data = str(data).split("~")
                    seq = data[0]
                    seq = seq[2:]
                    seq = int(seq)
                    checksum = int(data[1])
                    info = data[2]
                    info = info[:-1]
                    check = self.calculate_checksum(info.encode())
                    # TODO: use different thread to sending and receiving
                    if seq in expectedData:
                        #print("seq #", seq)
                        receivedData.insert(seq, info)
                        expectedData.remove(seq)
                        self.udpSocket.sendto(("ACK" + str(seq)).encode(), addr)
                        print("ACK" + str(seq))
                        count += 1
                        if seq == (size / 2):
                            print("50%, waiting for proceed...")
                            b = True
                            while b:

                                cmd = self.sock.recv(1024).decode()
                                if cmd == "<proceeding>":
                                    print("[*] Proceeding...")

                                    b = False
                                else:
                                    if seq in expectedData:
                                        print("seq #", seq)
                                        receivedData.insert(seq, info)
                                        expectedData.remove(seq)
                                        self.udpSocket.sendto(("ACK" + str(seq)).encode(), addr)
                                        print("[*] Sending ACK...", seq)
                        # time.sleep(0.1)
                    else:
                        self.udpSocket.sendto(("NACK" + str(count)).encode(), addr)
                        # time.sleep(0.1)
            print("end")
            self.udpSocket.sendto(("end").encode(), addr)
            for d in receivedData:
                file = open("received_file.txt", "a")
                file.write(d)
                file.close()
        except Exception as e:
            print(e)

    def calculate_checksum(self, data):
        checksum = 0
        for byte in data:
            checksum += byte
        checksum = checksum % 256
        return checksum


if __name__ == '__main__':
    c1 = Client()
    c1.send_message()

# <download><leave.png>
