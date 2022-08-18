import os
import socket
import sys

if __name__ == "__main__":
    print("1.   send request\n2.    port scanner\n3.    send file\n4.   receive file")
    choice = int(input("choice:"))
    if choice == 1:
        # host = "gaia.cs.umass.edu"
        # port = 80
        host = input("host:")
        port = int(input("port:"))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, port))
        except:
            print('Unable to connect')
            sys.exit()

        print('Connected to remote host')
        msg = ""
        req = input("-:")
        while len(req) != 0:
            msg = msg + req + "\r\n"
            req = input("-:")
            print(req)

        msg = msg + "\r\n"
        # msg = "GET /kurose_ross/interactive/index.php HTTP/1.1\r\nHost:gaia.cs.umass.edu\r\n\r\n".encode("ascii")
        print(msg)
        s.send(msg.encode("ascii"))

        while True:
            data = s.recv(4096)
            if not data:
                break
            else:
                print(data.decode())
    elif choice == 2:
        host = str(input("Enter the host to be scanned: "))  # Target Host, www.example.com
        ip_from = int(input("Enter port range start:"))
        ip_to = int(input("Enter port range end:"))

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("result:")
        while ip_from <= ip_to:

            try:
                s.connect((host, ip_from))
                print("Port {}: Open".format(ip_from))
            except:
                print("Port {}: Closed".format(ip_from))

            ip_from += 1
    elif choice == 3:
        host = input("Enter host address:")
        ip = input("Enter ip address:")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, ip))
            print("connected to remote host.")
            file_name = input("enter file name:")
            base_name = os.path.basename(file_name)
            s.send(base_name.encode())
            path = "D:\\lessons\\term6\\shabake\\projects\\project_two\\implementation\\FilesForSend"
            with open(path + os.sep + base_name, "rb") as f_read:
                while True:
                    bytes_read = f_read.read(1024)
                    if not bytes_read:
                        s.send("done".encode())
                        break
                    s.send(bytes_read)
        except:
            print("unable to connect!")
            sys.exit()
    elif choice == 4:
        host = input("Enter host address:")
        ip = input("Enter ip address:")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, ip))
            print("connected to remote host.")
            file_name = input("enter a name for file:")
            path = "D:\\lessons\\term6\\shabake\\projects\\project_two\\implementation\\ReceivedFiles"
            with open(path + os.sep + file_name, "wb") as f:
                while True:
                    data = s.recv(1024)
                    if "done" in data.decode():
                        break
                    f.write(data)
            print(f"{file_name} file received.")
        except:
            print("unable to connect!")
            sys.exit()
