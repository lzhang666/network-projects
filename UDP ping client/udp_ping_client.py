#!/usr/bin/python3
import sys
import socket
import time
from threading import Timer
import struct
import os
from ipaddress import ip_address

"""
global variables to calculate the total elapse time
"""
startTime = 0
endTime = 0


def main():
    """
    main function to get input parameters, set up socket, and kick off send and receive functions
    """
    server_ip, server_port, count, period, timeout = inputErrorCheck()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest = (server_ip, server_port)
    sock.settimeout(timeout)
    print('PING {}'.format(server_ip))

    typ = struct.pack('!B', 8)
    code = struct.pack('!B', 0)
    seqno = 1
    idf = (os.getpid()) % 65536 # takes mod in case the pid is too large

    pingSend(sock, dest, typ, code, idf, seqno, count, period)
    pongRecvd(sock, server_ip, count)


def pingSend(sock, dest, typ, code, idf, seqno, count, period):
    """
    this function assembles ping message and sends to server
    """
    idfByte = struct.pack('!H', idf)
    seqnoByte = struct.pack('!H', seqno)

    # convert timeStamp to millisecond precision
    timeStamp = int(time.time() * 1000)
    if seqno == 1:
        global startTime
        startTime = timeStamp
    timeStamp = timeStamp.to_bytes(6, byteorder='big')

    checksum = struct.pack('!H', 0)
    messageTemp = typ + code + checksum + idfByte + seqnoByte + timeStamp

    # compute checksum
    checksum = struct.pack('!H', getChecksum(messageTemp))
    message = typ + code + checksum + idfByte + seqnoByte + timeStamp
    sock.sendto(message, dest)

    # set sending termination condition
    if seqno == count:
        return
    # start timed thread
    timed = Timer(period, pingSend, args=[sock, dest, typ, code, idf, seqno + 1, count, period])
    timed.start()


def pongRecvd(sock, server_ip, count):
    """
    this function receives pong message send back from the server
    and prints the info of the received messages.
    upon socket timeout, this function closes socket and prints the final/conclusive statistics message
    """
    recvMax = float('-inf')
    recvMin = float('inf')
    recvSum = 0
    recvCount = 0
    global endTime
    while True:
        try:
            recvMsg, serv = sock.recvfrom(1024)
            recvTime = int(time.time()*1000)
            recvSeq = struct.unpack('!H', recvMsg[6:8])
            # verify received message via checksum
            if verifyChecksum(recvMsg):
                # parse recvMsg
                sendTime = int.from_bytes(recvMsg[8:], byteorder='big')
                elapsed = recvTime-sendTime
                recvMax = max(recvMax, elapsed)
                recvMin = min(recvMin, elapsed)
                recvSum += elapsed
                recvCount += 1
                print('PONG {}: seq={} time={} ms' .format(serv[0], recvSeq[0], elapsed))
                if recvCount == count:
                    endTime = int(time.time() * 1000)
                    break
            else:
                print('Checksum verification failed for echo reply seqno={}' .format(recvSeq[0]))

        except socket.timeout:
            endTime = int(time.time() * 1000)
            sock.close()
            break

    # print final message
    print('\n--- {} ping statistics ---' .format(server_ip))
    print('{} transmitted, {} received, {}% loss, time {} ms'.format(count, recvCount, int((count-recvCount)/count*100), endTime-startTime))
    if recvCount == 0:
        print('rtt min/avg/max = {}/{}/{} ms'.format(0, 0, 0))
    else:
        print('rtt min/avg/max = {}/{}/{} ms' .format(recvMin, int(recvSum/recvCount), recvMax))


def getChecksum(message):
    """
    this function computes and return the checksum of the message to be sent
    """
    carryOver = 1 << 16
    tempSum = 0
    for i in range(0, len(message), 2):
        tempSum = tempSum + (message[i] << 8) + message[i + 1]
        if tempSum >= carryOver:
            tempSum = tempSum + 1 - carryOver
    onesComp = ~tempSum & 0xffff
    return onesComp


def verifyChecksum(recvMsg):
    """
    this function verifies the received message against its checksum
    """
    carryOver = 1 << 16
    totalSum = 0
    for i in range(0, len(recvMsg), 2):
        totalSum = totalSum + (recvMsg[i] << 8) + recvMsg[i + 1]
        if totalSum >= carryOver:
            totalSum = totalSum + 1 - carryOver
    return totalSum == 65535


def inputErrorCheck():
    """
    this function checks if input parameters are valid
    if all parameters are valid, it returns an array of [server_ip, server_port, count, period, timeout]
    if any of the params are invalid, it terminates program and indicates which param is entered incorrectly
    """
    server_ip = ''
    server_port = 0
    count = 0
    period = 0
    timeout = 0
    try:
        s_ip = sys.argv[1][12:]
        try:
            ip_address(s_ip)
            server_ip = s_ip
        except ValueError:
            print('invalid IPv4 address')
            exit()
    except:
        print('IP address not entered correctly')
        exit()

    try:
        s_port = int(sys.argv[2][14:])
        server_port = s_port
    except:
        print('server port not entered correctly')
        exit()

    try:
        cnt = int(sys.argv[3][8:])
        count = cnt
    except:
        print('number of pings to send not entered correctly')
        exit()

    try:
        prd = int(sys.argv[4][9:])//1000
        period = prd
    except:
        print('wait interval not entered correctly')
        exit()

    try:
        tmo = int(sys.argv[5][10:]) // 1000
        timeout = tmo
    except:
        print('timeout not entered correctly')
        exit()

    return [server_ip, server_port, count, period, timeout]


if __name__ == "__main__":
    main()