(function () {
    "use strict";

    const MAX_FILE_SIZE =
        100 * 1024 * 1024;

    function normalizeText(value) {
        return String(value || "")
            .trim()
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");
    }

    function findHeading(fragment) {
        const normalizedFragment =
            normalizeText(fragment);

        return Array.from(
            document.querySelectorAll(
                "h1, h2, h3, h4"
            )
        ).find(function (element) {
            return normalizeText(
                element.textContent
            ).includes(
                normalizedFragment
            );
        });
    }

    function commonAncestor(elements) {
        const validElements = elements.filter(Boolean);

        if (!validElements.length) {
            return null;
        }

        let current = validElements[0];

        while (current) {
            const containsAll = validElements.every(
                function (element) {
                    return current.contains(element);
                }
            );

            if (containsAll) {
                return current;
            }

            current = current.parentElement;
        }

        return null;
    }

    function findCard(start, oppositeElement, root) {
        let current = start.parentElement;

        while (
            current &&
            current !== root &&
            current.parentElement
        ) {
            if (
                current.parentElement.contains(
                    oppositeElement
                )
            ) {
                return current;
            }

            current = current.parentElement;
        }

        return start.parentElement;
    }

    const title = findHeading(
        "importar estudiantes desde excel"
    );

    const uploadHeading = findHeading(
        "seleccionar matriz"
    );

    const resultHeading = findHeading(
        "resultado de la importacion"
    );

    const fileInput = document.querySelector(
        "input[type='file']"
    );

    if (
        !title ||
        !uploadHeading ||
        !resultHeading ||
        !fileInput
    ) {
        return;
    }

    let root = commonAncestor([
        title,
        fileInput,
        resultHeading
    ]);

    if (
        !root ||
        root === document.body ||
        root === document.documentElement
    ) {
        root =
            title.closest(
                "main, .app-main, .main-content, .content"
            ) ||
            fileInput.closest(
                "main, .app-main, .main-content, .content"
            );
    }

    if (!root) {
        return;
    }

    root.classList.add(
        "excel-import-pro"
    );

    const hero = title.parentElement;

    hero.classList.add(
        "excel-import-hero-pro"
    );

    if (
        !hero.querySelector(
            ".excel-import-hero-main"
        )
    ) {
        const heroMain = document.createElement(
            "div"
        );

        heroMain.className =
            "excel-import-hero-main";

        const icon = document.createElement(
            "span"
        );

        icon.className =
            "excel-import-hero-icon";

        icon.textContent = "XLSX";

        const textContainer =
            document.createElement("div");

        const children = Array.from(
            hero.children
        ).filter(function (child) {
            return (
                child !== heroMain &&
                !child.classList.contains(
                    "excel-import-limit-badge"
                )
            );
        });

        children.forEach(function (child) {
            textContainer.appendChild(child);
        });

        heroMain.appendChild(icon);
        heroMain.appendChild(textContainer);
        hero.prepend(heroMain);
    }

    if (
        !hero.querySelector(
            ".excel-import-limit-badge"
        )
    ) {
        const badge = document.createElement(
            "div"
        );

        badge.className =
            "excel-import-limit-badge";

        badge.innerHTML = `
            <span>100</span>
            <div>
                <small>Límite por archivo</small>
                <strong>100 MB</strong>
            </div>
        `;

        hero.appendChild(badge);
    }

    const uploadCard = findCard(
        uploadHeading,
        resultHeading,
        root
    );

    const resultCard = findCard(
        resultHeading,
        fileInput,
        root
    );

    uploadCard.classList.add(
        "excel-import-card",
        "excel-import-upload-card"
    );

    resultCard.classList.add(
        "excel-import-card",
        "excel-import-result-card"
    );

    const grid = commonAncestor([
        uploadCard,
        resultCard
    ]);

    if (grid && grid !== root) {
        grid.classList.add(
            "excel-import-grid"
        );
    }

    if (
        !root.querySelector(
            ".excel-import-metrics"
        )
    ) {
        const metrics = document.createElement(
            "section"
        );

        metrics.className =
            "excel-import-metrics";

        metrics.innerHTML = `
            <article class="excel-import-metric">
                <span class="excel-import-metric-icon">
                    XLSX
                </span>
                <div>
                    <span>Formato permitido</span>
                    <strong>Microsoft Excel .xlsx</strong>
                </div>
            </article>

            <article class="excel-import-metric">
                <span class="excel-import-metric-icon">
                    100
                </span>
                <div>
                    <span>Capacidad máxima</span>
                    <strong>Hasta 100 MB</strong>
                </div>
            </article>

            <article class="excel-import-metric">
                <span class="excel-import-metric-icon">
                    CI
                </span>
                <div>
                    <span>Identificador principal</span>
                    <strong>Actualización por cédula</strong>
                </div>
            </article>
        `;

        const reference =
            grid && grid !== root
                ? grid
                : uploadCard;

        reference.parentElement.insertBefore(
            metrics,
            reference
        );
    }

    const fileZone = document.createElement(
        "div"
    );

    fileZone.className =
        "excel-file-zone";

    fileInput.parentElement.insertBefore(
        fileZone,
        fileInput
    );

    fileZone.appendChild(fileInput);

    fileInput.accept =
        ".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";

    const fileMeta = document.createElement(
        "div"
    );

    fileMeta.className =
        "excel-file-meta";

    fileMeta.innerHTML = `
        <strong>Arrastra el archivo o selecciónalo</strong>
        <span>Formato .xlsx · Tamaño máximo 100 MB</span>
    `;

    fileZone.appendChild(fileMeta);

    const form = fileInput.closest("form");

    const submitButton = form
        ? form.querySelector(
            "button[type='submit'], input[type='submit']"
        )
        : null;

    if (submitButton) {
        submitButton.classList.add(
            "excel-import-submit"
        );
    }

    Array.from(
        uploadCard.querySelectorAll(
            "a, button"
        )
    ).forEach(function (element) {
        const text = normalizeText(
            element.textContent ||
            element.value
        );

        if (text.includes("descargar plantilla")) {
            element.classList.add(
                "excel-import-template"
            );
        }

        if (text === "volver") {
            element.classList.add(
                "excel-import-back"
            );
        }
    });

    const placeholder = Array.from(
        resultCard.querySelectorAll(
            "div, p, section, article"
        )
    ).find(function (element) {
        return normalizeText(
            element.textContent
        ).includes(
            "el resumen aparecera despues"
        );
    });

    if (placeholder) {
        placeholder.classList.add(
            "excel-result-placeholder"
        );
    }

    if (
        !resultCard.querySelector(
            ".excel-result-state"
        )
    ) {
        const state = document.createElement(
            "span"
        );

        state.className =
            "excel-result-state";

        state.textContent =
            "En espera de una matriz";

        resultHeading.insertAdjacentElement(
            "afterend",
            state
        );
    }

    function formatBytes(bytes) {
        if (!bytes) {
            return "0 MB";
        }

        const megabytes =
            bytes / (1024 * 1024);

        return (
            megabytes.toFixed(
                megabytes >= 10 ? 1 : 2
            ) + " MB"
        );
    }

    function validateFile(file) {
        fileZone.classList.remove(
            "is-valid",
            "is-invalid"
        );

        if (!file) {
            fileMeta.innerHTML = `
                <strong>Arrastra el archivo o selecciónalo</strong>
                <span>Formato .xlsx · Tamaño máximo 100 MB</span>
            `;

            if (submitButton) {
                submitButton.disabled = false;
            }

            return;
        }

        const validExtension =
            file.name
                .toLowerCase()
                .endsWith(".xlsx");

        const validSize =
            file.size <= MAX_FILE_SIZE;

        if (!validExtension) {
            fileZone.classList.add(
                "is-invalid"
            );

            fileMeta.innerHTML = `
                <strong>Formato no permitido</strong>
                <span>Selecciona un archivo con extensión .xlsx</span>
            `;

            if (submitButton) {
                submitButton.disabled = true;
            }

            return;
        }

        if (!validSize) {
            fileZone.classList.add(
                "is-invalid"
            );

            fileMeta.innerHTML = `
                <strong>El archivo supera los 100 MB</strong>
                <span>${file.name} · ${formatBytes(file.size)}</span>
            `;

            if (submitButton) {
                submitButton.disabled = true;
            }

            return;
        }

        fileZone.classList.add(
            "is-valid"
        );

        fileMeta.innerHTML = `
            <strong>${file.name}</strong>
            <span>${formatBytes(file.size)} · Archivo listo para procesar</span>
        `;

        if (submitButton) {
            submitButton.disabled = false;
        }
    }

    fileInput.addEventListener(
        "change",
        function () {
            validateFile(
                fileInput.files[0]
            );
        }
    );

    [
        "dragenter",
        "dragover"
    ].forEach(function (eventName) {
        fileZone.addEventListener(
            eventName,
            function (event) {
                event.preventDefault();

                fileZone.classList.add(
                    "is-dragging"
                );
            }
        );
    });

    [
        "dragleave",
        "drop"
    ].forEach(function (eventName) {
        fileZone.addEventListener(
            eventName,
            function (event) {
                event.preventDefault();

                fileZone.classList.remove(
                    "is-dragging"
                );
            }
        );
    });

    fileZone.addEventListener(
        "drop",
        function (event) {
            const files =
                event.dataTransfer.files;

            if (!files.length) {
                return;
            }

            const transfer =
                new DataTransfer();

            transfer.items.add(files[0]);

            fileInput.files =
                transfer.files;

            validateFile(files[0]);
        }
    );

    if (form && submitButton) {
        form.addEventListener(
            "submit",
            function () {
                submitButton.disabled = true;

                if (
                    submitButton.tagName === "INPUT"
                ) {
                    submitButton.value =
                        "Procesando matriz...";
                } else {
                    submitButton.textContent =
                        "Procesando matriz...";
                }
            }
        );
    }

    validateFile(
        fileInput.files[0]
    );
})();
