(function () {
    "use strict";

    const ruta = window.location.pathname.toLowerCase();

    if (!ruta.startsWith("/actas/")) {
        return;
    }

    function obtenerRGB(color) {
        const resultado = color.match(
            /rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)(?:[,\s/]+([\d.]+))?\s*\)/
        );

        if (!resultado) {
            return null;
        }

        return {
            r: Number(resultado[1]),
            g: Number(resultado[2]),
            b: Number(resultado[3]),
            a: resultado[4] === undefined
                ? 1
                : Number(resultado[4])
        };
    }

    function esFondoClaro(color) {
        const rgb = obtenerRGB(color);

        if (!rgb || rgb.a < 0.15) {
            return false;
        }

        return (
            rgb.r >= 205 &&
            rgb.g >= 205 &&
            rgb.b >= 205
        );
    }

    function corregirPanelesClaros() {
        const elementos = document.querySelectorAll(
            "div, section, article, header, footer, td, span"
        );

        elementos.forEach(function (elemento) {
            if (
                elemento.closest(
                    "nav, aside, button, a, input, select, textarea"
                )
            ) {
                return;
            }

            const rectangulo = elemento.getBoundingClientRect();

            if (
                rectangulo.width < 55 ||
                rectangulo.height < 22
            ) {
                return;
            }

            const estilo = window.getComputedStyle(elemento);

            if (esFondoClaro(estilo.backgroundColor)) {
                elemento.classList.add("puce-acta-panel-dark");
            }
        });
    }

    function corregirEstados() {
        const posiblesEstados = document.querySelectorAll(
            "span, td, div"
        );

        posiblesEstados.forEach(function (elemento) {
            const texto = elemento.textContent
                .trim()
                .toLowerCase();

            const esElementoPequeno =
                elemento.children.length === 0 &&
                texto.length <= 20;

            if (!esElementoPequeno) {
                return;
            }

            if (
                texto === "generada" ||
                texto === "generado"
            ) {
                elemento.classList.add(
                    "puce-estado-acta",
                    "puce-estado-generada"
                );
            }

            if (
                texto === "aprobada" ||
                texto === "aprobado"
            ) {
                elemento.classList.add(
                    "puce-estado-acta",
                    "puce-estado-aprobada"
                );
            }

            if (
                texto === "anulada" ||
                texto === "anulado"
            ) {
                elemento.classList.add(
                    "puce-estado-acta",
                    "puce-estado-anulada"
                );
            }
        });
    }

    function aplicarCorreccion() {
        corregirPanelesClaros();
        corregirEstados();
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            aplicarCorreccion
        );
    } else {
        aplicarCorreccion();
    }

    window.addEventListener("load", aplicarCorreccion);

    const observador = new MutationObserver(function () {
        window.requestAnimationFrame(aplicarCorreccion);
    });

    observador.observe(document.body, {
        childList: true,
        subtree: true
    });
})();
