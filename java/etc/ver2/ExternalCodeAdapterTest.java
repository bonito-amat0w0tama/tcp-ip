import jp.crestmuse.cmx.math.*;

public class ExternalCodeAdapterTest {

  static String code = "print \"Hello World\"\nprint 1+2+3";

  public static void main(String[] args) {
    try {
      ExternalCodeAdapter a = 
        new ExternalCodeAdapter(args[0], Integer.parseInt(args[1]));
      a.pushCode(code);
      DoubleMatrix matrix = MathUtils.createDoubleMatrix(3, 2);
      matrix.set(0, 0, 1.0);
      matrix.set(1, 0, 2.0);
      matrix.set(2, 0, 3.0);
      matrix.set(0, 1, 2.0);
      matrix.set(1, 1, 4.0);
      matrix.set(2, 1, 6.0);
      a.pushDoubleMatrix(matrix);
      a.pushEnd();
      a.close();
    } catch (Exception e) {
      e.printStackTrace();
      System.exit(1);
    }
  }

} 