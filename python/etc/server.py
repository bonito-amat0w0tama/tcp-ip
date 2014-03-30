#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import sys
import struct

host = 'localhost'
port = 1111

# コマンドライン引数からhost,postを取得
host = str(sys.argv[1])
port = int(sys.argv[2])

# print sys.argv.count()


#AF_INET→IPv4 インターネット・プロトコルを使用する
#SOCK_STREAM→TCP/IPを用いたSTREAM型のソケットを使用する
serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#作成したソケットを変数host,portでバインドする
serversock.bind((host,port))

#リクエストの接続待ちキューを1に設定し、接続要求の準備をする
serversock.listen(1)

print 'Waiting for connections...'
#accept→接続リクエストを受け取って、対応するIPアドレスとポート番号を返す
clientsock, client_address = serversock.accept()

# header, sizeを4バイトずつ受け取る
#header = str(clientsock.recv(4))
#size = int(clientsock.recv(4))
# 元からstr型なのでunpackする必要なし
header = clientsock.recv(4)
# int型にunpack
size = struct.unpack('i', clientsock.recv(4))

print 'Type_Header -> %s' % (type(header))
print 'Header -> %s' % (header)
print 'Type_Size -> %s' % (type(size))
print 'Size -> %d' % (size)

# data部受信
while True:

    #クライアント側から文字列を8092Byte受信する
    data = clientsock.recv(8192)

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

#ソケットを閉じる
clientsock.close()




