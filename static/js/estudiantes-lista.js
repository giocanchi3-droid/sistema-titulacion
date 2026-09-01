(function () {
    "use strict";

    const storageKey = "estudiantes-seleccionados";
    const selected = new Set(JSON.parse(localStorage.getItem(storageKey) || "[]"));
    const checkboxes = Array.from(document.querySelectorAll(".student-selector"));
    const selectAll = document.querySelector("#select-visible-students");
    const count = document.querySelector("#selected-student-count");
    const form = document.querySelector("#bulk-download-form");
    const container = document.querySelector("#selected-student-ids");

    function save() {
        localStorage.setItem(storageKey, JSON.stringify(Array.from(selected)));
        count.textContent = selected.size;
    }

    function refreshVisible() {
        checkboxes.forEach(function (checkbox) {
            checkbox.checked = selected.has(checkbox.value);
        });
        selectAll.checked = checkboxes.length > 0 && checkboxes.every(function (checkbox) {
            return checkbox.checked;
        });
        save();
    }

    checkboxes.forEach(function (checkbox) {
        checkbox.addEventListener("change", function () {
            if (checkbox.checked) selected.add(checkbox.value);
            else selected.delete(checkbox.value);
            refreshVisible();
        });
    });

    selectAll.addEventListener("change", function () {
        checkboxes.forEach(function (checkbox) {
            if (selectAll.checked) selected.add(checkbox.value);
            else selected.delete(checkbox.value);
        });
        refreshVisible();
    });

    form.addEventListener("submit", function (event) {
        if (!selected.size) {
            event.preventDefault();
            window.alert("Seleccione al menos un estudiante.");
            return;
        }
        container.replaceChildren();
        selected.forEach(function (id) {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = "estudiante_ids";
            input.value = id;
            container.appendChild(input);
        });
        localStorage.removeItem(storageKey);
    });

    refreshVisible();
}());
