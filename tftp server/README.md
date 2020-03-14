##### README
1) The script is written in python 3.8

2) The interpreter of python 3.8 is /Library/Frameworks/Python.framework/Versions/3.8/bin/python3

3) Implemented file not found error for RRQ.

4) For the WRQ method, if the file does not exist in the server, a new file will be created and be written to.
If the file does exist, for example a txt file, the content sent from client will append to the existing file.

5) The WRQ should be set with a longer timeout rate for connection through UDP proxy with drop rate. The TFTP protocol
works with 5000 ms timeout rate through the proxy (eg: python3 tftp_server.py 9090 5000)

6) The RRQ can be set with a shorter timeout such as 30 ms

7) During local test without server, the terminal line: (connect localhost 8080) did not work and must be replaced with (connect 127.0.0.1 8080).
However, the syntax (localhost) can be used during test using UDP proxy
