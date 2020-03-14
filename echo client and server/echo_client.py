# this program is coded in Python 3
# run file in terminal using for example : python3 echo_client.py localhost 12000
import socket
import sys
# serverName = 'localhost'
# serverPort = 12000
serverName = sys.argv[1]
serverPort = int(sys.argv[2])
while True:
    text = input('Send a message to server: ')
    if text:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
        clientSocket.send(text.encode())
        modifiedText = clientSocket.recv(1024)
        print('Server replies: ', modifiedText.decode())
        clientSocket.close()
