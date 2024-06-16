function togglePasswordVisibility(fieldId, iconId) {
    var passwordField = document.getElementById(fieldId);
    var passIcon = document.getElementById(iconId);
    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        passIcon.src = "{{ url_for('static', filename='password-view-true.png') }}";
    } else {
        passwordField.type = 'password';
        passIcon.src = "{{ url_for('static', filename='password-view-false.png') }}";
    }
}

function loadRegisterPage() {
    window.location.href = "/register"; // Replace 'register' with the appropriate endpoint for your register page
}