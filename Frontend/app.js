
const API = "http://127.0.0.1:5000/api";

// Set today's date
document.getElementById("date").value =
    new Date().toISOString().split("T")[0];


// Load Summary
async function loadSummary() {
    const response = await fetch(`${API}/summary`, {
        credentials: "include"
    });

    if (response.status === 401) {
        window.location.href = "login.html";
        return;
    }

    const data = await response.json();

    document.getElementById("balance").textContent =
        "₹" + data.balance.toFixed(2);

    document.getElementById("income").textContent =
        "₹" + data.income.toFixed(2);

    document.getElementById("expenses").textContent =
        "₹" + data.expenses.toFixed(2);
}


// Load Transactions
async function loadTransactions() {
    const response = await fetch(`${API}/transactions`, {
        credentials: "include"
    });

    if (response.status === 401) {
        window.location.href = "login.html";
        return;
    }

    const transactions = await response.json();

    const transactionList =
        document.getElementById("transactionList");

    transactionList.innerHTML = "";

    if (transactions.length === 0) {
        transactionList.innerHTML =
            "<p>No transactions found.</p>";
        return;
    }

    transactions.forEach(transaction => {
        const div = document.createElement("div");

        div.className = "transaction-item";

        div.innerHTML = `
            <div>
                <h3>${transaction.category}</h3>
                <p>${transaction.description || ""}</p>
                <small>${transaction.date}</small>
            </div>

            <div>
                <span class="${transaction.type}">
                    ${transaction.type === "income" ? "+" : "-"}
                    ₹${Number(transaction.amount).toFixed(2)}
                </span>

                <button onclick="deleteTransaction(${transaction.id})">
                    Delete
                </button>
            </div>
        `;

        transactionList.appendChild(div);
    });
}


// Add Transaction
document.getElementById("transactionForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const type = document.getElementById("type").value;
        const amount = document.getElementById("amount").value;
        const category = document.getElementById("category").value;
        const description = document.getElementById("description").value;
        const date = document.getElementById("date").value;

        const response = await fetch(`${API}/transactions`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
            body: JSON.stringify({
                type,
                amount,
                category,
                description,
                date
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message);

            document.getElementById("transactionForm").reset();

            document.getElementById("date").value =
                new Date().toISOString().split("T")[0];

            await loadSummary();
            await loadTransactions();
        } else {
            alert(data.message);
        }
    });


// Delete Transaction
async function deleteTransaction(id) {
    const confirmDelete = confirm(
        "Are you sure you want to delete this transaction?"
    );

    if (!confirmDelete) {
        return;
    }

    const response = await fetch(`${API}/transactions/${id}`, {
        method: "DELETE",
        credentials: "include"
    });

    const data = await response.json();

    if (response.ok) {
        alert(data.message);

        await loadSummary();
        await loadTransactions();
    } else {
        alert(data.message);
    }
}


// Logout
async function logout() {
    await fetch(`${API}/logout`, {
        method: "POST",
        credentials: "include"
    });

    window.location.href = "login.html";
}


// Load Dashboard
loadSummary();
loadTransactions();
