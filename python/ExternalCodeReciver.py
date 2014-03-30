#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 受け取るバッファはStr型

import socket
import sys
import struct
import numpy as np
import scipy.linalg as sl
#import scipy.sparse as sps
import nimfa
import os
import json
import datetime
import time
import pylab as plt
import Utils
import traceback
import numpy.linalg as nl


class ExternalCodeReceiver():
    nu = Utils.NMFUtils
    dict = {}
    def __init__(self, host, port):
        self.stack = []
        self.byteSizeInt = 4
        self.byteSizeHeader = 4
        self.host = host
        self.port = port

        self.recvSum = 0
        self.sendSum = 0

    def connectClient(self):
        #AF_INET:IPv4 インターネット・プロトコル
        #SOCK_STREAM:TCP/IPを用いたSTREAM型のソケット
        self.serversock = socket.socket(socket.AF_INET,
                socket.SOCK_STREAM)

        numConnectTry = 0
        numEndTry = 30
        while numConnectTry < numEndTry:
            numConnectTry += 1
            try:
                #host,portでバインドする
                self.serversock.bind((self.host, self.port))
                # if bind is succseed
                print "Connecting Succseed"
                break
            except socket.error as e:
                print "===接続エラー==="
                print str(e)
                print "接続回数:%d" % (numConnectTry)
                print "5秒後,再接続します"
                traceback.print_exc()
                print "=================\n"
                time.sleep(5)

        if self.serversock == None:
            print "end_server_by_error"
            sys.exit()

        #リクエストの接続待ちキューを1に設定し、 #接続要求の準備をする
        self.serversock.listen(1)
        print "waiting_ClientConnet...\n"
        self.clientsock, self.clientAddres = self.serversock.accept()

    def closeSocket(self):
        self.serversock.close()
        self.clientsock.close()

    # FIXME: name of clientsock
    def readHeader(self, clientsock):
        # bufferSize = 4
        header = clientsock.recv(self.byteSizeHeader)
        self.recvSum += self.byteSizeHeader
        return str(header)

    def readInt(self, clientsock):
        # buffersize = 4
        #print "buff"
        buff = clientsock.recv(self.byteSizeInt)
        self.recvSum += self.byteSizeInt
        if buff == '':
            intBuffer = 0
        else:
            # FIXME:variable name 
            intBuffer = struct.unpack('i', buff)[0]
        return intBuffer

    def getMatrix(self, rows, cols, size, clientsock):
        # rows, cols の8バイト分マイナス
        #dataSize = size - 8
        matrix = np.zeros((rows, cols))
        for i in range(rows):
            for j in range(cols):
                matrix[i,j] = struct.unpack('f', clientsock.recv(4))[0]
                self.recvSum += 4
        return  matrix

    def sendMatrix(self, matrix):

        buff = ''
        head = 'data'
        rows = matrix.shape[0]
        cols = matrix.shape[1]
        size = rows * cols * 4 + 8

        buff = struct.pack('cccciii', head[0], head[1], head[2], head[3], size, rows, cols)

        list = []
        for i in range(rows):
            for j in range(cols):
                # print type(matrix[i,j])
                matVal = matrix[i,j]

                val =  struct.pack('f', matVal)
                uVal = struct.unpack('f', val)
                buff = buff + val

                list.append(uVal)

        print "----------"
        print "sendMatrix"

        self.printUnpackMatrix(buff)
        self.clientsock.send(buff)
        self.sendSum += len(buff)

        print "sendSum:%d" % (self.sendSum)

        # for i in list:
        #     print i

    def sendError(self):
        head = "eror"
        buff = struct.pack("cccc", head[0], head[1], head[2], head[3])
        self.clientsock.send(buff)
        self.sendSum += len(buff)
        print "sendedError"

    # FIXME: メソッドの設計(clientsockなど）
    def run(self):
        #stack = []
        requestCount = 1
        head = ''
        self.connectClient()

        while True:
            try:
                try:
                    head = self.readHeader(self.clientsock)
                except socket.error as e:
                    print "headの読み込みエラー"
                    print str(e)
                    traceback.print_exc()
                    head = "exception"
                    # Java側が異常な終了をしたため再接続
                    self.closeSocket()
                    self.connectClient()

                # headがendの時ここで終了しないとsizeの読み込みでsocet.errorが起きる
                if head != "exception":
                    if head == "end ":
                        self.printRequestCount(requestCount)
                        self.printHeader(head)
                        requestCount += 1
                        # print "Server is end"
                        # break

                        print "ClientProgram_end"
                        self.closeSocket()
                        self.connectClient()

                    #size = self.readInt(self.clientsock)
                    #self.printSize(size)

                    if head == 'code':
                        self.printRequestCount(requestCount)
                        self.printHeader(head)
                        requestCount += 1
                        size = self.readInt(self.clientsock)
                        self.printSize(size)
                        #クライアント側から文字列をsize分受信する
                        code = self.clientsock.recv(size)
                        self.recvSum += size
                        self.printCode(code)
                        print "recvSum:%d" % (self.recvSum)

                        try :
                            # スコープ範囲の注意
                            #exec code in locals()
                            exec code in globals()

                        except (SyntaxError, TypeError, NameError, IndexError, AttributeError, ValueError ) as e:
                            print "=== エラー発生 ==="
                            print "type:" + str(type(e))
                            print "message:" + str(e)
                            print "実行コードに" + str(type(e)) + "があります"
                            traceback.print_exc()
                            self.sendError()

                            # エラーで終了したので再接続
                            self.closeSocket()
                            self.connectClient()
                        except MemoryError as e:
                            print "=== エラー発生 ==="
                            print "type:" + str(type(e))
                            print "message:" + str(e)
                            print "実行コードに" + str(type(e)) + "があります"
                            traceback.print_exc()
                            self.sendError()

                            # エラーで終了したので再接続
                            self.closeSocket()
                            self.connectClient()

                        # スタックが空になるまでJavaにおくる
                        # while len(self.stack) > 0:
                        #     self.pushMatrix(self.pop())

                    elif head == 'data':
                        self.printRequestCount(requestCount)
                        self.printHeader(head)
                        requestCount += 1
                        size = self.readInt(self.clientsock)
                        self.printSize(size)
                        rows = self.readInt(self.clientsock)
                        cols = self.readInt(self.clientsock)
                        self.printRowsAndCols(rows, cols)
                        matrix = self.getMatrix(rows, cols, size, self.clientsock)
                        self.printMatrix(matrix)
                        self.stack.append(matrix)

                        print "recvSum:%d" % (self.recvSum)

                    #elif head is 'end ' or size == 0:
                        #break

            except socket.error as e:
                print str(e)
                print "Javaプログラムが不正終了した"
                traceback.print_exc()
                self.closeSocket()
                self.connectClient()

        self.closeSocket()

    def push(self, matrix, name):
        print "----"
        print "push"
        print "----"
        self.stack.append(matrix)
        self.printStack()
        # ここでPushMatrixしたことがバグの原因
        # self.pushMatrix(matrix)

    def setMatrix(self, data, name):
        print "----"
        print "setMatrix"
        print "----"

        self.dict[name] = data
        self.printDict()

    def pop(self):
        print "---"
        print "pop"
        print "---"
        self.printStack()
        return self.stack.pop()

    def takeMatrix(self, name):
        print "---"
        print "takeMatrix"
        print "---"
        self.printDict()
        return self.dict[name]


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

        #for i in range(matrix.shape[0]):
        #    for j in range(matrix.shape[1]):
        #        print matrix[i,j]

    def getPseudoInverseMatrix(self, mat):
        return sl.pinv(mat)

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
        print "Values in Stack"
