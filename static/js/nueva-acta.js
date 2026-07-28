(function () {
    "use strict";

    const form = document.getElementById(
        "new-acta-form"
    );

    if (!form) {
        return;
    }

    const allFields = Array.from(
        form.querySelectorAll(
            "input:not([type='hidden']):not([type='submit']), " +
            "select, textarea"
        )
    ).filter(function (field) {
        return !field.disabled;
    });

    const requiredFields = allFields.filter(
        function (field) {
            return field.required;
        }
    );

    const selects = Array.from(
        form.querySelectorAll("select")
    );

    function findField(selectors, fallback) {
        for (const selector of selectors) {
            const element = form.querySelector(selector);

            if (element) {
                return element;
            }
        }

        return fallback || null;
    }

    const studentField = findField(
        [
            "[name='registro']",
            "[name='estudiante']",
            "[name*='registro']",
            "[name*='estudiante']"
        ],
        selects[0]
    );

    const typeField = findField(
        [
            "[name='tipo_acta']",
            "[name='tipo']",
            "[name*='tipo']"
        ],
        selects[1]
    );

    const statusField = findField(
        [
            "[name='estado']",
            "[name*='estado']"
        ],
        selects[2]
    );

    const observationsField = findField(
        [
            "textarea[name='observaciones']",
            "textarea[name*='observacion']",
            "textarea"
        ],
        null
    );

    const progressBar = document.getElementById(
        "new-acta-progress-bar"
    );

    const progressValue = document.getElementById(
        "new-acta-progress-value"
    );

    const progressDescription = document.getElementById(
        "new-acta-progress-description"
    );

    const headerStatus = document.getElementById(
        "new-acta-header-status"
    );

    const studentSummary = document.getElementById(
        "new-acta-summary-student"
    );

    const studentAvatar = document.getElementById(
        "new-acta-student-avatar"
    );

    const typeSummary = document.getElementById(
        "new-acta-summary-type"
    );

    const statusSummary = document.getElementById(
        "new-acta-summary-status"
    );

    const observationsSummary = document.getElementById(
        "new-acta-summary-observations"
    );

    function fieldHasValue(field) {
        if (!field) {
            return false;
        }

        if (
            field.type === "checkbox" ||
            field.type === "radio"
        ) {
            return field.checked;
        }

        return String(field.value || "").trim() !== "";
    }

    function selectedText(field, emptyText) {
        if (!field || !fieldHasValue(field)) {
            return emptyText;
        }

        if (
            field.tagName === "SELECT" &&
            field.selectedOptions.length
        ) {
            const text = field
                .selectedOptions[0]
                .textContent
                .trim();

            if (
                text === "---------" ||
                text === "---------"
            ) {
                return emptyText;
            }

            return text;
        }

        return String(field.value || "").trim();
    }

    function updateProgress() {
        const fieldsToEvaluate = requiredFields.length
            ? requiredFields
            : allFields.filter(function (field) {
                return field !== observationsField;
            });

        const completed = fieldsToEvaluate.filter(
            fieldHasValue
        ).length;

        const total = fieldsToEvaluate.length;

        const percentage = total
            ? Math.round(
                (completed / total) * 100
            )
            : 0;

        if (progressBar) {
            progressBar.style.width =
                percentage + "%";
        }

        if (progressValue) {
            progressValue.textContent =
                percentage + "%";
        }

        if (progressDescription) {
            progressDescription.textContent =
                completed +
                " de " +
                total +
                " campos obligatorios completados.";
        }

        if (headerStatus) {
            if (percentage === 100) {
                headerStatus.textContent =
                    "Listo para guardar";
            } else if (percentage > 0) {
                headerStatus.textContent =
                    "En preparación";
            } else {
                headerStatus.textContent =
                    "Pendiente";
            }
        }
    }

    function updateSummary() {
        const student = selectedText(
            studentField,
            "Sin seleccionar"
        );

        const type = selectedText(
            typeField,
            "Sin seleccionar"
        );

        const status = selectedText(
            statusField,
            "Borrador"
        );

        const observations = selectedText(
            observationsField,
            "Sin observaciones"
        );

        if (studentSummary) {
            studentSummary.textContent = student;
        }

        if (studentAvatar) {
            studentAvatar.textContent =
                student !== "Sin seleccionar"
                    ? student.charAt(0).toUpperCase()
                    : "E";
        }

        if (typeSummary) {
            typeSummary.textContent = type;
        }

        if (statusSummary) {
            statusSummary.textContent = status;
        }

        if (observationsSummary) {
            observationsSummary.textContent =
                observations.length > 55
                    ? observations.slice(0, 55) + "..."
                    : observations;
        }
    }

    function updateWorkflow() {
        const steps = {
            student: studentField,
            type: typeField,
            status: statusField
        };

        Object.entries(steps).forEach(
            function ([name, field]) {
                const step = document.querySelector(
                    "[data-workflow-step='" +
                    name +
                    "']"
                );

                if (!step) {
                    return;
                }

                step.classList.toggle(
                    "is-complete",
                    fieldHasValue(field)
                );
            }
        );
    }

    function updateInterface() {
        updateProgress();
        updateSummary();
        updateWorkflow();
    }

    document.querySelectorAll(
        "[data-new-acta-field]"
    ).forEach(function (container) {
        const textarea = container.querySelector(
            "textarea"
        );

        if (textarea) {
            container.classList.add(
                "is-full-width"
            );
        }
    });

    allFields.forEach(function (field) {
        field.addEventListener(
            "input",
            updateInterface
        );

        field.addEventListener(
            "change",
            updateInterface
        );
    });

    const submitButton = document.getElementById(
        "new-acta-submit"
    );

    const submitText = document.getElementById(
        "new-acta-submit-text"
    );

    form.addEventListener(
        "submit",
        function () {
            if (!submitButton) {
                return;
            }

            submitButton.disabled = true;

            if (submitText) {
                submitText.textContent =
                    "Guardando acta...";
            }
        }
    );

    updateInterface();
})();
