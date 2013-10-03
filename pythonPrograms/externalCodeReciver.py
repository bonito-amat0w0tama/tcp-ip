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
        self.clientsock, self.clientAddres = self.serversock.accept()


    # FIXME: name of clientsock
    def readHeader(self, clientsock):
        # bufferSize = 4
        header = clientsock.recv(self.byteSizeHeader) 
        return str(header)

    def readInt(self, clientsock):
        # buffersize = 4
        buff = clientsock.recv(self.byteSizeInt)
        if buff == '':
            intBuffer = 0
        else:
            # FIXME:variable name 
            intBuffer = struct.unpack('i', buff)[0]
        return intBuffer

    def getMatrix(self, clientsock):
        nmbRows = clientsock.recv(byteSizeInt)
        nmbCols = clientsock.recv(byteSizeInt)

    def run(self):

        head = ''
        while True:
            head = self.readHeader(self.clientsock)
            self.prihtHeader(head)
            size = self.readInt(self.clientsock)
            self.printSize(size)

            if head == 'code':
                #クライアント側から文字列をsize分受信する
                code = self.clientsock.recv(size)
                self.printCode(code)
                self.execCode(code)
            elif head == 'data':
                data = self.clientsock.recv(size)
            elif head == 'end' or size == 0:
                break
        self.clientsock.close()


    def printSize(self, size):
        print "Size -> %d" % (size)
    def prihtHeader(self, header):
        print "Header -> %s" % (header)
    def printCode(self, code):
        print 'Data -> %s' % (code)
    def execCode(self, code):
        print '----execute----'
        exec code
        print '----end--------'

if __name__ == '__main__':
    host = str('localhost')
    port = int(1111)
    server = externalCodeReceiver(host, port)
    server.run()

