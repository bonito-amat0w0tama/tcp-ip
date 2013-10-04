#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 受け取るバッファはStr型

import socket
import sys
import struct
import numpy as np
import nimfa

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

    def getMatrix(self, rows, cols, size, clientsock):
        # rows, cols の8バイト分マイナス
        dataSize = size - 8
        matrix = np.zeros((rows, cols))
        for i in range(rows):
            for j in range(cols):
                matrix[i,j] = struct.unpack('f', clientsock.recv(4))[0]
        return  matrix


    # FIXME: メソッドの設計(clientsockなど）
    def run(self):
        requestCount = 0
        head = ''
        while True:
            requestCount += 1
            self.printRequestCount(requestCount)
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
                rows = self.readInt(self.clientsock)
                cols = self.readInt(self.clientsock)
                matrix = self.getMatrix(rows, cols, size, self.clientsock)
                self.nmfMatrix(matrix)
            elif head == 'end' or size == 0:
                break
        self.clientsock.close()


    def printSize(self, size):
        print "Size -> %d" % (size)

    def prihtHeader(self, header):
        print "Header -> %s" % (header)

    def printCode(self, code):
        print 'Code-> %s' % (code)

    def printRequestCount(self, count):
        print "--------------------"
        print "RequestCount -> %d" % (count)
        print "--------------------"

    def execCode(self, code):
        print '----execute----'
        exec code
        print '----end--------'

    def nmfMatrix(self, V):
        V = np.array(V)
        print "Target matrix"
        print V

        fctr = nimfa.mf(V, seed = 'random_vcol', method = 'lsnmf', rank = 40, max_iter = 65)
        fctr_res = nimfa.mf_run(fctr)


        W = fctr_res.basis()
        print "Basis matrix"
        print W
        H = fctr_res.coef()
        print "Coef"
        print H

        print "Estimate"
        print np.dot(W, H)

        print 'Rss: %5.4f' % fctr_res.fit.rss()
        print 'Evar: %5.4f' % fctr_res.fit.evar()
        print 'K-L divergence: %5.4f' % fctr_res.distance(metric = 'kl')
        print 'Sparseness, W: %5.4f, H: %5.4f' % fctr_res.fit.sparseness()
if __name__ == '__main__':
    host = str('localhost')
    port = int(1111)
    server = externalCodeReceiver(host, port)
    server.run()

