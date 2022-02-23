import socket
from datetime import datetime
from colorama import Fore, init, Back
import random
# init colors
import Server

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
        # connect to the server
        self.sock.connect((HOST, PORT))
        print("[+] Connected.")
        self.client_color = random.choice(colors)
        self.username = input("Enter your username: ")
        self.sock.send(self.username.encode())
        #TODO: duplicate username check

    def send_message(self):
        while True:
            # input message we want to send to the server
            dest = input()
            message = input()
            # a way to exit the program
            if message.lower() == 'q':
                break
            # add the datetime, name & the color of the sender
            date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"{self.client_color}[{date_now}] {self.username}{saprate}{message}{Fore.RESET}{saprate}{dest}"
            self.sock.sendto(message.encode(), (HOST, PORT))
            print("message sent")

if __name__ == '__main__':

    client = Client()
    print("after adding")
    client.send_message()
