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

                const contentType = response.headers.get("content-type") || "";

            if (!contentType.includes("application/json")) {
                throw new Error("Resposta inválida do servidor.");
            }

const data = await response.json();
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


document.addEventListener("DOMContentLoaded", () => {
    const hero = document.querySelector("[data-profile-hero]");
    const savedImage = document.querySelector(
        "[data-profile-palette-source]"
    );
    const photoInput = document.querySelector(
        'input[type="file"][name="foto_perfil"]'
    );
    const avatarPreview = document.querySelector(
        "[data-avatar-preview]"
    );

    function rgbToHsl(red, green, blue) {
        const r = red / 255;
        const g = green / 255;
        const b = blue / 255;

        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);

        let hue = 0;
        let saturation = 0;
        const lightness = (max + min) / 2;

        if (max !== min) {
            const difference = max - min;

            saturation = lightness > .5
                ? difference / (2 - max - min)
                : difference / (max + min);

            if (max === r) {
                hue = (
                    (g - b) / difference
                    + (g < b ? 6 : 0)
                );
            }

            if (max === g) {
                hue = (b - r) / difference + 2;
            }

            if (max === b) {
                hue = (r - g) / difference + 4;
            }

            hue /= 6;
        }

        return [
            Math.round(hue * 360),
            saturation * 100,
            lightness * 100,
        ];
    }

    function extractPalette(image) {
        if (!hero || !image) {
            return;
        }

        const canvas = document.createElement("canvas");
        const context = canvas.getContext(
            "2d",
            { willReadFrequently: true }
        );

        if (!context) {
            return;
        }

        canvas.width = 42;
        canvas.height = 42;

        try {
            context.drawImage(
                image,
                0,
                0,
                canvas.width,
                canvas.height
            );

            const pixels = context.getImageData(
                0,
                0,
                canvas.width,
                canvas.height
            ).data;

            let red = 0;
            let green = 0;
            let blue = 0;
            let totalWeight = 0;

            for (
                let index = 0;
                index < pixels.length;
                index += 4
            ) {
                const alpha = pixels[index + 3];

                if (alpha < 180) {
                    continue;
                }

                const r = pixels[index];
                const g = pixels[index + 1];
                const b = pixels[index + 2];

                const brightest = Math.max(r, g, b);
                const darkest = Math.min(r, g, b);

                // Ignora fundos quase brancos.
                if (
                    brightest > 242
                    && darkest > 232
                ) {
                    continue;
                }

                const colorWeight = Math.max(
                    brightest - darkest,
                    18
                );

                red += r * colorWeight;
                green += g * colorWeight;
                blue += b * colorWeight;
                totalWeight += colorWeight;
            }

            if (!totalWeight) {
                return;
            }

            const [hue, saturation] = rgbToHsl(
                red / totalWeight,
                green / totalWeight,
                blue / totalWeight
            );

            const vivid = Math.max(
                34,
                Math.min(72, saturation)
            );

            hero.style.setProperty(
                "--profile-color-1",
                `hsl(${hue} ${vivid}% 25%)`
            );

            hero.style.setProperty(
                "--profile-color-2",
                (
                    `hsl(${(hue + 18) % 360} `
                    + `${Math.max(28, vivid - 8)}% 47%)`
                )
            );

            hero.classList.add("has-photo-palette");
        } catch {
            hero.classList.remove("has-photo-palette");
        }
    }

    function applyPalette(image) {
        if (!image) {
            return;
        }

        if (image.complete) {
            extractPalette(image);
            return;
        }

        image.addEventListener(
            "load",
            () => extractPalette(image),
            { once: true }
        );
    }

    applyPalette(savedImage);

    photoInput?.addEventListener("change", () => {
        const file = photoInput.files?.[0];

        if (!file || !avatarPreview) {
            return;
        }

        let image = avatarPreview.querySelector("img");

        if (!image) {
            image = document.createElement("img");
            avatarPreview.textContent = "";
            avatarPreview.appendChild(image);
        }

        image.src = URL.createObjectURL(file);
        image.alt = "Prévia da nova foto de perfil";

        image.addEventListener(
            "load",
            () => extractPalette(image),
            { once: true }
        );
    });
});

document.addEventListener("DOMContentLoaded", () => {
    document
        .querySelectorAll("[data-product-picker]")
        .forEach(picker => {
            const select = picker.querySelector("select");

            const preview = picker.querySelector(
                "[data-product-picker-preview]"
            );

            if (!select || !preview) {
                return;
            }

            function updatePreview() {
                const selected = select.options[
                    select.selectedIndex
                ];

                const label = selected?.textContent?.trim();

                preview.textContent = (
                    label && select.value
                    ? label.charAt(0).toUpperCase()
                    : "+"
                );

                preview.classList.toggle(
                    "has-product",
                    Boolean(select.value)
                );
            }

            select.addEventListener(
                "change",
                updatePreview
            );

            updatePreview();
        });
});

document.addEventListener("DOMContentLoaded", () => {
    document
        .querySelectorAll("[data-file-preview]")
        .forEach(preview => {
            const container = preview.closest(
                ".product-image-input"
            );

            const input = container?.querySelector(
                'input[type="file"]'
            );

            input?.addEventListener("change", () => {
                const file = input.files?.[0];

                if (!file) {
                    return;
                }

                preview.textContent = "";

                const image = document.createElement("img");
                image.src = URL.createObjectURL(file);
                image.alt = "Prévia da foto do produto";

                preview.appendChild(image);
            });
        });
});