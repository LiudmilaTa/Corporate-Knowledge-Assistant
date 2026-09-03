const documentsList = document.getElementById("documents-list");
const uploadForm = document.getElementById("upload-form");
const fileInput = document.getElementById("file");
const fileName = document.getElementById("file-name");
const uploadResult = document.getElementById("upload-result");
const refreshDocumentsButton = document.getElementById("refresh-documents");

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

    const cardActions = document.createElement("div");
    cardActions.className = "card-actions";

    const viewButton = document.createElement("button");
    viewButton.type = "button";
    viewButton.textContent = "👁";
    viewButton.setAttribute("aria-label", "View chunks");
    viewButton.title = "View chunks";
    viewButton.className = "card-icon-action";

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.textContent = "🗑";
    deleteButton.setAttribute("aria-label", "Delete document");
    deleteButton.title = "Delete document";
    deleteButton.className = "card-icon-action document-delete";

    cardActions.append(viewButton, deleteButton);

    const header = document.createElement("div");
    header.className = "document-header";

    const title = document.createElement("h3");
    title.textContent = filename;

    const meta = document.createElement("p");
    meta.className = "document-meta";
    meta.textContent = `${chunks.length} chunk${chunks.length !== 1 ? "s" : ""}`;

    header.append(title, meta);

    const chunksContainer = document.createElement("div");
    chunksContainer.className = "chunks-container";
    chunksContainer.style.display = "none";

    chunks.forEach((chunk) => {
        chunksContainer.appendChild(createChunkCard(chunk));
    });

    viewButton.addEventListener("click", () => {
        const isHidden = chunksContainer.style.display === "none";
        chunksContainer.style.display = isHidden ? "block" : "none";
        viewButton.textContent = isHidden ? "🙈" : "👁";
        viewButton.title = isHidden ? "Hide chunks" : "View chunks";
    });

    deleteButton.addEventListener("click", () => {
        showDeleteConfirmModal({
            title: "Delete document",
            message: `"${filename}" and all its chunks will be permanently deleted. This action cannot be undone.`,
            onConfirm: async () => {
                try {
                    const response = await fetch(`/documents/${encodeURIComponent(filename)}`, {method: "DELETE"});
                    if (!response.ok) {
                        const body = await response.json().catch(() => null);
                        throw new Error(body?.detail || `Failed to delete document (HTTP ${response.status})`);
                    }

                    card.classList.add("removing");
                    setTimeout(() => {
                        card.remove();
                        if (documentsList.children.length === 0) {
                            documentsList.innerHTML = '<p class="empty">No documents uploaded yet.</p>';
                        }

                        showToast(`Document "${filename}" deleted.`, "success");
                    }, 180);
                } catch (error) {
                    console.error(error);
                    showToast(`Failed to delete "${filename}": ${error.message}`, "error");
                }
            },
        });
    });

    card.append(cardActions, header, chunksContainer);
    return card;
}

function showToast(text, variant) {
    const toast = document.createElement("div");
    toast.className = variant === "error" ? "delete-toast error" : "delete-toast";
    toast.textContent = text;
    toast.addEventListener("animationend", () => toast.remove());
    documentsList.appendChild(toast);
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
refreshDocumentsButton.addEventListener("click", loadDocuments);
