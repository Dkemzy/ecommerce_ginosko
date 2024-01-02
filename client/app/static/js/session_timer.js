// session_timer.js

// Set the timeout duration in milliseconds (e.g., 30 minutes)
const timeoutDuration = 30 * 60 * 1000; // 30 minutes

// Function to reset the session timeout
function resetSessionTimeout() {
    clearTimeout(window.sessionTimeout);
    window.sessionTimeout = setTimeout(logoutUser, timeoutDuration);
}

// Function to logout the user
function logoutUser() {
    window.location.href = "/logout";
}

// Attach event listeners to reset the session timeout on user activity
document.addEventListener("mousemove", resetSessionTimeout);
document.addEventListener("keypress", resetSessionTimeout);

// Initialize the session timeout on page load
resetSessionTimeout();
