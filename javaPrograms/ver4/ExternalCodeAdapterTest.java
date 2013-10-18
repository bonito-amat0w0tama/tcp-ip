import jp.crestmuse.cmx.math.*;

public class ExternalCodeAdapterTest {

  static String code = "W,H = self.nmfMatrix(self.pop())\nself.push(W)\nself.push(H)";

  public static void main(String[] args) {
    try {
      ExternalCodeAdapter a = 
        new ExternalCodeAdapter(args[0], Integer.parseInt(args[1]));
      DoubleMatrix x = MathUtils.createDoubleMatrix(2, 2);
      x.set(0, 0, 1.0);
      x.set(1, 0, 2.0);
      x.set(0, 1, 3.0);
      x.set(1, 1, 2.0);
      System.out.println(MathUtils.toString1(x));
      a.pushDoubleMatrix(x);
      DoubleMatrix y = MathUtils.createDoubleMatrix(2, 2);
      y.set(0, 0, 4.0);
      y.set(1, 0, 5.0);
      y.set(0, 1, 6.0);
      y.set(1, 1, 7.0);
      System.out.println(MathUtils.toString1(y));
      a.pushDoubleMatrix(y);
      a.pushCode(code);
      DoubleMatrix z = (DoubleMatrix)a.pop();
      System.out.println("sum: " + MathUtils.toString1(z));
      a.pushEnd();
      a.close();
    } catch (Exception e) {
      e.printStackTrace();
      System.exit(1);
    }
  }

} 
