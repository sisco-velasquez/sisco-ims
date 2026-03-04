const API_URL = "http://127.0.0.1:8001/auth"; 

// 2. Toggle between Login and Register views
function toggleForm() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    
    if (loginForm.style.display === 'none') {
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    } else {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
    }
}

// 3. Handle Registration
async function handleRegister(event) {
    event.preventDefault(); // Stop page refresh
    console.log(" Registration started...");

    // Grab inputs from the Register Form
    const username = document.querySelector('#register-form input[type="text"]').value;
    const password = document.querySelector('#register-form input[type="password"]').value;

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            // Field names must match your 'UserCreate' schema in schemas.py
            body: JSON.stringify({ 
                username: username, 
                password: password 
            })
        });

        const result = await response.json();

        if (response.ok) {
            console.log(" Registration Success:", result);
            alert("Registration successful! You can now login.");
            toggleForm();
        } else {
            console.error("Registration Failed:", result.detail);
            alert("Error: " + (result.detail || "Something went wrong"));
        }
    } catch (error) {
        console.error("Network Error:", error);
        alert("Could not connect to the backend. Is FastAPI running on port 8000?");
    }
}

// 4. Handle Login
async function handleLogin(event) {
    event.preventDefault();
    console.log(" Login attempt started...");

    const username = document.querySelector('#login-form input[type="text"]').value;
    const password = document.querySelector('#login-form input[type="password"]').value;

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                username: username, 
                password: password 
            })
        });

        const result = await response.json();

        if (response.ok) {
            console.log(" Login Success:", result);
            
            // Change "my_token" to "access_token" to match dashboard.html
            localStorage.setItem("access_token", result.access_token);
            localStorage.setItem("username", result.username);
            
            alert("Welcome back, " + result.username + "!");
            window.location.href = "dashboard.html"; 
        }
    } catch (error) {
        console.error(" Network Error:", error);
        alert("Backend connection failed.");
    }
}

// 5. Attach Event Listeners
// This ensures the functions run when the forms are submitted
document.addEventListener('DOMContentLoaded', () => {
    const regForm = document.querySelector('#register-form form');
    const loginForm = document.querySelector('#login-form form');

    if (regForm) regForm.addEventListener('submit', handleRegister);
    if (loginForm) loginForm.addEventListener('submit', handleLogin);
});