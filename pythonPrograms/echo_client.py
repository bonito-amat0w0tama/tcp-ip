import socket
import sys

host = str(sys.argv[1])
port = int(sys.argv[2])

clientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsock.connect((host,port))

while True:
    print 'Type message...'
    c_msg = raw_input()
    if c_msg == '':
        break
    print 'Wait...'

    clientsock.sendall(c_msg)
    rcvmsg = clientsock.recv(1024)
    print 'Received -> %s' % (rcvmsg)
    if rcvmsg == '':
        break
clientsock.close()

