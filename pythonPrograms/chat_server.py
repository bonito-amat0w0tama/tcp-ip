#!/usr/bin/env python
# -*- coding: utf-8 -*-


import socket
#socketモジュールをインポートする。

host = '127.0.0.1'
port = 1111
#相手のIPアドレスと使用するポート番号を指定

serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#socket関数の引数を指定する。
#AF_INET→IPv4 インターネット・プロトコルを使用する
#SOCK_STREAM→TCP/IPを用いたSTREAM型のソケットを使用する

serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#SOL_SOCKET→setsockoptでソケットのオプションを指定する
#SO_REUSEADDR→前回のTCPセッションが残っていてもbindできる

serversock.bind((host,port))
#作成したソケットを変数host,portでバインドする

serversock.listen(1)
#リクエストの接続待ちキューを1に設定し、接続要求の準備をする

print 'Waiting for connections...'
clientsock, client_address = serversock.accept()
#accept→接続リクエストを受け取って、対応するIPアドレスとポート番号を返す

while True:
    rcvmsg = clientsock.recv(1024)
#クライアント側から文字列を1024byte受信する

    print 'Received -> %s' % (rcvmsg)
#受信したメッセージを表示する

    if rcvmsg == '':
      break
#受信した文字列が空であればループを終了する

    print 'Type message...'
    s_msg = raw_input()
#raw_input()関数で標準入力からの入力を変数に代入

    if s_msg == '':
      break
    print 'Wait...'

    clientsock.sendall(s_msg) 
#変数s_msgに代入した文字列を送信する

clientsock.close()
#ソケットを閉じる




