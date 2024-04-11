import java.sql.*;

public class AdminPanel {
    public void fetchDataFromDatabase() {
        // Database connection parameters
        String url = "jdbc:mysql://localhost:3306/booking";
        String username = "localhost";
        String password = "";

        try {
            // Establish database connection
            Connection connection = DriverManager.getConnection(url, username, password);

            // Create SQL statement
            Statement statement = connection.createStatement();

            // Execute SQL query
            String query = "SELECT * FROM your_table";
            ResultSet resultSet = statement.executeQuery(query);

            // Process and handle the retrieved data
            while (resultSet.next()) {
                int id = resultSet.getInt("Id");
                String name = resultSet.getString("Name");
                long number = resultSet.getLong("Number");
                String location = resultSet.getString("Location");
                Date date = resultSet.getDate("Date");
                Timestamp createdAt = resultSet.getTimestamp("created_at");

                // Perform desired operations with the retrieved data
                // For example, you can store the data in a list, display it in your admin panel, etc.
                System.out.println("ID: " + id + ", Name: " + name + ", Number: " + number + ", Location: " + location +
                                   ", Date: " + date + ", Created At: " + createdAt);
            }

            // Close resources
            resultSet.close();
            statement.close();
            connection.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