#        for i in range(len(self.stack)):
#            print "%d -> " % (i+1)
#            print self.stack[i]

        count = 1
        for val in self.stack:
            print "%d -> " % (count)
            print val

        print "-------------"

    def printSize(self, size):
        print "Size -> %d" % (size)

    def printHeader(self, header):
        print "Header -> %s" % (header)

    def printCode(self, code):
        print 'Code->'
        print '%s' % (code)

    def printDict(self):
        print "Dist_length-> %d" % (len(self.dict))
        print "Values in dic"
        for key, val in self.dict.iteritems(): 
            print "%s -> " % (key)
            print self.dict[key]
        print "-------------"


    def printRequestCount(self, count):
        print "------------------"
        print "RequestCount -> %d" % (count)
        print "------------------"

    def execCode(self, code):
        print '----execute----'
        exec code
        print '----end--------'

    def nmfMatrix(self, V, method, rank, maxIter):
        stime = time.clock()
        print "---"
        print "NMF"
        print "---"

        V = np.array(V)
        print "Target matrix"
        print V.shape[0]
        print V.shape[1]
        print V


#         X = sp.rand(V.shape[0], V.shape[1], density=1).tocsr()
        # NMFの際の、基底数やイテレーションの設定
        # rank = 8 
        # maxIter = 2000 
        # method = "snmf"

