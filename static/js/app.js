document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const drawer = document.querySelector(".drawer");
    const openButton = document.querySelector("[data-menu-open]");
    const closeButtons = document.querySelectorAll("[data-menu-close]");

    function openMenu() {
        body.classList.add("menu-open");
        drawer?.setAttribute("aria-hidden", "false");
    }

    function closeMenu() {
        body.classList.remove("menu-open");
        drawer?.setAttribute("aria-hidden", "true");
    }

    openButton?.addEventListener("click", openMenu);
    closeButtons.forEach(button => {
        button.addEventListener("click", closeMenu);
    });

    document.addEventListener("keydown", event => {
        if (event.key === "Escape") closeMenu();
    });

    document.querySelectorAll("[data-nav-link]").forEach(link => {
        const linkPath = new URL(link.href).pathname;
        const currentPath = window.location.pathname;
        const isRoot = linkPath === "/";
        const active = isRoot
            ? currentPath === "/"
            : currentPath === linkPath || currentPath.startsWith(linkPath);

        if (active) link.classList.add("is-active");
    });

    document.querySelectorAll("[data-like-form]").forEach(form => {
        form.addEventListener("submit", async event => {
            event.preventDefault();

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    body: new FormData(form),
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                });

                if (!response.ok) throw new Error("Falha ao curtir");

                const data = await response.json();
                const button = form.querySelector("button");
                const count = form.querySelector("[data-like-count]");

                button?.classList.toggle("is-liked", data.curtido);
                button?.setAttribute("aria-pressed", String(data.curtido));
                if (count) count.textContent = data.total;
            } catch {
                form.submit();
            }
        });
    });

    const avatarInput = document.querySelector(
        'input[type="file"][name="foto_perfil"]'
    );
    const avatarPreview = document.querySelector("[data-avatar-preview]");

    avatarInput?.addEventListener("change", () => {
        const file = avatarInput.files?.[0];
        if (!file || !avatarPreview) return;

        let image = avatarPreview.querySelector("img");
        if (!image) {
            image = document.createElement("img");
            avatarPreview.textContent = "";
            avatarPreview.appendChild(image);
        }

        image.src = URL.createObjectURL(file);
        image.alt = "Prévia da nova foto de perfil";
    });
});
