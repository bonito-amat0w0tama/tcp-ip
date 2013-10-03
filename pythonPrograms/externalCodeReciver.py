#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 受け取るバッファはStr型

import socket
import sys
import struct

class externalCodeReceiver():
    def __init__(self, host, port):
        
        self.byteSizeInt = 4
        self.byteSizeHeader = 4

        #AF_INET:IPv4 インターネット・プロトコル
        #SOCK_STREAM:TCP/IPを用いたSTREAM型のソケット
        self.serversock = socket.socket(socket.AF_INET, 
                socket.SOCK_STREAM)

        #host,portでバインドする
        self.serversock.bind((host,port))

        #リクエストの接続待ちキューを1に設定し、
        #接続要求の準備をする
        self.serversock.listen(1)
        print "waiting..."
        self.clientsock, clientAddres = self.serversock.accept()


    # FIXME: name of clientsock
    def readHeader(self):
        # bufferSize = 4
        header = self.clientsock.recv(self.byteSizeHeader) 
        return str(header)

    def readInt(self):
        # buffersize = 4
        # FIXME:variable name 
        intBuffer = struct.unpack('i', self.clientsock.recv(self.byteSizeInt))
        return intBuffer[0]

    def getMatrix(self, clientsock):
        nmbRows = clientsock.recv(byteSizeInt)
        nmbCols = clientsock.recv(byteSizeInt)

    def run(self):
        # data部受信
        while True:
            #クライアント側から文字列を8192Byte受信する
            data = self.clientsock.recv(8192)

            if not data:
                print "end"
                break

            #受信したメッセージを表示する
            print 'Data -> %s' % (data)
            print '----execute----'
            exec data
            print '----end--------'
            #変数s_msgに代入した文字列を送信する
            #clientsock.sendall(rcvmsg) 
        self.clientsock.close()

if __name__ == '__main__':
    host = str('localhost')
    port = int(1111)
    server = externalCodeReceiver(host, port)
    header = server.readHeader()
    size = server.readInt()
    print header
    print size
    server.run()

