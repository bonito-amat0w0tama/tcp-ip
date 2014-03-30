import java.io.*;
import java.nio.*;
import java.net.*;
import jp.crestmuse.cmx.math.*;

public class ExternalCodeAdapter {

  private Socket socket;
  private OutputStream outstream;
  private InputStream instream;
  private ByteOrder DEFAULT_ENDIAN =  ByteOrder.LITTLE_ENDIAN;

  public ExternalCodeAdapter(String hostname, int port) throws IOException {
    socket = new Socket(hostname, port);
    outstream = socket.getOutputStream();
    instream = socket.getInputStream();
  }

  private int readInt(InputStream instream) throws IOException {
    byte[] buff = new byte[4];
    instream.read(buff);
    ByteBuffer bb = ByteBuffer.wrap(buff);
    bb.order(DEFAULT_ENDIAN);
    return bb.getInt();
  }

  private String readHead(InputStream instream) throws IOException {
    byte[] buff = new byte[4];
    instream.read(buff);
    return new String(buff);
  }

  private DoubleMatrix getMatrix(byte[] bytes) {
    ByteBuffer buff = ByteBuffer.wrap(bytes);
    buff.order(DEFAULT_ENDIAN);
    int nrows = buff.getInt();
    int ncols = buff.getInt();
    DoubleMatrix matrix = MathUtils.createDoubleMatrix(nrows, ncols);
    for (int i = 0; i < nrows; i++) 
      for (int j = 0; j < ncols; j++) 
        matrix.set(i, j, buff.getFloat());
    return matrix;
  }

  public Object pop() throws IOException {
    String head = readHead(instream);
    if (head.equals("data")) {
      int size = readInt(instream);
      byte[] data = new byte[size];
      instream.read(data);
      DoubleMatrix matrix = getMatrix(data);
      return matrix;
    } else {
      throw new IOException("Invalid header: " + head);
    }
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
    outstream.flush();
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
    outstream.flush();
  }

  public void pushEnd() throws IOException {
    outstream.write("end ".getBytes());
    outstream.flush();
  }

  public void close() throws IOException {
    outstream.close();
    instream.close();
    socket.close();
  }
    

}
    
