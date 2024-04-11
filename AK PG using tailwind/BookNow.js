// Function to validate the form before submission
function validateForm() {
    var phoneNumber = document.forms["signupForm"]["contact"].value;
    var password = document.forms["signupForm"]["psw"].value;
    var repeatPassword = document.forms["signupForm"]["psw-repeat"].value;

    // Basic validation example
    if (phoneNumber === "") {
        alert("Please enter your phone number.");
        return false;
    }
    if (phoneNumber.length > 10) {
        alert("Phone number cannot exceed 10 digits.");
        return false;
    }
    if (password === "") {
        alert("Please enter your password.");
        return false;
    }
    if (password !== repeatPassword) {
        alert("Passwords do not match.");
        return false;
    }

    // You can add more validation logic here as needed

    return true; // Form submission will proceed if all validations pass
}