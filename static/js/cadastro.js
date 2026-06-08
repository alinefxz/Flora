document.addEventListener("DOMContentLoaded", () => {
    const radios = document.querySelectorAll(
        'input[name="tipo_usuario"]'
    );
    const userFields = document.querySelector("[data-user-fields]");
    const specialistFields = document.querySelector(
        "[data-specialist-fields]"
    );

    function toggleFields() {
        const selected = document.querySelector(
            'input[name="tipo_usuario"]:checked'
        );
        const specialist = selected?.value === "ESPECIALISTA";

        userFields.hidden = specialist;
        specialistFields.hidden = !specialist;

        userFields.querySelectorAll("input, select, textarea")
            .forEach(field => {
                field.disabled = specialist;
            });

        specialistFields.querySelectorAll("input, select, textarea")
            .forEach(field => {
                field.disabled = !specialist;
            });
    }

    radios.forEach(radio => {
        radio.addEventListener("change", toggleFields);
    });

    toggleFields();
});