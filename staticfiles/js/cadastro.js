document.addEventListener("DOMContentLoaded", () => {
    const radios = document.querySelectorAll('input[name="tipo_usuario"]');
    const userFields = document.querySelector("[data-user-fields]");
    const specialistFields = document.querySelector("[data-specialist-fields]");

    if (!radios.length || !userFields || !specialistFields) return;

    function setSectionState(section, disabled) {
        section.hidden = disabled;
        section.querySelectorAll("input, select, textarea").forEach(field => {
            field.disabled = disabled;

            if (field.disabled) {
                // Evita carregar valores fantasmas em campos ocultados
                if (field.type !== 'radio' && field.type !== 'checkbox') field.value = "";
            }

            if (field.tagName === "SELECT") {
                field.dispatchEvent(new Event("smart-select:refresh"));
            }
        });
    }

    function toggleFields() {
        const selected = document.querySelector('input[name="tipo_usuario"]:checked');
        if (!selected) return; // Proteção para não executar sem seleção ativa
        
        const specialist = selected.value === "ESPECIALISTA";
        setSectionState(userFields, specialist);
        setSectionState(specialistFields, !specialist);
    }

    radios.forEach(radio => {
        radio.addEventListener("change", toggleFields);
    });

    // Só roda a alternância inicial se já houver um tipo pré-selecionado pelo Django
    if (document.querySelector('input[name="tipo_usuario"]:checked')) {
        toggleFields();
    }
});