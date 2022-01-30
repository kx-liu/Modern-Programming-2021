## 第十三次作业 聊天室——网络编程

### 13.1 Manager

```python
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
```

### 13.2 Client

```python
import sys
from socket import *
from threading import Thread

HOST = "127.0.0.1"
RSIZE = 1024

class Sender(Thread):
    def __init__(self, client, name):
        super().__init__()
        self.client = client
        self.name = name
        self.message = None
        self._log = []

    def get_message(self):
        message = ""
        while message == "":
            print("\r您：", end="", flush=True)
            message = input()
        self.message = message
        self._log.append(self.name+":"+message)

    def send(self):
        self.client.send(self.message.encode("utf-8"))

    def save(self):
        with open(f"{self.name}聊天记录.txt", "w", encoding="utf-8") as f:
            for i in self._log:
                f.write(i)
                f.write("\n")

    def run(self):
        self.client.send(self.name.encode("utf-8"))
        while True:
            self.get_message()
            self.send()
            if self.message == "byebye":
                self.save()
                break
        print("The sender has stopped working...")

class Reciever(Thread):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.message = None

    def recieve(self):
        data = self.client.recv(RSIZE)
        self.message = data.decode("utf-8")

    def show(self):
        print("\r", end="")
        print(self.message)
        print("您：", end="", flush=True)

    def run(self):
        while True:
            try:
                self.recieve()
            except ConnectionResetError:
                print("The reciever has closed by Server...")
                break
            self.show()
            if self.message == "":
                print("The reciever has stopped working...")
                break

def main():
    PORT = int(sys.argv[1])
    name = sys.argv[2]

    print(f"欢迎{name}进入聊天室！")
    print("您：", end="")
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((HOST, PORT))

    s = Sender(client, name)
    r = Reciever(client)
    s.start()
    r.start()
    s.join()
    r.join()

    print("欢迎再来聊天！")

    client.close()

if __name__ == "__main__":
    main()
```

![image-20211225222959534](https://s2.loli.net/2022/01/29/XHNBZ4xao5isF6p.png)

![image-20211225224951145](https://s2.loli.net/2022/01/29/DSLUNwMAbl9RyZ1.png)

