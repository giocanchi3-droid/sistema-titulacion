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

    const secciones = Array.from(
        document.querySelectorAll(
            "[data-form-section]"
        )
    );

    function obtenerDesplazamientoSuperior() {
        const header = document.querySelector(".app-main-header");
        const navegacion = document.querySelector(".acta-form-sidebar-card");
        const esMovil = window.matchMedia("(max-width: 1080px)").matches;
        const alturaHeader = header ? header.getBoundingClientRect().height : 0;
        const alturaNavegacion = esMovil && navegacion
            ? navegacion.getBoundingClientRect().height
            : 0;

        return alturaHeader + alturaNavegacion + 16;
    }

    function activarSeccion(id) {
        botonesNavegacion.forEach(function (boton) {
            boton.classList.toggle(
                "is-active",
                boton.dataset.sectionTarget === id
            );
        });

        const activo = botonesNavegacion.find(function (boton) {
            return boton.dataset.sectionTarget === id;
        });

        if (activo && window.matchMedia("(max-width: 760px)").matches) {
            const navegacion = activo.closest(".acta-form-navigation");
            if (navegacion) {
                const margen = (navegacion.clientWidth - activo.clientWidth) / 2;
                navegacion.scrollTo({
                    left: activo.offsetLeft - margen,
                    behavior: "smooth"
                });
            }
        }
    }

    botonesNavegacion.forEach(function (boton) {
        boton.addEventListener("click", function () {
            const destino = document.getElementById(
                boton.dataset.sectionTarget
            );

            if (!destino) {
                return;
            }

            window.scrollTo({
                top: window.scrollY
                    + destino.getBoundingClientRect().top
                    - obtenerDesplazamientoSuperior(),
                behavior: "smooth"
            });
            activarSeccion(destino.id);
        });
    });

    let ultimaSeccionActiva = "";

    function actualizarSeccionVisible() {
        const limite = obtenerDesplazamientoSuperior() + 24;
        let actual = secciones[0];

        secciones.forEach(function (seccion) {
            if (seccion.getBoundingClientRect().top <= limite) {
                actual = seccion;
            }
        });

        if (actual && actual.id !== ultimaSeccionActiva) {
            ultimaSeccionActiva = actual.id;
            activarSeccion(actual.id);
        }
    }

    let rafPendiente = false;

    function actualizarSeccionEnFrame() {
        if (rafPendiente) {
            return;
        }

        rafPendiente = true;
        window.requestAnimationFrame(function () {
            rafPendiente = false;
            actualizarSeccionVisible();
        });
    }

    window.addEventListener("scroll", actualizarSeccionEnFrame, {
        passive: true
    });
    window.addEventListener("resize", actualizarSeccionVisible);
    actualizarSeccionVisible();

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
