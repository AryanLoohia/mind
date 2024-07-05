// Get the modal
var modal = document.getElementById("loginModal");

// Get the button that opens the modal
var btn = document.getElementById("loginBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// Get the buttons for email and phone login
var emailLoginBtn = document.getElementById("emailLoginBtn");
var phoneLoginBtn = document.getElementById("phoneLoginBtn");

// Get the back buttons
var backToOptions2 = document.getElementById("backToOptions2");

// Get the login options and login forms
var loginOptions = document.getElementById("loginOptions");
var phoneLogin = document.getElementById("phoneLogin");

// When the user clicks the button, open the modal 
btn.onclick = function() {
    modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
    resetLoginForms();
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
        resetLoginForms();
    }
}

// Redirect to login.html for email login
emailLoginBtn.onclick = function() {
    window.location.href = "{{ url_for('login') }}";
}

// Show phone login form
phoneLoginBtn.onclick = function() {
    loginOptions.style.display = "none";
    phoneLogin.style.display = "block";
}

// Back to login options
backToOptions2.onclick = function() {
    resetLoginForms();
}

// Reset login forms to initial state
function resetLoginForms() {
    loginOptions.style.display = "block";
    phoneLogin.style.display = "none";
}

