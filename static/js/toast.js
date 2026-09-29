let toastDisplayTimer;
let toastHideTimer;

function showToast(title, message, type = "normal", duration = 3000) {
    const toastComponent = document.getElementById("toast-component");
    const toastTitle = document.getElementById("toast-title");
    const toastMessage = document.getElementById("toast-message");

    if (!toastComponent || !toastTitle || !toastMessage) return;

    clearTimeout(toastDisplayTimer);
    clearTimeout(toastHideTimer);

    toastTitle.textContent = title;
    toastMessage.textContent = message;

    toastComponent.classList.remove("toast-success", "toast-error", "toast-normal");
    toastComponent.classList.add(
        type === "success" ? "toast-success" : type === "error" ? "toast-error" : "toast-normal"
    );
    toastComponent.setAttribute("role", type === "error" ? "alert" : "status");
    toastComponent.setAttribute("aria-live", type === "error" ? "assertive" : "polite");

    if (!toastComponent.matches(":popover-open")) {
        toastComponent.showPopover();
    }
    // Establish the hidden state before starting the entrance transition.
    if (!toastComponent.classList.contains("toast-visible")) {
        void toastComponent.offsetWidth;
    }
    toastComponent.classList.add("toast-visible");

    toastDisplayTimer = setTimeout(() => {
        toastComponent.classList.remove("toast-visible");
        toastHideTimer = setTimeout(() => {
            if (toastComponent.matches(":popover-open")) {
                toastComponent.hidePopover();
            }
        }, 250);
    }, duration);
}
