const chatbox = document.getElementById("chatbox");
const messageInput = document.getElementById("message");
const sendBtn = document.getElementById("sendBtn");

// -------------------------
// Add Message
// -------------------------

function addMessage(sender, text, type, emotion = "", risk = "") {

    const messageDiv = document.createElement("div");
    messageDiv.className = `${type}-message`;

    const title = document.createElement("strong");
    title.textContent = sender;

    const message = document.createElement("p");
    message.textContent = text;

    messageDiv.appendChild(title);
    messageDiv.appendChild(message);

    if (emotion && risk) {

        const info = document.createElement("small");

        info.innerHTML = `
            😊 Emotion: <b>${emotion}</b>
            &nbsp;&nbsp;&nbsp;
            ⚠️ Risk: <b>${risk}</b>
        `;

        messageDiv.appendChild(info);

    }

    chatbox.appendChild(messageDiv);

    chatbox.scrollTop = chatbox.scrollHeight;
}

// -------------------------
// Typing Indicator
// -------------------------

function showTyping() {

    const typing = document.createElement("div");

    typing.className = "bot-message";

    typing.id = "typing";

    typing.innerHTML = `
        <strong>🤖 MindCare AI</strong>
        <p>Typing...</p>
    `;

    chatbox.appendChild(typing);

    chatbox.scrollTop = chatbox.scrollHeight;

}

function removeTyping() {

    const typing = document.getElementById("typing");

    if (typing) typing.remove();

}

// -------------------------
// Send Message
// -------------------------

async function sendMessage() {

    const message = messageInput.value.trim();

    if (!message) return;

    addMessage("🧑 You", message, "user");

    messageInput.value = "";

    sendBtn.disabled = true;
    messageInput.disabled = true;

    showTyping();

    try {

        const controller = new AbortController();

        const timeout = setTimeout(() => {

            controller.abort();

        }, 10000);

        const response = await fetch("/chat", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                message: message

            }),

            signal: controller.signal

        });

        clearTimeout(timeout);

        if (!response.ok) {

            throw new Error("Server Error");

        }

        const data = await response.json();

        removeTyping();

        addMessage(

            "🤖 MindCare AI",

            data.response,

            "bot",

            data.emotion,

            data.risk

        );

    }

    catch (error) {

        removeTyping();

        if (error.name === "AbortError") {

            addMessage(

                "⚠️ Error",

                "Server took too long to respond.",

                "bot"

            );

        }

        else {

            addMessage(

                "⚠️ Error",

                "Unable to connect to the server. Please try again.",

                "bot"

            );

        }

        console.error(error);

    }

    finally {

        sendBtn.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();

        chatbox.scrollTop = chatbox.scrollHeight;

    }

}

// -------------------------
// Events
// -------------------------

sendBtn.addEventListener("click", sendMessage);
function quickMessage(text) {

    messageInput.value = text;

    sendMessage();

}

messageInput.addEventListener("keydown", function (e) {

    if (e.key === "Enter") {

        e.preventDefault();

        if (!sendBtn.disabled) {

            sendMessage();

        }

    }
});