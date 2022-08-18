import datetime
import os
import socket
import ssl
import sys

import pymongo

CA_CERT_PATH = 'certificate.crt'


def receive_command(connection):
    d1 = connection.recv(1024)
    print("type: " + d1.decode())
    if d1.decode() == 's.m':
        data1 = connection.recv(1024)
        print(f"received message: {data1.decode()}")
    elif d1.decode() == 's.s.m':
        ssl_conn = ssl.wrap_socket(connection, server_side=True,
                                   certfile="certificate.crt", keyfile="private.key",
                                   ssl_version=ssl.PROTOCOL_TLSv1)
        data2 = ssl_conn.read()
        print(f"received message: {data2.decode()}")
        ssl_conn.close()
        sys.exit()
    elif d1.decode() == 'f.m':
        fn = connection.recv(1024)
        file_name = fn.decode()
        sys_file_name = os.path.basename(file_name)
        path = "D:\\lessons\\term6\\shabake\\projects\\project_two\\implementation\\ReceivedFiles"
        with open(path + os.sep + sys_file_name, "wb") as f:
            while True:
                data = connection.recv(1024)
                if "done" in data.decode():
                    break
                f.write(data)
        print(f"{file_name} file received.")
    elif d1.decode() == 'e.m':
        input_command = connection.recv(1024).decode()
        sec = "-e" in input_command
        input_message = ""
        if "\"" in input_command:
            input_message = input_command[input_command.index("\"") + 1: input_command.rindex("\"")]
        input_command = input_command.split()
        send_command(connection, input_command[1], input_message, sec)


def send_command(client_socket, command, message, secret):
    if command == "send" and secret:
        c = command + " -e " + message
    else:
        c = command + " " + message
    data = {"command": c, "ip": client_socket.getpeername()[0], "datetime": datetime.datetime.now()}
    x = collection.insert_one(data)
    print(x)
    if command == "send":
        if not secret:
            client_socket.send('s.m'.encode())
            client_socket.send(message.encode())
            print("sent message:" + message)
        else:
            client_socket.send('s.s.m'.encode())
            ssl_conn = ssl.wrap_socket(client_socket, cert_reqs=ssl.CERT_REQUIRED,
                                       ssl_version=ssl.PROTOCOL_TLSv1, ca_certs=CA_CERT_PATH)
            ssl_conn.write(message.encode())
            print("sent message:" + message)
            ssl_conn.close()
            sys.exit()
    elif command == "upload":
        client_socket.send('f.m'.encode())
        base_name = os.path.basename(message)
        client_socket.send(base_name.encode())
        path = "D:\\lessons\\term6\\shabake\\projects\\project_two\\implementation\\FilesForSend"
        with open(path + os.sep + message, "rb") as f_read:
            while True:
                bytes_read = f_read.read(1024)
                if not bytes_read:
                    client_socket.send("done".encode())
                    break
                client_socket.send(bytes_read)
    elif command == "exec":
        client_socket.send('e.m'.encode())
        print("-------83")
        client_socket.send(message.encode())
        if "history" not in message:
            receive_command(client_socket)
    elif command == "history":
        query = {"ip": client_socket.getpeername()[0]}
        doc = collection.find(query)
        print("commands history : ")
        for record in doc:
            print(record)


if __name__ == '__main__':

    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["CNP2"]
    collection = db["command"]

    role, ip_address = input("command:").split()
    # role = input("command:")
    if role == "connect":

        HOST = ip_address
        # HOST = "127.0.0.11"
        PORT = 23

        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        print(hostname + "--" + ip)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((HOST, PORT))
                print("Connected to remote host")
            except:
                print('Unable to connect')
                sys.exit()
            while True:
                command = input("Command:")
                secret = "-e" in command
                message = ""
                if "\"" in command:
                    message = command[command.index("\"") + 1: command.rindex("\"")]
                command = command.split()
                send_command(client_socket, command[1], message, secret)

    elif role == "listen":
        HOST = ip_address
        # HOST = "127.0.0.11"
        PORT = 23

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print(f"listening on {HOST}")
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    receive_command(conn)
