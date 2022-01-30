import sys
from socket import *
from queue import Queue
from threading import Thread
import sys

HOST = "127.0.0.1"
RSIZE = 1024

class Manager:
    def __init__(self, i, port, maxconnection=5):
        super().__init__()
        self._name = f"Manager-{i}"
        self._port = port
        self._maxconnection = maxconnection
        self._server = socket(AF_INET, SOCK_STREAM)
        self._clients = []
        self._log = []

    @property
    def name(self):
        return self._name

    def background(self, name, conn):
        while True:
            try:
                data = conn.recv(RSIZE)
                if not data:
                    break
                message = data.decode("utf-8")
                self._log.append(name+":"+message)

                if message == "byebye":
                    self._log.append(f"{name}离开了聊天室")
                    for i in self._clients:
                        i[1].send(f"{name}离开了聊天室".encode("utf-8"))
                    break
                else:
                    member = []
                    if message[0] == "@":
                        m_list = message.split()
                        name = m_list[0][1:]
                        msg = m_list[1]
                        member.append(name)
                    else:
                        msg = message

                    if len(member) != 0:
                        for i in member:
                            for j in self._clients:
                                if i == j[0]:
                                    j[1].send(f"{name}@了你：{msg}".encode("utf-8"))
                    else:
                        for i in self._clients:
                            i[1].send(f"{name}：{msg}".encode("utf-8"))          
            except:
                print("error")
                break

    def save(self):
        with open("聊天记录.txt", "w", encoding="utf-8") as f:
            for i in self._log:
                f.write(i)

    def start(self):
        self._server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._server.bind((HOST, self._port))
        self._server.listen(self._maxconnection)
        while True:
            try:
                conn, addr = self._server.accept()
                print(f"client's connection: {conn}, its address:{addr}")
                name = conn.recv(RSIZE).decode("utf-8")
                for i in self._clients:
                    i[1].send(f"热烈欢迎{name}进入聊天室".encode("utf-8"))
                self._clients.append([name, conn, addr])
                b = Thread(target=self.background, args=(name, conn))
                # s = Thread(target=self.send, args=())
                b.start()
                # s.start()
                if conn is None:
                    continue
            except OSError:
                print("exit!")
                break

def main():
    PORT = int(sys.argv[1])

    server = Manager(HOST, PORT)
    server.start()

if __name__ == "__main__":
    main()