import java.io.*;
import java.nio.*;
import java.net.*;
import jp.crestmuse.cmx.math.*;

public class ExternalCodeAdapterReceiverSample {

  static int readInt(InputStream instream) throws IOException {
    byte[] buff = new byte[4];
    instream.read(buff);
    ByteBuffer bb = ByteBuffer.wrap(buff);
    bb.order(ByteOrder.LITTLE_ENDIAN);
    return bb.getInt();
  }

  static String readHead(InputStream instream) throws IOException {
    byte[] buff = new byte[4];
    instream.read(buff);
    return new String(buff);
  }

  static DoubleMatrix getMatrix(byte[] bytes) {
    ByteBuffer buff = ByteBuffer.wrap(bytes);
    buff.order(ByteOrder.LITTLE_ENDIAN);
    int nrows = buff.getInt();
    int ncols = buff.getInt();
    DoubleMatrix matrix = MathUtils.createDoubleMatrix(nrows, ncols);
    for (int i = 0; i < nrows; i++) 
      for (int j = 0; j < ncols; j++) 
        matrix.set(i, j, buff.getFloat());
    return matrix;
  }

  public ExternalCodeAdapterReceiverSample(int port) throws IOException {
    ServerSocket ss = new ServerSocket(port);
    Socket socket = ss.accept();
    BufferedInputStream instream = new BufferedInputStream(socket.getInputStream());
    String head = "";
    while (!head.equals("end ")) {
      head = readHead(instream);
      System.out.println(head);
      int size = readInt(instream);
      System.out.println(size);
      byte[] data = new byte[size];
      instream.read(data);
      if (head.equals("code")) {
        String code = new String(data);
        System.out.println(new String(data));
      } else if (head.equals("data")) {
        DoubleMatrix matrix = getMatrix(data);
        System.out.println(MathUtils.toString(matrix));
      }
    }
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
