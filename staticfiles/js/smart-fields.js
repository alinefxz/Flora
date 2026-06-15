document.addEventListener("DOMContentLoaded", () => {
    const enhanced = new WeakMap();
    let cityTarget = null;
    let productTarget = null;

    function csrfToken() {
        return document.cookie
            .split("; ")
            .find(item => item.startsWith("csrftoken="))
            ?.split("=")[1] || "";
    }

    function closeSelects(except = null) {
        document
            .querySelectorAll(".smart-select.is-open")
            .forEach(item => {
                if (item !== except) {
                    item.classList.remove("is-open");
                }
            });
    }

    function actionLabel(select) {
        const kind = select.dataset.createKind
            || (select.name === "cidade" ? "city" : "");

        if (kind === "city") {
            return "Não encontrei minha cidade";
        }

        if (kind === "product") {
            return "Não encontrei meu produto";
        }

        return "";
    }

    function enhanceSelect(select) {
        if (enhanced.has(select) || select.multiple) {
            return;
        }

        const wrapper = document.createElement("div");
        wrapper.className = "smart-select";

        const trigger = document.createElement("button");
        trigger.type = "button";
        trigger.className = "smart-select-trigger";
        trigger.setAttribute("aria-haspopup", "listbox");

        const panel = document.createElement("div");
        panel.className = "smart-select-panel";
        panel.setAttribute("role", "listbox");

        select.classList.add("smart-select-native");
        select.insertAdjacentElement("afterend", wrapper);
        wrapper.append(trigger, panel);

        function render() {
            const selected = select.options[select.selectedIndex];

            trigger.textContent = (
                selected?.textContent?.trim()
                || "Selecione uma opção"
            );

            trigger.classList.toggle(
                "is-placeholder",
                !select.value
            );

            trigger.disabled = select.disabled;
            panel.textContent = "";

            const options = [...select.options].filter(
                option => option.value
            );

            const searchable = (
                options.length > 6
                || select.hasAttribute("data-smart-select")
                || actionLabel(select)
            );

            let search = null;

            if (searchable) {
                search = document.createElement("input");
                search.type = "search";
                search.className = "smart-select-search";
                search.placeholder = (
                    select.dataset.searchPlaceholder
                    || "Pesquisar"
                );
                search.setAttribute(
                    "aria-label",
                    "Pesquisar opções"
                );

                panel.appendChild(search);
            }

            const list = document.createElement("div");
            list.className = "smart-select-options";
            panel.appendChild(list);

            options.forEach(option => {
                const button = document.createElement("button");

                button.type = "button";
                button.className = "smart-select-option";
                button.textContent = option.textContent.trim();
                button.dataset.search = (
                    button.textContent.toLocaleLowerCase("pt-BR")
                );

                button.classList.toggle(
                    "is-selected",
                    option.selected
                );

                button.disabled = option.disabled;

                button.addEventListener("click", () => {
                    select.value = option.value;

                    select.dispatchEvent(
                        new Event("change", {
                            bubbles: true,
                        })
                    );

                    wrapper.classList.remove("is-open");
                    render();
                });

                list.appendChild(button);
            });

            const label = actionLabel(select);

            if (label) {
                const action = document.createElement("button");

                action.type = "button";
                action.className = "smart-select-create";
                action.textContent = label;

                action.addEventListener("click", () => {
                    wrapper.classList.remove("is-open");

                    if (
                        select.dataset.createKind === "product"
                        || label.includes("produto")
                    ) {
                        openProductModal(select);
                    } else {
                        openCityModal(select);
                    }
                });

                panel.appendChild(action);
            }

            search?.addEventListener("input", () => {
                const term = search.value
                    .trim()
                    .toLocaleLowerCase("pt-BR");

                list
                    .querySelectorAll(".smart-select-option")
                    .forEach(item => {
                        item.hidden = !item.dataset.search
                            .includes(term);
                    });
            });
        }

        trigger.addEventListener("click", () => {
            if (select.disabled) {
                return;
            }

            const opening = !wrapper.classList.contains(
                "is-open"
            );

            closeSelects(wrapper);
            wrapper.classList.toggle("is-open", opening);

            if (opening) {
                panel.querySelector("input")?.focus();
            }
        });

        select.addEventListener("change", render);
        select.addEventListener(
            "smart-select:refresh",
            render
        );

        enhanced.set(select, {
            render,
            wrapper,
        });

        render();
    }

    function addAndSelect(select, value, label) {
        if (!select) {
            return;
        }

        let option = [...select.options].find(
            item => String(item.value) === String(value)
        );

        if (!option) {
            option = new Option(
                label,
                value,
                true,
                true
            );

            select.add(option);
        }

        select.value = String(value);

        select.dispatchEvent(
            new Event("change", {
                bubbles: true,
            })
        );

        select.dispatchEvent(
            new Event("smart-select:refresh")
        );
    }

    async function loadUfs() {
        const select = document.querySelector("#city-uf");

        if (!select || select.options.length > 1) {
            return;
        }

        const response = await fetch("/usuarios/ufs/");
        const data = await response.json();

        data.ufs.forEach(uf => {
            select.add(
                new Option(
                    `${uf.nome_estado} - ${uf.sigla}`,
                    uf.id
                )
            );
        });

        select.dispatchEvent(
            new Event("smart-select:refresh")
        );
    }

    async function loadCategories() {
        const select = document.querySelector(
            "#product-category"
        );

        if (!select || select.options.length > 1) {
            return;
        }

        const response = await fetch(
            "/produtos/categorias/"
        );

        const data = await response.json();

        data.categorias.forEach(category => {
            select.add(
                new Option(
                    category.nome,
                    category.id
                )
            );
        });

        select.dispatchEvent(
            new Event("smart-select:refresh")
        );
    }

    function openCityModal(select) {
        cityTarget = select;

        const modal = document.querySelector(
            "[data-city-modal]"
        );

        const form = document.querySelector(
            "[data-city-form]"
        );

        const status = document.querySelector(
            "[data-city-status]"
        );

        form?.reset();

        form?.querySelectorAll("select").forEach(item => {
            item.dispatchEvent(
                new Event("smart-select:refresh")
            );
        });

        if (status) {
            status.textContent = "";
        }

        loadUfs().catch(() => {
            if (status) {
                status.textContent = (
                    "Não foi possível carregar os estados."
                );
            }
        });

        modal?.showModal();
    }

    function resetProductModal() {
        const form = document.querySelector(
            "[data-product-form]"
        );

        form?.reset();
        form?.removeAttribute("data-verified-code");

        form?.querySelectorAll("select").forEach(item => {
            item.dispatchEvent(
                new Event("smart-select:refresh")
            );
        });

        document
            .querySelector("[data-product-details]")
            ?.setAttribute("hidden", "");

        const submit = document.querySelector(
            "[data-product-submit]"
        );

        if (submit) {
            submit.disabled = true;
        }

        const preview = document.querySelector(
            "[data-product-preview]"
        );

        if (preview) {
            preview.innerHTML = (
                "<span>Foto do produto</span>"
            );
        }

        const status = document.querySelector(
            "[data-product-status]"
        );

        if (status) {
            status.textContent = "";
        }
    }

    function openProductModal(select) {
        productTarget = select;
        resetProductModal();

        loadCategories().catch(() => {
            const status = document.querySelector(
                "[data-product-status]"
            );

            if (status) {
                status.textContent = (
                    "Não foi possível carregar as categorias."
                );
            }
        });

        document
            .querySelector("[data-product-modal]")
            ?.showModal();
    }

    function showProductPreview(url) {
        const preview = document.querySelector(
            "[data-product-preview]"
        );

        if (!preview) {
            return;
        }

        preview.textContent = "";

        const image = document.createElement("img");
        image.src = url;
        image.alt = "Prévia do produto";

        preview.appendChild(image);
    }

    document
        .querySelectorAll("select:not([multiple])")
        .forEach(enhanceSelect);

    document.addEventListener("click", event => {
        if (!event.target.closest(".smart-select")) {
            closeSelects();
        }

        if (event.target.closest("[data-modal-close]")) {
            event.target.closest("dialog")?.close();
        }
    });

    document.addEventListener("keydown", event => {
        if (event.key === "Escape") {
            closeSelects();
        }
    });

    document
        .querySelector("[data-city-form]")
        ?.addEventListener("submit", async event => {
            event.preventDefault();

            const form = event.currentTarget;
            const status = form.querySelector(
                "[data-city-status]"
            );

            status.textContent = (
                "Conferindo na lista oficial do IBGE..."
            );

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    body: new FormData(form),
                    headers: {
                        "X-CSRFToken": csrfToken(),
                    },
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.erro);
                }

                addAndSelect(
                    cityTarget,
                    data.cidade.id,
                    data.cidade.nome
                );

                form.closest("dialog").close();
            } catch (error) {
                status.textContent = (
                    error.message
                    || "Não foi possível adicionar."
                );
            }
        });

    document
        .querySelector("[data-product-verify]")
        ?.addEventListener("click", async () => {
            const form = document.querySelector(
                "[data-product-form]"
            );

            const codeInput = form.querySelector(
                "[name='codigo_barras']"
            );

            const status = form.querySelector(
                "[data-product-status]"
            );

            const details = form.querySelector(
                "[data-product-details]"
            );

            const submit = form.querySelector(
                "[data-product-submit]"
            );

            const code = codeInput.value.replace(
                /\D/g,
                ""
            );

            codeInput.value = code;
            status.textContent = (
                "Conferindo código e procurando o produto..."
            );

            submit.disabled = true;
            details.hidden = true;

            try {
                const url = (
                    `${form.dataset.verifyUrl}`
                    + `?codigo_barras=${code}`
                );

                const response = await fetch(url);
                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.erro);
                }

                if (data.ja_cadastrado) {
                    addAndSelect(
                        productTarget,
                        data.produto.id,
                        (
                            `${data.produto.nome} `
                            + `(${data.produto.marca})`
                        )
                    );

                    form.closest("dialog").close();
                    return;
                }

                const product = data.produto;

                form.dataset.verifiedCode = code;

                form.querySelector(
                    "[name='nome']"
                ).value = product.nome || "";

                form.querySelector(
                    "[name='marca']"
                ).value = product.marca || "";

                form.querySelector(
                    "[name='fabricante']"
                ).value = product.fabricante || "";

                if (product.imagem) {
                    showProductPreview(product.imagem);
                }

                details.hidden = false;
                submit.disabled = false;

                status.textContent = (
                    "Produto confirmado. Complete a categoria "
                    + "e, se quiser, adicione uma foto."
                );
            } catch (error) {
                form.removeAttribute(
                    "data-verified-code"
                );

                status.textContent = (
                    error.message
                    || "Produto não confirmado."
                );
            }
        });

    document
        .querySelector("#product-image")
        ?.addEventListener("change", event => {
            const file = event.currentTarget.files?.[0];

            if (file) {
                showProductPreview(
                    URL.createObjectURL(file)
                );
            }
        });

    document
        .querySelector("[data-product-form]")
        ?.addEventListener("submit", async event => {
            event.preventDefault();

            const form = event.currentTarget;
            const status = form.querySelector(
                "[data-product-status]"
            );

            const code = form.querySelector(
                "[name='codigo_barras']"
            ).value;

            if (form.dataset.verifiedCode !== code) {
                status.textContent = (
                    "Verifique o código antes de cadastrar."
                );
                return;
            }

            status.textContent = "Salvando produto...";

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    body: new FormData(form),
                    headers: {
                        "X-CSRFToken": csrfToken(),
                    },
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.erro);
                }

                addAndSelect(
                    productTarget,
                    data.produto.id,
                    (
                        `${data.produto.nome} `
                        + `(${data.produto.marca})`
                    )
                );

                form.closest("dialog").close();
            } catch (error) {
                status.textContent = (
                    error.message
                    || "Não foi possível cadastrar."
                );
            }
        });
});