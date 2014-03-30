import java.io.*;
import java.nio.*;
import java.net.*;

public class ExternalCodeAdapterReceiverSample {

  static int readInt(InputStream instream) throws IOException {
    byte[] buff = new byte[4];
    instream.read(buff);
    ByteBuffer bb = ByteBuffer.wrap(buff);
    bb.order(ByteOrder.LITTLE_ENDIAN);
    return bb.getInt();
  }


  public ExternalCodeAdapterReceiverSample(int port) throws IOException {
    ServerSocket ss = new ServerSocket(port);
    Socket socket = ss.accept();
    BufferedInputStream instream = new BufferedInputStream(socket.getInputStream());
    byte[] head = new byte[4];
    instream.read(head);
    System.out.println(new String(head));
    int size = readInt(instream);
    System.out.println(size);
    byte[] data = new byte[size];
    instream.read(data);
    System.out.println(new String(data));
  }

  public static void main(String []args) {
    try {
      new ExternalCodeAdapterReceiverSample(Integer.parseInt(args[0]));
    } catch (Exception e) {
      e.printStackTrace();
      System.exit(1);
    }
  }
}
