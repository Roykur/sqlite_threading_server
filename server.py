import socket
from pathlib import Path
import threading
import sqlite3
import time
from queue import Queue

request_queue = Queue()
stored_requests_queue = Queue()
queue_counter = 0  # counter of how many nodes were written to db


db_path = Path('requests.db')  # requests database path

is_stop = False
FORMAT = 'utf-8'  # decode and encode format
HOST = socket.gethostbyname(socket.gethostname())
PORT = 6869


# create requests database
def create_db():
    conn = sqlite3.connect(db_path)
    curr = conn.cursor()

    curr.execute("CREATE TABLE requests (req_time text, client_id text, message text)")

    conn.commit()
    conn.close()


def stop_prog():
    global is_stop
    while True:
        if input() == 'stop':
            is_stop = True


# print the request
def print_requests():
    conn = sqlite3.connect(db_path)
    curr = conn.cursor()
    curr.execute("SELECT * FROM requests")
    requests = curr.fetchall()
    for req in requests:
        print(f"{req}\n")
    conn.commit()
    conn.close()


# write a new request to database
def append_to_db():
    global request_queue
    global stored_requests_queue
    count = 0
    conn = sqlite3.connect(db_path)
    curr = conn.cursor()
    while True:
        if 0 < request_queue.qsize():
            temp_req = request_queue.get()
            if temp_req is not None:
                count += 1
                curr.execute("INSERT INTO requests VALUES(?, ?, ?)", (temp_req[0], temp_req[1], temp_req[2]))
                conn.commit()
                stored_requests_queue.put(temp_req)
                time.sleep(0.05)  # to not write to fast
            if is_stop:
                break

    conn.commit()
    conn.close()


# handle single client
def handle_client(client_socket, client_id):
    global request_queue
    while True and not is_stop:
        try:
            message = client_socket.recv(1024).decode(FORMAT)
            request_time = time.ctime()
            if message != "":  # if message is not empty string:
                print(message)
                request_queue.put((request_time, client_id[0], message, client_socket))
                print(f"received a message from {client_id}: {message}")
        except:
            print(f"connection with {client_id} is lost\n")
            time.sleep(3)  #time to for send_ack() to send acknowledgment
            client_socket.close()
            print(f"current connections:{threading.activeCount() - 2}\n")
            break
    # if server stopped
    time.sleep(3)  # time to for send_ack() to send acknowledgment
    client_socket.close()


def send_ack():
    while True:
            temp_req = stored_requests_queue.get()
            temp_socket = temp_req[3]
            temp_message = temp_req[2]
            temp_socket.send(f"{temp_message}.ACK".encode(FORMAT))


# main

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print('starting server...')

# create database
if not db_path.is_file():
    create_db()

print_requests()

# thread for writing data to db
db_thread = threading.Thread(target=append_to_db)
db_thread.start()

# thread to check if user wants to stop program
stop_thread = threading.Thread(target=stop_prog)
stop_thread.start()

# send validation to client for every request that was stored in db
ack_thread = threading.Thread(target=send_ack)
ack_thread.start()

# get new connections
while True and not is_stop:
    client_socket, client_id = server.accept()

    # thread for getting request for each client
    thread = threading.Thread(target=handle_client, args=(client_socket, client_id))
    thread.start()
    print(f"current connections:{threading.activeCount()-1}\n")

print_requests()

