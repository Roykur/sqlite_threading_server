import socket
import threading
import time

FORMAT = 'utf-8'  # decode and encode format
HOST = socket.gethostbyname(socket.gethostname())
PORT = 6869
NUM_OF_BOMBERS = 5  # numbers of client to connect to server
BOMB_COUNT = 50  # number of messages to send
BOMB_FREQ = 0.1  # number of seconds between every reqquest
MESSAGE = "hello server"


def bomb_server(comm_socket):
    for _ in range(BOMB_COUNT):
        comm_socket.send(MESSAGE.encode(FORMAT))
        time.sleep(BOMB_FREQ)
    comm_socket.close()


def rec_messages(comm_socket):
    while True:
        try:
            print(comm_socket.recv(1024).decode(FORMAT))
        except:
            break

# main


for _ in range(NUM_OF_BOMBERS):
    comm_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    comm_socket.connect((HOST, PORT))
    # create bombing thread
    bomber_thread = threading.Thread(target=bomb_server, args=(comm_socket,))
    bomber_thread.start()
    # create receving thread

    bomber_thread = threading.Thread(target=rec_messages, args=(comm_socket,))
    bomber_thread.start()
