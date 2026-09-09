document.addEventListener("DOMContentLoaded", () => {
    // Mobile nav toggle
    const navToggle = document.getElementById("nav-toggle");
    const navLinks = document.getElementById("nav-links");

    if (navToggle && navLinks) {
        navToggle.addEventListener("click", () => {
            const isOpen = navLinks.classList.toggle("is-open");
            navToggle.setAttribute("aria-expanded", String(isOpen));
        });
    }

    // Dismissible flash messages
    document.querySelectorAll(".alert-dismiss").forEach((btn) => {
        btn.addEventListener("click", () => {
            const alert = btn.closest(".alert");
            if (alert) alert.remove();
        });
    });

    // Confirm before destructive actions (e.g. deleting an application)
    document.querySelectorAll("form[data-confirm]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            const message = form.getAttribute("data-confirm");
            if (message && !window.confirm(message)) {
                event.preventDefault();
            }
        });
    });
});
