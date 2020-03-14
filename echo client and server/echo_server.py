# this program is coded in Python 3
# run file in terminal using for example : python3 echo_server.py 12000
import socket
import sys
# serverPort = 12000
serverPort = int(sys.argv[1])
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print('The server is ready ro receive')
while True:
    connectionSocket, addr = serverSocket.accept()
    text = connectionSocket.recv(1024).decode()
    print(text)
    # capitalizeText = text.upper()
    connectionSocket.send(text.encode())
    connectionSocket.close()
