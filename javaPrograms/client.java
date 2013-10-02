import java.net.*;
import java.io.*;


public class JavaClient {
    public static void main(String[] args) throws IOException {
        // test
        // コマンドライン引数が異常の時
        if ((args.length < 2) || (args.length > 3)) {
            throw new IllegalArgumentException("Parameter(s): <Server> <Word> [<port>]");
        }
        // hostの設定
        String server = args[0];
        // メッセージの設定
        byte[] byteBuffer = args[1].getBytes();
        // portの設定
        int servPort = (args.length == 3) ? Integer.parseInt(args[2]) : 7;

        // socketの作成
        Socket socket  = new Socket(server, servPort);
        System.out.println("Connected to server...sending echo string");

        InputStream in = socket.getInputStream();
        OutputStream out = socket.getOutputStream();

        // Byteに変換したメッセージをストリームに書き込む
        out.write(byteBuffer);

        socket.close();
    }
}
