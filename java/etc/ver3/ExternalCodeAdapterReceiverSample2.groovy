import java.io.*;
import java.nio.*;
import java.net.*;
import jp.crestmuse.cmx.math.*;


class ExternalCodeAdapterReceiverSample2 {

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

    public void pushDoubleMatrix(DoubleMatrix matrix) throws IOException {
        ByteBuffer buff = 
            ByteBuffer.allocate(matrix.nrows() * matrix.ncols() * 4 + 16);
        buff.order(ByteOrder.LITTLE_ENDIAN);
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

    def push(matrix) {
        stack.push(matrix)
        pushDoubleMatrix(matrix)
    }

    def pop() {
        stack.pop()
    }


    def stack = []
    def shell = new GroovyShell(new Binding(self: this))
    def instream
    def outstream

    static void main(String[] args) {
        DoubleMatrix.mixin(Operations)
            new ExternalCodeAdapterReceiverSample2(Integer.parseInt(args[0]))
    }

    ExternalCodeAdapterReceiverSample2(int port) {
        def ss = new ServerSocket(port)
        def socket = ss.accept()
        instream = new BufferedInputStream(socket.getInputStream())
        outstream = new BufferedOutputStream(socket.getOutputStream())
        String head = ""
        while (!head.equals("end ")) {
            head = readHead(instream) 
            println head
            int size = readInt(instream)
            println size
            byte[] data = new byte[size]
            instream.read(data)
            if (head.equals("code")) {
                String code = new String(data)
                println code
                shell.evaluate(code)
            } else if (head.equals("data")) {
                DoubleMatrix matrix = getMatrix(data)
                println(MathUtils.toString(matrix))
                stack.push(matrix)
            }
        }
    }

}
