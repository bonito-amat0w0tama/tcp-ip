public class ExternalCodeAdapterTest {

  static String code = "print \"Hello World\"\nprint 1+2+3";

  public static void main(String[] args) {
    try {
      ExternalCodeAdapter a = 
        new ExternalCodeAdapter(args[0], Integer.parseInt(args[1]));
      a.pushCode(code);
      a.close();
    } catch (Exception e) {
      e.printStackTrace();
      System.exit(1);
    }
  }

} 