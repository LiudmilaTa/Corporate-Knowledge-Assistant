function showDeleteConfirmModal({title = "Delete", message, onConfirm}) {
    const overlay = document.createElement("div");
    overlay.className = "modal-overlay";

    const modal = document.createElement("div");
    modal.className = "modal-box";

    const titleEl = document.createElement("h3");
    titleEl.textContent = title;

    const text = document.createElement("p");
    text.textContent = message;

    const buttons = document.createElement("div");
    buttons.className = "modal-buttons";

    const confirmButton = document.createElement("button");
    confirmButton.type = "button";
    confirmButton.textContent = "Delete";
    confirmButton.className = "danger-action";

    const cancelButton = document.createElement("button");
    cancelButton.type = "button";
    cancelButton.textContent = "Cancel";
    cancelButton.className = "secondary-action";

    const closeModal = () => overlay.remove();

    confirmButton.addEventListener("click", () => {
        closeModal();
        onConfirm();
    });
    cancelButton.addEventListener("click", closeModal);
    overlay.addEventListener("click", (event) => {
        if (event.target === overlay) {
            closeModal();
        }
    });

    buttons.append(cancelButton, confirmButton);
    modal.append(titleEl, text, buttons);
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
}
