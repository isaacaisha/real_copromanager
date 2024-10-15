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
