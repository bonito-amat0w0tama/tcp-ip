import java.io.*;
import java.nio.*;
import java.net.*;
import jp.crestmuse.cmx.math.*;

public class ExternalCodeAdapter {
	private Socket socket;
	private OutputStream outstream;
	private InputStream instream;
	private ByteOrder DEFAULT_ENDIAN = ByteOrder.LITTLE_ENDIAN;
	
	
	private int recvSum = 0;
	private int sendSum = 0;
	private boolean zeroFlag = false;
	public ExternalCodeAdapter(String hostname, int port) throws IOException {
		socket = new Socket(hostname, port);
		outstream = socket.getOutputStream();
		instream = socket.getInputStream();
	}

	private int readInt(InputStream instream) throws IOException {
recvSum += 4;
		byte[] buff = new byte[4];
		instream.read(buff);
		ByteBuffer bb = ByteBuffer.wrap(buff);
		bb.order(DEFAULT_ENDIAN);
		return bb.getInt();
	}

	private String readHead(InputStream instream) throws IOException {
recvSum +=4;
		byte[] buff = new byte[4];
		instream.read(buff);
		return new String(buff);
	}
	//バグのげいいんげいいん
	private DoubleMatrix getMatrix(byte[] bytes) {
		ByteBuffer buff = ByteBuffer.wrap(bytes);
		buff.order(DEFAULT_ENDIAN);
		int nrows = buff.getInt();
recvSum += 4;
		int ncols = buff.getInt();
recvSum += 4;
		System.out.println("nrows:" + nrows);
		System.out.println("ncols:" + ncols);
		DoubleMatrix matrix = MathUtils.createDoubleMatrix(nrows, ncols);
		
		float val = 0;
		for (int i = 0; i < nrows; i++) {
			for (int j = 0; j < ncols; j++) {
				try {
					val = buff.getFloat();
				} catch (Exception e) {
					System.out.println("erororo");
				}

				// バグチェックのため、最初にゼロになる場所を表示
				if (val == 0.0 && !zeroFlag) {
					System.out.println("rows:" + i + "\n" + "cols:" + j);
					System.out.println("Error-recvSum:" + recvSum);
					System.out.println("sendSum:" + sendSum);
					zeroFlag = true;
				}
recvSum += 4;
				matrix.set(i, j, val);
			}
		}
System.out.println("recvSum:" + recvSum);
		return matrix;
	}

	public Object pop() throws IOException {
		System.out.println("Pop");
		InputStream in = instream;
		String head = readHead(in);
		if (head.equals("data")) {
			int size = readInt(in);
			System.out.println("size:" + size);
			byte[] data = new byte[size];

			int len = in.read(data);
			// inputStream.read()の使用で最大lenバイトまでしか読み込まない仕様のため
			// size分まで読み込むまでループさせる
			int readSum= 0;
			while (readSum < size ) {
				readSum += len;
				int readSize = size - readSum;
				len = in.read(data, readSum, readSize);
			}
			DoubleMatrix matrix = getMatrix(data);

			return matrix;
		} else if(head.equals("eror")) { 
			//送ったコードなどにエラーが発生した場合
			throw new IOException("Header : " + head);
		} else {
			throw new IOException("Invalid header: " + head);
		}
	}

	public void pushCode(String code) throws IOException {
		System.out.println("PushCode");
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
		
sendSum += bCode.length + 8;
	}

	public void pushDoubleMatrix(DoubleMatrix matrix) throws IOException {
		System.out.println("PushDoubleMatrix");
		ByteBuffer buff =
				ByteBuffer.allocate(matrix.nrows() * matrix.ncols() * 4 + 16);
		buff.order(DEFAULT_ENDIAN);
		buff.put((byte)'d');
		buff.put((byte)'a');
		buff.put((byte)'t');
		buff.put((byte)'a');
		buff.putInt(matrix.nrows() * matrix.ncols() * 4 + 8);
//		System.out.println(matrix.nrows() * matrix.ncols() * 4 + 8);
		buff.putInt(matrix.nrows());
		buff.putInt(matrix.ncols());
		for (int i = 0; i < matrix.nrows(); i++)
			for (int j = 0; j < matrix.ncols(); j++)
				buff.putFloat((float)matrix.get(i, j));
		outstream.write(buff.array());
		outstream.flush();
		
sendSum += matrix.nrows() * matrix.ncols() * 4 +16;
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