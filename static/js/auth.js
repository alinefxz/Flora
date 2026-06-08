document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const switchLinks = document.querySelectorAll("[data-auth-switch]");

    switchLinks.forEach(link => {
        link.addEventListener("click", event => {
            if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
                return;
            }

            event.preventDefault();
            body.classList.add("auth-is-switching");

            window.setTimeout(() => {
                window.location.href = link.href;
            }, 620);
        });
    });

    document.querySelectorAll(".input-password").forEach(wrapper => {
        const input = wrapper.querySelector('input[type="password"]');
        if (!input) return;

        const button = document.createElement("button");
        button.type = "button";
        button.className = "password-toggle";
        button.textContent = "Mostrar";
        button.setAttribute("aria-label", "Mostrar senha");

        button.addEventListener("click", () => {
            const showing = input.type === "text";
            input.type = showing ? "password" : "text";
            button.textContent = showing ? "Mostrar" : "Ocultar";
            button.setAttribute(
                "aria-label",
                showing ? "Mostrar senha" : "Ocultar senha"
            );
        });

        wrapper.appendChild(button);
    });
});
