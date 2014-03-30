import java.io.*;
import java.nio.*;
import java.net.*;

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

  public void close() throws IOException {
    outstream.close();
    socket.close();
  }
    

}
    
