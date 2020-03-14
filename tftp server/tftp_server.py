#!/Library/Frameworks/Python.framework/Versions/3.8/bin/python3
import socket
import sys
from threading import Thread
import struct
import random


def main():
    serverPort = int(sys.argv[1])
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', serverPort))
    # read in timeout
    timeout = int(sys.argv[2])/1000

    while True:
        data, clientAddress = sock.recvfrom(1024)
        opCode = struct.unpack('!H', data[:2])
        fileName = data[2:-7].decode('ASCII')

        # RRQ
        if opCode[0] == 1:
            readThread = Thread(target=readRequest, args=(fileName, clientAddress, timeout))
            readThread.start()
        # WRQ
        elif opCode[0] == 2:
            writeThread = Thread(target=writeRequest, args=(fileName, clientAddress, timeout))
            writeThread.start()


def readRequest(fileName, clientAddress, timeout):
    print('RRQ read request received')
    blockNum = 0
    clientAckNum = 0
    writeRead = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    writeRead.settimeout(timeout)

    # select a random port between 0 to 65535
    outPort = random.randint(0, 65535)
    while writeRead.bind(('', outPort)) == False:
        outPort = random.randint(0, 65535)

    #check if file exist
    try:
        file = open(fileName, 'rb')
    except:
        message = 'file not found'
        errorHandling(1, message, writeRead, clientAddress)

    while True:
        if blockNum == clientAckNum:
            blockNum += 1
            dataBlock = file.read(512)
        dataPacket = struct.pack('!HH', 3, blockNum) + dataBlock
        writeRead.sendto(dataPacket, clientAddress)

        # terminate transfer if packet size less than 512 bytes
        if len(dataBlock) < 512:
            print('file download completed')
            exit()

        try:
            nextRead, newAddress = writeRead.recvfrom(1024)

            # check if sent from correct address
            if newAddress != clientAddress:
                message = 'Unknown transfer ID'
                errorHandling(5, message, writeRead, clientAddress)

            # read opcode and client ACK #
            opCode, clientAckNum = struct.unpack('!HH', nextRead)

            if opCode == 5:
                message = 'error'
                errorHandling(0, message, writeRead, clientAddress)

            # print('opcode', opCode, type(opCode))

        except socket.timeout:
            print("timeout, resend packet")
            continue
        print('read packet #:', blockNum)
    file.close()


def writeRequest(fileName, clientAddress, timeout):
    print('enter write function')
    file = open(fileName, 'ab')
    sockWrite = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockWrite.settimeout(timeout)

    # select a random port between 0 to 65535
    outPort = random.randint(0, 65535)
    while sockWrite.bind(('', outPort)) == False:
        outPort = random.randint(0, 65535)

    # initialize server and client ACK #
    ackNum = 0
    clientBlockNum = 0

    while True:
        if clientBlockNum == ackNum:
            ack = struct.pack('!HH', 4, ackNum)
            sockWrite.sendto(ack, clientAddress)
            ackNum += 1
        else:
            sockWrite.sendto(ack, clientAddress)

        try:
            uploaded = sockWrite.recv(1024)
            opCode = struct.unpack('!H', uploaded[:2])
            if int(opCode[0]) == 3:
                clientBlockNum = struct.unpack('!H', uploaded[2:4])[0]
                if clientBlockNum == ackNum:
                    recvDataBlock = uploaded[4:]
                    file.write(recvDataBlock)
                    if len(recvDataBlock) < 512:
                        print('file upload completed')
                        # send the last ACK to server
                        for time in range(8):
                            ack = struct.pack('!HH', 4, ackNum)
                            sockWrite.sendto(ack, clientAddress)
                        file.close()
                        exit()

            if int(opCode[0]) == 5:
                message = 'error'
                errorHandling(0, message, sockWrite, clientAddress)

            print('write packet #:', ackNum)
        except socket.timeout:
            print("timeout, resend ACK")
            continue

def errorHandling(errorCode, errorMessage, socket, clientAddress):
    errorAck = struct.pack('!HH', 5, errorCode) + errorMessage.encode() + b'\x00'
    socket.sendto(errorAck, clientAddress)
    print('Error: ' + errorMessage)
    exit()

if __name__ == "__main__":
    main()