const form = document.getElementById("order-form");
const response = document.getElementById("response");

const messageInput = document.getElementById("message");
const conversation = document.getElementById("conversation");
const orderResult = document.getElementById("order-result");
const submitButton = document.getElementById("submit-button");

const typingIndicator = document.getElementById("typing-indicator");

// Identifiant de la conversation.
// Il doit être conservé entre les différentes requêtes.
let conversationId = null;

// ---------------------------------------------------------
// Ajoute un message dans l'interface
// ---------------------------------------------------------

function addMessage(role, text) {

    const messageElement = document.createElement("div");

    messageElement.classList.add(
        "message",
        role === "user"
            ? "user-message"
            : "assistant-message"
    );

    const label = document.createElement("strong");

    label.textContent =
        role === "user"
            ? "Vous : "
            : "Assistant : ";

    const content = document.createElement("span");

    content.textContent = text;

    messageElement.appendChild(label);
    messageElement.appendChild(content);

    conversation.appendChild(messageElement);
    conversation.hidden = false;

    // Faire défiler automatiquement vers le dernier message
    conversation.scrollTop = conversation.scrollHeight;
}


// ---------------------------------------------------------
// Affiche la commande finale
// ---------------------------------------------------------

function displayOrder(data) {

    orderResult.hidden = false;

    response.innerHTML = "";

    const title = document.createElement("h3");

    title.textContent = "Commande traitée";

    response.appendChild(title);


    const status = document.createElement("p");

    status.innerHTML =
        `<strong>Statut :</strong> ${data.status}`;

    response.appendChild(status);


    const customer = document.createElement("p");

    customer.innerHTML =
        `<strong>Client :</strong> ${data.customer}`;

    response.appendChild(customer);


    const email = document.createElement("p");

    email.innerHTML =
        `<strong>Email :</strong> ${data.email}`;

    response.appendChild(email);


    const total = document.createElement("p");

    total.innerHTML =
        `<strong>Total :</strong> ${data.total} €`;

    response.appendChild(total);


    const action = document.createElement("p");

    action.innerHTML =
        `<strong>Action :</strong> ${data.action}`;

    response.appendChild(action);


    const reason = document.createElement("p");

    reason.innerHTML =
        `<strong>Raison :</strong> ${data.reason}`;

    response.appendChild(reason);
}

// ---------------------------------------------------------
// Envoi du message
// ---------------------------------------------------------
form.addEventListener("submit", async function (event) {

    event.preventDefault();

    //const message = document.getElementById("message").value;
    const message = messageInput.value.trim();

    if (!message) {
        return;
    }

    // Afficher immédiatement le message de l'utilisateur
    addMessage("user", message);

    // Vider le champ
    messageInput.value = "";
    // Désactiver le formulaire pendant l'appel
    submitButton.disabled = true;
    messageInput.disabled = true;

    // Construire la requête
    const order = {
        text: message
    };


    // Si une conversation existe déjà,
    // on la transmet au backend.
    if (conversationId !== null) {
        order.conversation_id = conversationId;
    }


    try {
        // on affiche le visuel d'attente
        showTypingIndicator();

        const result = await fetch(
            "http://localhost:8000/orders",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(order)
            }
        );


        if (!result.ok) {

            let errorMessage =
                "Erreur lors du traitement de la commande.";

            try {

                const errorData = await result.json();

                if (errorData.detail) {
                    errorMessage = errorData.detail;
                }

            } catch (error) {
                // La réponse n'était pas du JSON.
            }

            throw new Error(errorMessage);
        }


        const data = await result.json();


        // -------------------------------------------------
        // IMPORTANT :
        // conserver l'identifiant de conversation
        // -------------------------------------------------

        if (data.conversation_id) {
            conversationId = data.conversation_id;
        }


        // -------------------------------------------------
        // NEED_INFORMATION
        // -------------------------------------------------

        if (data.status === "NEED_INFORMATION") {

            addMessage(
                "assistant",
                data.message
            );

            return;
        }


        // -------------------------------------------------
        // Commande finale
        // -------------------------------------------------

        if (
            data.status === "accepted" ||
            data.status === "rejected"
        ) {

            addMessage(
                "assistant",
                data.message || "Commande traitée."
            );

            displayOrder(data);

            return;
        }


        // -------------------------------------------------
        // Statut inattendu
        // -------------------------------------------------

        addMessage(
            "assistant",
            "Réponse inattendue du serveur."
        );

        console.error(
            "Réponse inattendue :",
            data
        );

    } catch (error) {

        addMessage(
            "assistant",
            `Une erreur est survenue : ${error.message}`
        );

    } finally {

        submitButton.disabled = false;
        messageInput.disabled = false;

        // on cache le visuel d'attente
        hideTypingIndicator();
        // on remet le focus sur la zone de texte
        messageInput.focus();
    }

    /* init
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
    }*/
});

/* Gère l'affichage d'un visuel d'attente*/
function showTypingIndicator() {
    typingIndicator.hidden = false;
    submitButton.disabled = true;
    messageInput.disabled = true;
}


function hideTypingIndicator() {
    typingIndicator.hidden = true;
    submitButton.disabled = false;
    messageInput.disabled = false;
}