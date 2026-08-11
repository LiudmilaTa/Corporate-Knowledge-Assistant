const documentsList = document.getElementById("documents-list");
const uploadForm = document.getElementById("upload-form");
const fileInput = document.getElementById("file");
const uploadResult = document.getElementById("upload-result");

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
        documentsList.innerHTML = `
            <p class="empty">
                No documents uploaded yet.
            </p>
        `;
        return;
    }

    // Group chunks by filename
    const groupedDocuments = {};

    documents.forEach(doc => {
        if (!groupedDocuments[doc.filename]) {
            groupedDocuments[doc.filename] = [];
        }

        groupedDocuments[doc.filename].push(doc);
    });

    Object.entries(groupedDocuments).forEach(
        ([filename, chunks]) => {
            const card = document.createElement("div");
            card.className = "document-card";

            const header = document.createElement("div");
            header.className = "document-header";

            const title = document.createElement("h3");
            title.textContent = filename;

            const meta = document.createElement("p");
            meta.className = "document-meta";
            meta.textContent =
                `${chunks.length} chunk${chunks.length !== 1 ? "s" : ""}`;

            header.appendChild(title);
            header.appendChild(meta);

            const actions = document.createElement("div");
            actions.className = "document-actions";

            const viewButton = document.createElement("button");
            viewButton.type = "button";
            viewButton.textContent = "View";

            const deleteButton = document.createElement("button");
            deleteButton.type = "button";
            deleteButton.textContent = "Delete";
            deleteButton.className = "delete-button";

            const chunksContainer =
                document.createElement("div");

            chunksContainer.className = "chunks-container";
            chunksContainer.style.display = "none";

            chunks.forEach(chunk => {
                const chunkCard = document.createElement("div");
                chunkCard.className = "chunk-card";

                const chunkTitle =
                    document.createElement("strong");

                chunkTitle.textContent =
                    `Chunk ${chunk.chunk_id}`;

                const page =
                    document.createElement("span");

                page.textContent =
                    `Page ${chunk.page ?? "—"}`;

                const content =
                    document.createElement("p");

                content.textContent =
                    chunk.content ?? "";

                chunkCard.appendChild(chunkTitle);
                chunkCard.appendChild(page);
                chunkCard.appendChild(content);

                chunksContainer.appendChild(chunkCard);
            });

            viewButton.addEventListener("click", () => {
                const isHidden =
                    chunksContainer.style.display === "none";

                chunksContainer.style.display =
                    isHidden ? "block" : "none";

                viewButton.textContent =
                    isHidden ? "Hide" : "View";
            });

            deleteButton.addEventListener("click", async () => {
                const confirmed = confirm(
                    `Delete "${filename}"?`
                );

                if (!confirmed) {
                    return;
                }

                try {
                    // Delete all chunks belonging to this document
                    for (const chunk of chunks) {
                        const response = await fetch(
                            `/documents/${chunk.id}`,
                            {
                                method: "DELETE",
                            }
                        );

                        if (!response.ok) {
                            throw new Error(
                                `Failed to delete chunk ${chunk.id}`
                            );
                        }
                    }

                    await loadDocuments();

                } catch (error) {
                    console.error(error);

                    alert(
                        "Failed to delete document."
                    );
                }
            });

            actions.appendChild(viewButton);
            actions.appendChild(deleteButton);

            card.appendChild(header);
            card.appendChild(actions);
            card.appendChild(chunksContainer);

            documentsList.appendChild(card);
        }
    );

} catch (error) {
    console.error(error);

    documentsList.innerHTML = `
        <p class="error">
            Failed to load documents.
        </p>
    `;
}

}

uploadForm.addEventListener("submit", async function (event) {
event.preventDefault();

const file = fileInput.files[0];

if (!file) {
    return;
}

const formData = new FormData();
formData.append("file", file);

uploadResult.textContent = "Uploading...";

try {
    const response = await fetch("/upload", {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
    }

    const data = await response.json();

    uploadResult.textContent =
        `Uploaded ${data.filename} (${data.chunks} chunks).`;

    fileInput.value = "";

    await loadDocuments();

} catch (error) {
    console.error(error);

    uploadResult.textContent =
        "Failed to upload document.";
}

});

loadDocuments();