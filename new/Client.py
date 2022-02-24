import socket
import time
from datetime import datetime
from colorama import Fore, init, Back
import random
import threading

# from Packet import Packet

HOST = "127.0.0.1"
PORT = 5002
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
        self.username = input("Please enter your username..")
        self.sock.send(self.username.encode())
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        t = threading.Thread(target=self.listen_for_messages)
        t.daemon = True
        t.start()

        # TODO: duplicate username check
        # TODO: add a way to exit the chat

    def send_message(self):
        while True:
            # input message we want to send to the server
            command = input()
            if command == "<get_users>" or command == "<disconnect>" or command == "<get_list_file>":
                self.sock.send(command.encode())
                if command == "<disconnect>":
                    exit()
            else:
                if command[:10] == "<download>":
                    print("[*] Sending file...")
                    self.udpSocket.sendto(command.encode(), (HOST, PORT))
                else:
                    message = input()
                    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    message = f"{self.client_color}[{date_now}] {self.username}{saprate}{message}{Fore.RESET}{saprate}{command}"
                    self.sock.send(message.encode())

    def listen_for_messages(self):
        while True:
            message = self.sock.recv(1024).decode()
            if message == "Sending file...":
                #t = threading.Thread(target=self.get_file())
                #t.daemon = True
                #t.start()
                #time.sleep(1)
                self.get_file()
            else:
                if message:
                    print(message)

    def get_file(self):
        len = int(self.udpSocket.recvfrom(1024)[0])
        expectedData = []
        receivedData = []
        count = 0
        print("Receiving file...")
        print("len: ", len)
        for i in range(len):
            expectedData.append(i)
        print("expectedData: ", expectedData)
        while count < len:
            data = self.udpSocket.recvfrom(32)[0]
            if data:
                data = data.decode()
                print("data" + data)
                data = data.split("~")
                seq = data[0]
                seq = int(seq)
                checksum = int(data[1])
                info = data[2]
                check = self.calculate_checksum(info.encode())
                #TODO: use deffrent thread to sending and receiving
                if check == checksum and seq in expectedData and seq not in receivedData and seq == count:
                    receivedData.append(info)
                    expectedData.remove(seq)
                    self.udpSocket.sendto(("ACK" + str(count)).encode(), (HOST, PORT))
                    count += 1
                    time.sleep(0.1)
                else:
                    self.udpSocket.sendto(("NACK" + str(count)).encode(), (HOST, PORT))
                    time.sleep(0.1)

        print("end")
        for d in receivedData:
            file = open("received_file.txt", "a")
            file.write(d)
            file.close()

    def calculate_checksum(self, data):
        checksum = 0
        for byte in data:
            checksum += byte
        checksum = checksum % 256
        return checksum

if __name__ == '__main__':
    c1 = Client()
    c1.send_message()
