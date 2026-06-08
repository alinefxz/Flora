document.addEventListener("DOMContentLoaded", () => {
    const radios = document.querySelectorAll(
        'input[name="tipo_usuario"]'
    );
    const userFields = document.querySelector("[data-user-fields]");
    const specialistFields = document.querySelector(
        "[data-specialist-fields]"
    );

    if (!radios.length || !userFields || !specialistFields) return;

    function setSectionState(section, disabled) {
        section.hidden = disabled;
        section.querySelectorAll("input, select, textarea")
            .forEach(field => {
                field.disabled = disabled;
            });
    }

    function toggleFields() {
        const selected = document.querySelector(
            'input[name="tipo_usuario"]:checked'
        );
        const specialist = selected?.value === "ESPECIALISTA";

        setSectionState(userFields, specialist);
        setSectionState(specialistFields, !specialist);
    }

    radios.forEach(radio => {
        radio.addEventListener("change", toggleFields);
    });

    toggleFields();
});
