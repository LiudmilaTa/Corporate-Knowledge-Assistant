const form = document.getElementById("ask-form");
const button = document.getElementById("ask-button");
const loading = document.getElementById("loading");
const answer = document.getElementById("answer");
const sources = document.getElementById("sources");

form.addEventListener("submit", async function(e) {
    e.preventDefault();

    const input = document.querySelector(
        "input[name='question']"
    );

    button.disabled = true;
    button.innerHTML = "Thinking...";

    loading.style.display = "flex";

    answer.innerHTML = "";
    sources.innerHTML = "";

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {"Content-Type": "application/json" },
            body: JSON.stringify({
                question: input.value
            })
        });

        const data = await response.json();

        answer.textContent = data.answer ?? "";

        data.sources.forEach(source => {
            const card = document.createElement("div");
            card.className = "source-card";
            const title = document.createElement("strong");
            title.textContent = source.filename;
            card.append(title, document.createElement("br"), `Page: ${source.page}`);
            sources.appendChild(card);
        });

    } catch(error) {
        answer.innerHTML =
            "Error while processing request";
        console.error(error);
    }
    loading.style.display = "none";
    button.disabled = false;
    button.innerHTML = "Ask";

});

const historyContainer = document.getElementById("chat-history");
const refreshHistoryButton =
document.getElementById("refresh-history");

async function loadChatHistory() {
historyContainer.innerHTML = "Loading chat history...";

try {
    const response = await fetch("/chats");

    if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
    }

    const messages = await response.json();

    historyContainer.innerHTML = "";

    if (messages.length === 0) {
        historyContainer.innerHTML = `
            <p class="empty">
                No conversations yet.
            </p>
        `;
        return;
    }

    messages.forEach(message => {
        const card = document.createElement("div");
        card.className = "history-card";

        const question = document.createElement("div");
        question.className = "history-question";

        question.innerHTML = `
            <strong>Question</strong>
            <p></p>
        `;

        question.querySelector("p").textContent =
            message.question;

        const answer = document.createElement("div");
        answer.className = "history-answer";
        answer.textContent = message.answer;
        card.appendChild(question);
        card.appendChild(answer);

        const sources = renderSources(message.sources);

        if (sources) {
        card.appendChild(sources);
        }
        answer.innerHTML = `
            <strong>Answer</strong>
            <p></p>
        `;

        answer.querySelector("p").textContent =
            message.answer;

        const date = document.createElement("div");
        date.className = "history-date";

        date.textContent = new Date(
            message.created_at
        ).toLocaleString();

        card.appendChild(question);
        card.appendChild(answer);
        card.appendChild(date);

        historyContainer.appendChild(card);
    });

} catch (error) {
    console.error(error);

    historyContainer.innerHTML = `
        <p class="error">
            Failed to load chat history.
        </p>
    `;
}

}

function renderSources(sources) {
if (!sources || sources.length === 0) {
return null;
}

const container = document.createElement("div");
container.className = "history-sources";

const title = document.createElement("strong");
title.textContent = "Sources";
container.appendChild(title);

sources.forEach(source => {
    const sourceCard = document.createElement("div");
    sourceCard.className = "history-source-card";

    const filename = document.createElement("div");
    filename.textContent = source.filename;

    const page = document.createElement("div");
    page.textContent = `Page: ${source.page}`;

    sourceCard.appendChild(filename);
    sourceCard.appendChild(page);

    container.appendChild(sourceCard);
});

return container;

}

refreshHistoryButton.addEventListener(
"click",
loadChatHistory
);

loadChatHistory();