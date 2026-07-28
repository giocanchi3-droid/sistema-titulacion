(function () {
    "use strict";

    const formulario = document.getElementById(
        "acta-main-form"
    );

    if (!formulario) {
        return;
    }

    const campos = Array.from(
        formulario.querySelectorAll(
            "input:not([type='hidden']):not([type='submit']), " +
            "select, textarea"
        )
    ).filter(function (campo) {
        return !campo.disabled;
    });

    const barra = document.getElementById(
        "acta-progress-bar"
    );

    const porcentajeTexto = document.getElementById(
        "acta-progress-percentage"
    );

    const detalle = document.getElementById(
        "acta-progress-detail"
    );

    function campoCompletado(campo) {
        if (
            campo.type === "checkbox" ||
            campo.type === "radio"
        ) {
            return campo.checked;
        }

        return String(campo.value || "").trim() !== "";
    }

    function actualizarProgreso() {
        const completados = campos.filter(
            campoCompletado
        ).length;

        const total = campos.length;

        const porcentaje = total
            ? Math.round((completados / total) * 100)
            : 0;

        barra.style.width = porcentaje + "%";
        porcentajeTexto.textContent = porcentaje + "%";

        detalle.textContent =
            completados +
            " de " +
            total +
            " campos completados";
    }

    campos.forEach(function (campo) {
        const contenedor = campo.closest(
            "[data-field-container]"
        );

        campo.classList.add("acta-form-control");

        if (contenedor) {
            if (campo.tagName === "TEXTAREA") {
                contenedor.classList.add(
                    "is-full-width"
                );
            }

            if (
                campo.type === "checkbox" ||
                campo.type === "radio"
            ) {
                contenedor.classList.add(
                    "is-checkbox"
                );
            }
        }

        campo.addEventListener(
            "input",
            actualizarProgreso
        );

        campo.addEventListener(
            "change",
            actualizarProgreso
        );
    });

    const botonesNavegacion = Array.from(
        document.querySelectorAll(
            "[data-section-target]"
        )
    );

    botonesNavegacion.forEach(function (boton) {
        boton.addEventListener(
            "click",
            function () {
                const destino = document.getElementById(
                    boton.dataset.sectionTarget
                );

                if (destino) {
                    destino.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });
                }
            }
        );
    });

    const secciones = Array.from(
        document.querySelectorAll(
            "[data-form-section]"
        )
    );

    if ("IntersectionObserver" in window) {
        const observador = new IntersectionObserver(
            function (entradas) {
                entradas.forEach(function (entrada) {
                    if (!entrada.isIntersecting) {
                        return;
                    }

                    botonesNavegacion.forEach(
                        function (boton) {
                            const activa =
                                boton.dataset.sectionTarget ===
                                entrada.target.id;

                            boton.classList.toggle(
                                "is-active",
                                activa
                            );
                        }
                    );
                });
            },
            {
                rootMargin: "-20% 0px -65% 0px",
                threshold: 0.01
            }
        );

        secciones.forEach(function (seccion) {
            observador.observe(seccion);
        });
    }

    const botonGuardar = document.getElementById(
        "acta-submit-button"
    );

    const textoGuardar = document.getElementById(
        "acta-submit-text"
    );

    formulario.addEventListener(
        "submit",
        function () {
            if (!botonGuardar) {
                return;
            }

            botonGuardar.disabled = true;

            if (textoGuardar) {
                textoGuardar.textContent =
                    "Guardando información...";
            }
        }
    );

    actualizarProgreso();
})();
