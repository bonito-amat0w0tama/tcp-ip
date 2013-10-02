#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import sys

#host = '127.0.0.1'
#port = 1111

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

while True:
    #クライアント側から文字列を1024byte受信する
    rcvmsg = clientsock.recv(1024)

    if not rcvmsg:
        print "end"
        break

    #受信したメッセージを表示する
    print 'Received -> %s' % (rcvmsg)


    #変数s_msgに代入した文字列を送信する
    clientsock.sendall(rcvmsg) 

#ソケットを閉じる
clientsock.close()




