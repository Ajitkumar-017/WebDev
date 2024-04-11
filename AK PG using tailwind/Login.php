<?php
// Establish MySQL connection
$Name = $_POST['name'];
$Number = $_POST['contact'];
$Location = $_POST['Location'];
$Date = $_POST['Date'];
$Password = $_POST['psw'];

$conn = new mysqli('localhost', 'root', '', 'booking');

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} else {
    // Check if the record already exists in the database
    $checkStmt = $conn->prepare("SELECT COUNT(*) AS num_records FROM bookings WHERE Name = ? AND Location = ? AND Date = ?");
    $checkStmt->bind_param("sss", $Name, $Location, $Date);
    $checkStmt->execute();
    $checkResult = $checkStmt->get_result();
    $checkRow = $checkResult->fetch_assoc();
    $numRecords = $checkRow['num_records'];

    if ($numRecords > 0) {
        // Record exists, check if it was created within the last 24 hours
        $checkCreatedStmt = $conn->prepare("SELECT * FROM bookings WHERE Name = ? AND Location = ? AND Date = ?");
        $checkCreatedStmt->bind_param("sss", $Name, $Location, $Date);
        $checkCreatedStmt->execute();
        $checkCreatedResult = $checkCreatedStmt->get_result();
        $checkCreatedRow = $checkCreatedResult->fetch_assoc();
        $createdTime = strtotime($checkCreatedRow['created_at']);
        $currentTime = time();

        if ($currentTime - $createdTime < 24 * 3600) { // 24 hours in seconds
            // Registration within 24 hours
            echo "You have already registered. We will reach you soon.";
        } else {
            // Registration older than 24 hours
            echo "We encountered an error. Please contact customer helpline number 1234567890.";
        }
    } else {
        // Hash the password for security
        $hashed_password = password_hash($Password, PASSWORD_DEFAULT);

        // Insert the new record into the database
        $stmt = $conn->prepare("INSERT INTO bookings (Name, Number, Location, Date, Password) VALUES (?, ?, ?, ?, ?)");

        if (!$stmt) {
            die("Error: " . $conn->error);
        }

        $stmt->bind_param("sssss", $Name, $Number, $Location, $Date, $hashed_password);
        $stmt->execute();
        echo "Registration Successful";
        $stmt->close();
    }

    // Close MySQL connection
    $conn->close();
}
?>
