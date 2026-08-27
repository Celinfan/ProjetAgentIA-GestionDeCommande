const form = document.getElementById("order-form");
const response = document.getElementById("response");

form.addEventListener("submit", async function (event) {

    event.preventDefault();

    const message = document.getElementById("message").value;

    const order = {
        text: `${message}`
    };

    response.textContent = "Traitement de la commande...";

    try {

        const result = await fetch("http://localhost:8000/orders", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(order)
        });

        if (!result.ok) {
            throw new Error("Erreur lors du traitement de la commande.");
        }

        const data = await result.json();

        response.textContent =
            `Statut : ${data.status}
Action : ${data.action}
Client : ${data.customer}
Total : ${data.total} €
Raison : ${data.reason}`;

    } catch (error) {

        response.textContent =
            `Une erreur est survenue : ${error.message}`;
    }
});