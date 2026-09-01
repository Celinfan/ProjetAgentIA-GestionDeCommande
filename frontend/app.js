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
    label.textContent = role === "user"
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
    response.replaceChildren();

    const title = document.createElement("h3");
    title.textContent = "Commande traitée";
    response.appendChild(title);

    appendOrderField("Statut", data.status);
    appendOrderField("Client", data.customer);
    appendOrderField("Email", data.email);
    appendOrderField("Total", data.total);
    appendOrderField("Action", data.action);
    appendOrderField("Raison", data.reason);   
}


// ---------------------------------------------
// Ajoute une information à la commande finale
// ---------------------------------------------
function appendOrderField(label, value) {
    const element  = document.createElement("p");

    const strong = document.createElement("strong");
    strong.textContent = `${label} : `;

    element.appendChild(strong);
    element.appendChild(document.createTextNode(value));

    response.appendChild(element);
}

// ---------------------------------------------------------
// Envoi du message
// ---------------------------------------------------------
form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const message = messageInput.value.trim();

    if (!message) {
        return;
    }

    // Afficher immédiatement le message de l'utilisateur
    addMessage("user", message);

    // Vider le champ
    messageInput.value = "";
    // Désactiver le formulaire pendant l'appel
    setFormDisabled(true);

    // on affiche le visuel d'attente
    showTypingIndicator();

    // Construire la requête
    const order = {
        text: message
    };


    // Si une conversation existe déjà, on la transmet au backend.
    if (conversationId !== null) {
        order.conversation_id = conversationId;
    }

    try {
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

            } catch {
                // La réponse n'était pas du JSON.
            }

            throw new Error(errorMessage);
        }


        const data = await result.json();

        // IMPORTANT : conserver l'identifiant de conversation
        if (data.conversation_id) {
            conversationId = data.conversation_id;
        }

        // NEED_INFORMATION
        if (data.status === "NEED_INFORMATION") {
            addMessage("assistant", data.message);
            return;
        }

        // Commande finale
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

        // Statut inattendu
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
        // on cache le visuel d'attente
        hideTypingIndicator();
        // on réactive le formulaire
        setFormDisabled(false);
        // on remet le focus sur la zone de texte
        messageInput.focus();
    }
});

// Active/Désactive le formulaire 
function setFormDisabled(disabled) {
    submitButton.disabled = disabled;
    messageInput.disabled = disabled;
}

/* Gère l'affichage d'un visuel d'attente*/
function showTypingIndicator() {
    typingIndicator.hidden = false;
}
function hideTypingIndicator() {
    typingIndicator.hidden = true;
}