#### README
1) This script is written in python3 and runs in the python 3.5.2 environment on the department linux machines

2) The ping server initialization command is:\
    java -jar pingserver.jar --port=<port> [--loss_rate=<rate>] [--bit_error_rate=<rate>][--avg_delay=<delay>]

3) The udp ping client start up command is:\
    python3 udp_ping_client.py --server_ip=<server ip addr> --server_port=<server port> --count=<number of pings to send> --period=<wait interval> --timeout=<timeout>
    
4) For example, the udp ping client start up command I used was:\
    python3 udp_ping_client.py --server_ip=127.0.0.1 --server_port=8181 --count=10 --period=1000 --timeout=4000

5) The user can specify the server ip, server port, number of pings to send, 
wait period between pings, and the timeout period the port will remain open listening to pongs

6) The udp ping client will print out the sequence number and the round trip time it receives from the server

7) The communication is terminated either by receiving all the ping requests it sent out, or by a socket timeout.
At termination the client will print out the statistics including number of pings sent, number of pongs received, loss rate, 
total communication time, as well as the minimum, average and maximum round trip time.
