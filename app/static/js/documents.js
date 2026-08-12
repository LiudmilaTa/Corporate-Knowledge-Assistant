const documentsList = document.getElementById("documents-list");
const uploadForm = document.getElementById("upload-form");
const fileInput = document.getElementById("file");
const fileName = document.getElementById("file-name");
const uploadResult = document.getElementById("upload-result");

function createChunkCard(chunk) {
    const card = document.createElement("div");
    card.className = "chunk-card";

    const title = document.createElement("strong");
    title.textContent = `Chunk ${chunk.chunk_id}`;

    const page = document.createElement("span");
    page.textContent = `Page ${chunk.page ?? "—"}`;

    const content = document.createElement("p");
    content.textContent = chunk.content ?? "";

    card.append(title, page, content);
    return card;
}

function createDocumentCard(filename, chunks) {
    const card = document.createElement("div");
    card.className = "document-card";

    const header = document.createElement("div");
    header.className = "document-header";

    const title = document.createElement("h3");
    title.textContent = filename;

    const meta = document.createElement("p");
    meta.className = "document-meta";
    meta.textContent = `${chunks.length} chunk${chunks.length !== 1 ? "s" : ""}`;

    header.append(title, meta);

    const actions = document.createElement("div");
    actions.className = "document-actions";

    const viewButton = document.createElement("button");
    viewButton.type = "button";
    viewButton.textContent = "View";
    viewButton.className = "secondary-action";

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.textContent = "Delete";
    deleteButton.className = "danger-action";

    const chunksContainer = document.createElement("div");
    chunksContainer.className = "chunks-container";
    chunksContainer.style.display = "none";

    chunks.forEach((chunk) => {
        chunksContainer.appendChild(createChunkCard(chunk));
    });

    viewButton.addEventListener("click", () => {
        const isHidden = chunksContainer.style.display === "none";
        chunksContainer.style.display = isHidden ? "block" : "none";
        viewButton.textContent = isHidden ? "Hide" : "View";
    });

    deleteButton.addEventListener("click", () => {
        const confirmation = document.createElement("div");
        confirmation.className = "delete-confirmation";

        const message = document.createElement("p");
        message.textContent = `Delete "${filename}"?`;

        const buttons = document.createElement("div");
        buttons.className = "delete-confirmation-buttons";

        const confirmButton = document.createElement("button");
        confirmButton.type = "button";
        confirmButton.textContent = "Yes";
        confirmButton.className = "danger-action confirm-delete";

        const cancelButton = document.createElement("button");
        cancelButton.type = "button";
        cancelButton.textContent = "Cancel";
        cancelButton.className = "secondary-action cancel-delete";

        confirmButton.addEventListener("click", async () => {
            try {
                const response = await fetch(`/documents/${encodeURIComponent(filename)}`, {method: "DELETE"});
                if (!response.ok) {
                    throw new Error(`Failed to delete document ${filename}`);
                }

                card.classList.add("removing");
                setTimeout(() => {
                    card.remove();
                    if (documentsList.children.length === 0) {
                        documentsList.innerHTML = '<p class="empty">No documents uploaded yet.</p>';
                    }

                    const toast = document.createElement("div");
                    toast.className = "delete-toast";
                    toast.textContent = `Document "${filename}" deleted.`;
                    documentsList.appendChild(toast);
                }, 180);
            } catch (error) {
                console.error(error);
                confirmation.innerHTML = '<p>Failed to delete document.</p>';
            }
        });

        cancelButton.addEventListener("click", () => {
            confirmation.remove();
        });

        buttons.append(confirmButton, cancelButton);
        confirmation.append(message, buttons);
        card.appendChild(confirmation);
    });

    actions.append(viewButton, deleteButton);
    card.append(header, actions, chunksContainer);
    return card;
}

async function loadDocuments() {
    documentsList.innerHTML = "Loading documents...";

    try {
        const response = await fetch("/documents");
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const documents = await response.json();
        documentsList.innerHTML = "";

        if (documents.length === 0) {
            documentsList.innerHTML = '<p class="empty">No documents uploaded yet.</p>';
            return;
        }

        const groupedDocuments = {};
        documents.forEach((doc) => {
            if (!groupedDocuments[doc.filename]) {
                groupedDocuments[doc.filename] = [];
            }
            groupedDocuments[doc.filename].push(doc);
        });

        Object.entries(groupedDocuments).forEach(([filename, chunks]) => {
            documentsList.appendChild(createDocumentCard(filename, chunks));
        });
    } catch (error) {
        console.error(error);
        documentsList.innerHTML = '<p class="error">Failed to load documents.</p>';
    }
}

fileInput.addEventListener("change", () => {
    const selectedFile = fileInput.files[0];
    fileName.textContent = selectedFile ? selectedFile.name : "No file selected";
});

uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const file = fileInput.files[0];
    if (!file) {
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    uploadResult.textContent = "Uploading...";

    try {
        const response = await fetch("/upload", {method: "POST", body: formData});
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const data = await response.json();
        uploadResult.textContent = `Uploaded ${data.filename} (${data.chunks} chunks).`;
        fileInput.value = "";
        fileName.textContent = "No file selected";
        await loadDocuments();
    } catch (error) {
        console.error(error);
        uploadResult.textContent = "Failed to upload document.";
    }
});

loadDocuments();
