function togglePasswordVisibility(fieldId, iconId) {
    var passwordField = document.getElementById(fieldId);
    var passIcon = document.getElementById(iconId);
    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        passIcon.src = "static/password-view-true.png";
    } else {
        passwordField.type = 'password';
        passIcon.src = "static/password-view-false.png";
    }
}

function loadLoginPage() {
    window.location.href = "/login"; // Replace 'register' with the appropriate endpoint for your register page
}

const login=document.querySelector('.login')
const loginBtn=document.querySelector('.loginBtn')
const register=document.querySelector('.register')
const registerBtn=document.querySelector('.registerBtn')
loginBtn.addEventListener('click', ()=>{
    login.classList.add('active')
    register.classList.add('active')
})

registerBtn.addEventListener('click', ()=>{
    login.classList.remove('active')
    register.classList.remove('active')
})


document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');

    registerForm.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent the default form submission

        // Collect the form data
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm_password').value;

        // Check if passwords match
        if (password !== confirmPassword) {
            alert('Passwords do not match!');
            return;
        }

        // Create an object to hold the form data
        const formData = {
            email: email,
            password: password,
            confirmPassword: confirmPassword
        };
    });
});