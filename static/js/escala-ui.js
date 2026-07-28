(function () {
    "use strict";

    function aplicarEscalaGlobal() {
        const body = document.body;

        const paginaInterna =
            body.classList.contains("app-authenticated") ||
            body.classList.contains("system-page");

        if (!paginaInterna) {
            return;
        }

        /*
         * Eliminar clases utilizadas por versiones anteriores
         * para impedir que el contenido se amplíe dos veces.
         */

        document.querySelectorAll(
            ".puce-ui-scaled, " +
            ".puce-main-scaled, " +
            ".puce-content-scale"
        ).forEach(function (elemento) {
            elemento.classList.remove(
                "puce-ui-scaled",
                "puce-main-scaled",
                "puce-content-scale"
            );
        });

        /*
         * Priorizar el contenedor que incluye encabezado y
         * contenido, pero no el menú lateral.
         */

        const selectores = [
            ".app-main",
            ".main-wrapper",
            ".main-content-wrapper",
            ".content-side",
            "main"
        ];

        let contenidoPrincipal = null;

        for (const selector of selectores) {
            const candidato = document.querySelector(selector);

            if (
                candidato &&
                !candidato.closest(
                    ".sidebar, .app-sidebar, .side-menu, aside"
                )
            ) {
                contenidoPrincipal = candidato;
                break;
            }
        }

        if (!contenidoPrincipal) {
            console.warn(
                "No se encontró el contenedor principal para aplicar la escala."
            );

            return;
        }

        contenidoPrincipal.classList.add(
            "puce-content-scale"
        );
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            aplicarEscalaGlobal
        );
    } else {
        aplicarEscalaGlobal();
    }

    window.addEventListener(
        "load",
        aplicarEscalaGlobal
    );
})();
