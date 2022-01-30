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