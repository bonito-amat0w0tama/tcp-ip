import java.io.*;
import java.nio.*;
import java.net.*;
import jp.crestmuse.cmx.math.*;

public class ExternalCodeAdapter {

  private Socket socket;
  private OutputStream outstream;
  private ByteOrder DEFAULT_ENDIAN =  ByteOrder.LITTLE_ENDIAN;

  public ExternalCodeAdapter(String hostname, int port) throws IOException {
    socket = new Socket(hostname, port);
    outstream = socket.getOutputStream();
  }

  public void pushCode(String code) throws IOException {
    byte[] bCode = code.getBytes();
    ByteBuffer buff = ByteBuffer.allocate(bCode.length + 8);
    buff.order(DEFAULT_ENDIAN);
    buff.put((byte)'c');
    buff.put((byte)'o');
    buff.put((byte)'d');
    buff.put((byte)'e'); 
    buff.putInt(bCode.length);
    buff.put(bCode);
    outstream.write(buff.array());
  }

  public void pushDoubleMatrix(DoubleMatrix matrix) throws IOException {
    ByteBuffer buff = 
      ByteBuffer.allocate(matrix.nrows() * matrix.ncols() * 4 + 16);
    buff.order(DEFAULT_ENDIAN);
    buff.put((byte)'d');
    buff.put((byte)'a');
    buff.put((byte)'t');
    buff.put((byte)'a');
    buff.putInt(matrix.nrows() * matrix.ncols() * 4 + 8);
    buff.putInt(matrix.nrows());
    buff.putInt(matrix.ncols());
    for (int i = 0; i < matrix.nrows(); i++) 
      for (int j = 0; j < matrix.ncols(); j++) 
        buff.putFloat((float)matrix.get(i, j));
    outstream.write(buff.array());
  }

  public void pushEnd() throws IOException {
    outstream.write("end ".getBytes());
  }

  public void close() throws IOException {
    outstream.close();
    socket.close();
  }
    

}
    