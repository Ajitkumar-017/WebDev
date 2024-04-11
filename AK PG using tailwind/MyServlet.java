import java.io.*;
import javax.servlet.*;
import javax.servlet.http.*;

public class MyServlet extends HttpServlet {
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        // Your logic to execute the AdminPanel.class file
        AdminPanel adminPanel = new AdminPanel(); // Assuming AdminPanel is your class
        adminPanel.execute(); // Call a method within AdminPanel to execute desired logic

        // Respond to the client
        response.setContentType("text/html");
        PrintWriter out = response.getWriter();
        out.println("<html><body>");
        out.println("<h1>Admin Panel Executed Successfully!</h1>");
        out.println("</body></html>");
    }
}
