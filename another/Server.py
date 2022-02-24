import select
import socket
from threading import Thread

# server's IP address
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5002 # port we want to use
list_of_users = {}
separator_token = "<SEP>" # we will use this to separate the client name & message
# initialize list/set of all connected client's sockets
client_sockets = set()
# create a TCP socket
s = socket.socket()
# make the port as reusable port
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind the socket to the address we specified
s.bind((SERVER_HOST, SERVER_PORT))
# listen for upcoming connections
s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

def get_client_sockets():
    """
    This function returns the list of all connected client's sockets
    """
    return client_sockets

def listen_for_client(cs):
    """
    This function keep listening for a message from `cs` socket
    Whenever a message is received, broadcast it to all other connected clients
    """
    while True:
        try:
            # keep listening for a message from `cs` socket
            msg = cs.recv(1024).decode()
        except Exception as e:
            # client no longer connected
            # remove it from the set
            print(f"[!] Error: {e}")
            client_sockets.remove(cs)
        else:
            # if we received a message, replace the <SEP>
            # token with ": " for nice printing
            msg = msg.replace(separator_token, ": ")
            print(msg)
            str_msg = str(msg).split(": ")
            print(str_msg[0])
            str_msg2 = str(str_msg[0]) + ": " + str(str_msg[1])
            detail = str(msg).split("] ")
            print("detail" + detail[1])
            print("detail" + str(detail[1]))
            user_name = detail[1].split(": ")[0]
            send_to = detail[1].split(": ")[2]
            print("user_name" + str(user_name))
            print("send_to" + str(send_to))
            str_msg2 = str_msg2.replace(send_to + " ", "")
            print("str_msg2 " + str(str_msg2))
            list_of_users[user_name] = cs.getpeername()
            dest = list_of_users[send_to]
        # iterate over all connected sockets
        for client_socket in client_sockets:
            # and send the message
            print(client_sockets)
            print("dest" + str(dest))
            peer = client_socket.getpeername()
            print("peer: " + str(peer))
            if peer[1] == dest[1] and peer[0] == dest[0]:
                client_socket.send(str_msg2.encode())

while True:
    # we keep listening for new connections all the time
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected.")
    # add the new connected client to connected sockets
    client_sockets.add(client_socket)
    print(client_sockets)
    # start a new thread that listens for each client's messages
    t = Thread(target=listen_for_client, args=(client_socket,))
    # make the thread daemon so it ends whenever the main thread ends
    t.daemon = True
    # start the thread
    t.start()

# close client sockets
for cs in client_sockets:
    cs.close()
# close server socket
s.close()