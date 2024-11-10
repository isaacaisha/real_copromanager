// Function to toggle the theme
function toggleTheme() {
  document.body.classList.toggle("dark-mode");

  // Save the current theme in localStorage
  const isDarkMode = document.body.classList.contains("dark-mode");
  localStorage.setItem("theme", isDarkMode ? "dark" : "light");
  document.getElementById("theme-toggle").checked = isDarkMode;

  // Dynamically update reCAPTCHA theme
  toggleCaptchaTheme(isDarkMode);
}

// On page load, apply the saved theme
window.addEventListener("load", function () {
  const theme = localStorage.getItem("theme");
  const isDarkMode = theme === "dark";

  // Apply the saved theme
  document.body.classList.toggle("dark-mode", isDarkMode);
  document.getElementById("theme-toggle").checked = isDarkMode;

  // Add smooth transitions (optional for a better UX)
  document.body.style.transition = "background-color 0.3s, color 0.3s";

  // Render reCAPTCHA based on theme
  toggleCaptchaTheme(isDarkMode);
});

// Function to dynamically render reCAPTCHA with the correct theme and size
function toggleCaptchaTheme(isDarkMode) {
  const captchaContainer = document.getElementById("recaptcha-container");

  // Remove the existing reCAPTCHA if it exists
  while (captchaContainer.firstChild) {
    captchaContainer.removeChild(captchaContainer.firstChild);
  }

  // Set the theme and size
  const theme = isDarkMode ? "dark" : "light";

  // Re-render reCAPTCHA with the new theme and compact size
  grecaptcha.render("recaptcha-container", {
    sitekey: "6LeJM3oqAAAAAE1TqJOWbCvg5ovgYl6rn0zD6f9d", // Replace with your actual site key
    theme: theme,
    size: "compact", // Compact size for better UX
  });
}

// Attach event listener for theme toggle button
document.getElementById("theme-toggle").addEventListener("change", toggleTheme);

// Function to toggle password visibility
function togglePasswordVisibility(toggleElement, passwordField) {
  toggleElement.addEventListener("click", function () {
    const type =
      passwordField.getAttribute("type") === "password" ? "text" : "password";
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
