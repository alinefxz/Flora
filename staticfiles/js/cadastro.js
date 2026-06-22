document.addEventListener("DOMContentLoaded", () => {
    const radios = document.querySelectorAll('input[name="tipo_usuario"]');
    const userFields = document.querySelector("[data-user-fields]");
    const specialistFields = document.querySelector("[data-specialist-fields]");

    if (!radios.length || !userFields || !specialistFields) {
        return;
    }

    function clearSectionFields(section) {
        section.querySelectorAll("input, select, textarea").forEach(field => {
            if (
                field.type === "radio" ||
                field.type === "checkbox"
            ) {
                field.checked = false;
            } else {
                field.value = "";
            }

            if (field.tagName === "SELECT") {
                field.selectedIndex = 0;
                field.dispatchEvent(
                    new Event("smart-select:refresh", { bubbles: true })
                );
            }
        });
    }

    function setSectionState(section, disabled) {
        section.hidden = disabled;

        section.querySelectorAll("input, select, textarea").forEach(field => {
            field.disabled = disabled;
        });

        if (disabled) {
            clearSectionFields(section);
        }
    }

    function toggleFields() {
        const selected = document.querySelector(
            'input[name="tipo_usuario"]:checked'
        );

        if (!selected) {
            setSectionState(userFields, true);
            setSectionState(specialistFields, true);
            return;
        }

        const specialist = selected.value === "ESPECIALISTA";

        setSectionState(userFields, specialist);
        setSectionState(specialistFields, !specialist);
    }

    radios.forEach(radio => {
        radio.addEventListener("change", toggleFields);
    });

    const selected = document.querySelector(
        'input[name="tipo_usuario"]:checked'
    );

    if (selected) {
        toggleFields();
    } else {
        setSectionState(userFields, true);
        setSectionState(specialistFields, true);
    }
});