#         init2arizer = nimfa.methods.seeding.random_vcol.Random_vcol()
        initiarizer = nimfa.methods.seeding.random.Random()
        initW, initH = initiarizer.initialize(V, rank, {})

        fctr = nimfa.mf(V, seed = 'random_vcol', method = method, rank = rank, max_iter = maxIter)
        # fctr = nimfa.mf(V, method = "lsnmf", rank = rank, max_iter = maxIter, W = initW, H = initH)
        fctr_res = nimfa.mf_run(fctr)

        W = fctr_res.basis()
        print "Basis matrix"
        print W.shape[0]
        print W.shape[1]
        print W
        H = fctr_res.coef()
        print "Coef"
        print H.shape[0]
        print H.shape[1]
        print H

        print "Estimate"
        print np.dot(W, H)

        print 'Rss: %5.4f' % fctr_res.fit.rss()
        print 'Evar: %5.4f' % fctr_res.fit.evar()
        print 'K-L divergence: %5.4f' % fctr_res.distance(metric = 'kl')
        print 'Sparseness, W: %5.4f, H: %5.4f' % fctr_res.fit.sparseness()

        #sm = fctr_res.summary()
        #print type(sm)
        # print "Rss: %8.3f" % sm['rss']
        # # Print explained variance.
        # print "Evar: %8.3f" % sm['evar']
        # # Print actual number of iterations performed
        # print "Iterations: %d" % sm['n_iter']

        # プロットの際に不具合が生じるため,numpy.ndarray型に変換
        NW = np.asarray(W)
        NH = np.asarray(H)

        etime = time.clock()
        ptime = etime - stime

        sec = int(ptime) % 60
        minu = int(ptime) / 60 % 60
        hour = int(minu) / 60

        times = str(hour) + "時間" + str(minu) + "分" + str(sec) + "秒"
        print times

        etc = {'method': method, 'rank': rank, 'maxiter': maxIter, 'times': times}
        
        return NW, NH, etc

    def createZeroMatrix(self, rows, cols):
        return np.zeros([rows, cols])

    def writeDataToJson(self, name, data, dateFlag=True):
        try:
            if dateFlag:
                date = datetime.datetime.today()
                dateStr = str(date.year) + "-" + str(date.month) + "-" +str(date.day) + "-" + str(date.hour) + ":" + str(date.minute)
                filePath = "../../jsonData/" + name + "_" + dateStr + ".json"
            else:
                filePath = "../../jsonData/" + name + ".json" 

            # ファイルが存在しない場合のみ、Jsonファイルを生成
            if not os.path.isfile(filePath):
                file = open(filePath, "w")
                json.dump(data, file)
                file.close()
                print "Writing_josn_Succeed"
            else:
                print "File_exists"
        except Exception as e:
            print str(e)
            print type(e)
            traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        host = str(sys.argv[1])
        port = int(sys.argv[2])
    else:
        host = str('localhost')
        port = int(1111)

    server = ExternalCodeReceiver(host, port)
    server.run()

