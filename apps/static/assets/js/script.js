// Function to toggle the theme
function toggleTheme() {
  document.body.classList.toggle('dark-mode');

  // Save the current theme in localStorage
  if (document.body.classList.contains('dark-mode')) {
    localStorage.setItem('theme', 'dark');
    document.getElementById('theme-toggle').checked = true;
  } else {
    localStorage.setItem('theme', 'light');
    document.getElementById('theme-toggle').checked = false;
  }
}

// On page load, apply the saved theme
window.addEventListener('load', function () {
  const theme = localStorage.getItem('theme');

  // Apply the saved theme
  if (theme === 'dark') {
    document.body.classList.add('dark-mode');
    document.getElementById('theme-toggle').checked = true; // Ensure the toggle switch is in sync
  } else {
    document.body.classList.remove('dark-mode');
    document.getElementById('theme-toggle').checked = false;
  }

  // Add smooth transitions (optional for a better UX)
  document.body.style.transition = "background-color 0.3s, color 0.3s";
});

// Attach event listener for theme toggle button
document.getElementById('theme-toggle').addEventListener('change', toggleTheme);
// Function to toggle password visibility
function togglePasswordVisibility(toggleElement, passwordField) {
    toggleElement.addEventListener("click", function () {
        const type = passwordField.getAttribute("type") === "password" ? "text" : "password";
        passwordField.setAttribute("type", type);
        this.classList.toggle("fa-eye");
        this.classList.toggle("fa-eye-slash");
    });
}

// Show the Password Field during Login
const togglePassword = document.querySelector("#togglePassword");
const passwordField = document.querySelector("#id_password");
if (togglePassword && passwordField) {
    togglePasswordVisibility(togglePassword, passwordField);
}

// Show the Password Fields during Registration
const togglePassword1 = document.querySelector("#togglePassword1");
const passwordField1 = document.querySelector("#id_password1");
const togglePassword2 = document.querySelector("#togglePassword2");
const passwordField2 = document.querySelector("#id_password2");

if (togglePassword1 && passwordField1) {
    togglePasswordVisibility(togglePassword1, passwordField1);
}

if (togglePassword2 && passwordField2) {
    togglePasswordVisibility(togglePassword2, passwordField2);
}
