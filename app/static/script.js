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

/*
const uploadForm = document.getElementById("upload-form");

if (uploadForm) {
    uploadForm.addEventListener("submit", async function(e) {
        e.preventDefault();
        const file = document.getElementById("file").files[0];
        if (!file) { return; }

        const formData = new FormData();
        formData.append(
            "file",
            file
        );

        const response = await fetch(
            "/upload",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        document.getElementById(
            "upload-result"
        ).innerText =
            `Uploaded ${data.filename}. Chunks: ${data.chunks}`;
    });
}*/