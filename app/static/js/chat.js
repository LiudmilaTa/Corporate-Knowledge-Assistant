const form = document.getElementById("ask-form");
const button = document.getElementById("ask-button");
const loading = document.getElementById("loading");
const answer = document.getElementById("answer");
const sources = document.getElementById("sources");
const historyContainer = document.getElementById("chat-history");
const refreshHistoryButton = document.getElementById("refresh-history");
const documentFilter = document.getElementById("document-filter");

async function loadDocumentFilter() {
    try {
        const response = await fetch("/documents");
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const documents = await response.json();
        const filenames = [...new Set(documents.map((document) => document.filename).filter(Boolean))];
        filenames.forEach((filename) => {
            const option = document.createElement("option");
            option.value = filename;
            option.textContent = filename;
            documentFilter.appendChild(option);
        });
    } catch (error) {
        console.error("Failed to load document list", error);
    }
}

function setLoadingState(isLoading) {
    loading.style.display = isLoading ? "flex" : "none";
    button.disabled = isLoading;
    button.textContent = isLoading ? "Thinking..." : "Ask";
}

function renderSources(sourceList) {
    if (!sourceList || sourceList.length === 0) {
        return null;
    }

    const container = document.createElement("div");
    container.className = "history-sources";

    const title = document.createElement("strong");
    title.textContent = "Sources";
    container.appendChild(title);

    sourceList.forEach((source) => {
        const sourceCard = document.createElement("div");
        sourceCard.className = "history-source-card";

        const filename = document.createElement("div");
        filename.textContent = source.filename;

        const page = document.createElement("div");
        page.textContent = `Page: ${source.page}`;

        sourceCard.append(filename, page);

        if (source.excerpt) {
            const excerpt = document.createElement("p");
            excerpt.className = "source-excerpt";
            excerpt.textContent = `"${source.excerpt}"`;
            sourceCard.appendChild(excerpt);
        }

        container.appendChild(sourceCard);
    });

    return container;
}

function renderHistoryCard(message) {
    const card = document.createElement("div");
    card.className = "history-card";

    const question = document.createElement("div");
    question.className = "history-question";
    question.innerHTML = "<strong>Question</strong><p></p>";
    question.querySelector("p").textContent = message.question;

    const answerBlock = document.createElement("div");
    answerBlock.className = "history-answer";
    answerBlock.innerHTML = "<strong>Answer</strong><p></p>";
    answerBlock.querySelector("p").textContent = message.answer;

    const sourcesBlock = renderSources(message.sources);
    const date = document.createElement("div");
    date.className = "history-date";
    date.textContent = new Date(message.created_at).toLocaleString();

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.textContent = "🗑";
    deleteButton.setAttribute("aria-label", "Delete message");
    deleteButton.title = "Delete message";
    deleteButton.className = "history-delete";

    const deleteMessage = async () => {
        deleteButton.disabled = true;
        try {
            const response = await fetch(`/chats/${message.id}`, {method: "DELETE"});
            if (!response.ok) {
                throw new Error(`Failed to delete chat message ${message.id}`);
            }
            card.remove();
        } catch (error) {
            console.error(error);
            deleteButton.disabled = false;
        }
    };

    deleteButton.addEventListener("click", () => {
        showDeleteConfirmModal({
            title: "Delete message",
            message: "This message will be permanently deleted. This action cannot be undone.",
            onConfirm: deleteMessage,
        });
    });

    card.append(question, answerBlock);
    if (sourcesBlock) {
        card.appendChild(sourcesBlock);
    }
    card.append(date, deleteButton);

    return card;
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const input = document.querySelector("input[name='question']");
    setLoadingState(true);
    answer.innerHTML = "";
    sources.innerHTML = "";

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({question: input.value, filename: documentFilter.value || null}),
        });
        const data = await response.json();

        answer.textContent = data.answer ?? "";
        data.sources.forEach((source) => {
            const card = document.createElement("div");
            card.className = "source-card";
            const title = document.createElement("strong");
            title.textContent = source.filename;
            card.append(title, document.createElement("br"), `Page: ${source.page}`);
                        
            if (source.excerpt) {
                const excerpt = document.createElement("p");
                excerpt.className = "source-excerpt";
                excerpt.textContent = `"${source.excerpt}"`;
                card.appendChild(excerpt);
            }
            
            sources.appendChild(card);
        });
    } catch (error) {
        answer.textContent = "Database is not available. Start PostgreSQL and try again.";
        console.error(error);
    } finally {
        setLoadingState(false);
    }
});

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
            historyContainer.innerHTML = '<p class="empty">No conversations yet.</p>';
            return;
        }

        messages.forEach((message) => {
            historyContainer.appendChild(renderHistoryCard(message));
        });
    } catch (error) {
        console.error(error);
        historyContainer.innerHTML = '<p class="error">Failed to load chat history.</p>';
    }
}

refreshHistoryButton.addEventListener("click", loadChatHistory);
loadDocumentFilter();
loadChatHistory();
