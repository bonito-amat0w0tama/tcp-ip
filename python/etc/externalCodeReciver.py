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
        self.stack = []
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
        #print "buff"
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

    def pushMatrix(self, matrix):
        buff = ''
        head = 'data'
        rows = matrix.shape[0]
        cols = matrix.shape[1]
        size = rows * cols * 4 + 8

        buff = struct.pack('cccciii', head[0], head[1], head[2], head[3], size, rows, cols)
        for i in range(rows):
            for j in range(cols):
                # print type(matrix[i,j])
                val =  struct.pack('f', matrix[i,j])
                buff = buff + val

        self.printUnpackMatrix(buff)
        self.clientsock.send(buff)

    # FIXME: メソッドの設計(clientsockなど）
    def run(self):
        stack = []
        requestCount = 0
        head = ''

        while True:
            try:
                requestCount += 1
                self.printRequestCount(requestCount)
                head = self.readHeader(self.clientsock)
                self.printHeader(head)

                # headがendの時ここで終了しないとsizeの読み込みでsocet.errorが起きる
                if head == "end ":
                    print "Server is end"
                    break
                size = self.readInt(self.clientsock)
                self.printSize(size)

                if head == 'code':
                    #クライアント側から文字列をsize分受信する
                    code = self.clientsock.recv(size)
                    self.printCode(code)

                    # スコープ範囲の注意
                    exec code in locals()
                    # スタックからになるまでJavaにおくる
                    while len(self.stack) > 0:
                        self.pushMatrix(self.pop())

                elif head == 'data':
                    rows = self.readInt(self.clientsock)
                    cols = self.readInt(self.clientsock)
                    matrix = self.getMatrix(rows, cols, size, self.clientsock)
                    self.printMatrix(matrix)
                    self.stack.append(matrix)
                    #self.nmfMatrix(matrix)
                #elif head is 'end ' or size == 0:
                    #break
            except socket.error:
                #print str(type(e))
                print "Javaプログラムが不正終了した"

        self.clientsock.close()

    def push(self, matrix):
        print "----"
        print "push"
        print "----"
        self.printStack()
        self.stack.append(matrix)
        # self.pushMatrix(matrix)

    def pop(self):
        print "---"
        print "pop"
        print "---"
        self.printStack()
        return self.stack.pop()

    # FIXME: length is bad
    def convertBinaryToString(self, buff, length):
        head = ''
        for i in range(length):
            head = head+ struct.unpack('c', buff[i])[0]
        return head


    # FIXME: unncode
    def convertBinaryToMatirx(self, buff, rows, cols, begin):
        matrix = np.zeros((rows, cols))
        end = begin + 4

        for i in range(rows):
            for j in range(cols):
                matrix[i,j] = struct.unpack('f', buff[begin:end])[0]
                begin += 4
                end += 4

        print matrix

    def printUnpackMatrix(self, buff):
        print "------------"
        print 'unpackMatrix'
        print "------------"
        head = self.convertBinaryToString(buff, 4)
        size = struct.unpack('i', buff[4:8])[0]
        rows = struct.unpack('i', buff[8:12])[0]
        cols = struct.unpack('i', buff[12:16])[0]
        self.printHeader(head)
        self.printSize(size)
        self.printRowsAndCols(rows, cols)
        self.convertBinaryToMatirx(buff, rows, cols, 16)
        # print struct.unpack('cccciiiffff', buff)

    def printMatrix(self, matrix):
        print "data ->"
        print matrix

    def printRowsAndCols(self, rows, cols):
        print "Rows -> %d" % (rows)
        print "Cols -> %d" % (cols)

    # FIXME: うんこーど
    def printStack(self):
        print "stack_length -> %d" % (len(self.stack))
        for i in range(len(self.stack)):
            print "%d -> " % (i+1)
            print self.stack[i]

    def printSize(self, size):
        print "Size -> %d" % (size)

    def printHeader(self, header):
        print "Header -> %s" % (header)

    def printCode(self, code):
        print 'Code->'
        print '%s' % (code)

    def printRequestCount(self, count):
        print "------------------"
        print "RequestCount -> %d" % (count)
        print "------------------"

    def execCode(self, code):
        print '----execute----'
        exec code
        print '----end--------'

    def nmfMatrix(self, V):
        print "---"
        print "NMF"
        print "---"

        V = np.array(V)
        print "Target matrix"
        print V

        fctr = nimfa.mf(V, seed = 'random_vcol', method = 'lsnmf', rank = 40, max_iter = 10)
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

        return W, H

if __name__ == '__main__':
    host = str('localhost')
    port = int(1111)
    server = externalCodeReceiver(host, port)
    server.run()
