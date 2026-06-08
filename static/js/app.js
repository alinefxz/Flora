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
});