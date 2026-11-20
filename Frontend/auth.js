
const API = "http://127.0.0.1:5000/api";

// Show Signup Form
function showSignup() {
    document.getElementById("loginForm").classList.add("hidden");
    document.getElementById("signupForm").classList.remove("hidden");
    document.getElementById("message").textContent = "";
}

// Show Login Form
function showLogin() {
    document.getElementById("signupForm").classList.add("hidden");
    document.getElementById("loginForm").classList.remove("hidden");
    document.getElementById("message").textContent = "";
}

// Signup Function
async function signup() {
    const name = document.getElementById("signupName").value;
    const email = document.getElementById("signupEmail").value;
    const password = document.getElementById("signupPassword").value;

    if (!name || !email || !password) {
        document.getElementById("message").textContent = "Please fill all fields";
        return;
    }

    try {
        const response = await fetch(`${API}/signup`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
            body: JSON.stringify({
                name,
                email,
                password
            })
        });

        const data = await response.json();

        if (response.ok) {
            showLogin();
            document.getElementById("message").textContent = "Signup successful! Please login.";
        } else {
            document.getElementById("message").textContent = data.message;
        }

    } catch (error) {
        document.getElementById("message").textContent = "Server connection failed";
    }
}

// Login Function
async function login() {
    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;

    if (!email || !password) {
        document.getElementById("message").textContent = "Please enter email and password";
        return;
    }

    try {
        const response = await fetch(`${API}/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
            body: JSON.stringify({
                email,
                password
            })
        });

        const data = await response.json();

        document.getElementById("message").textContent = data.message;

        if (response.ok) {
            window.location.href = "index.html";
        }

    } catch (error) {
        document.getElementById("message").textContent = "Server connection failed";
    }
}
