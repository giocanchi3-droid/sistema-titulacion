
document.addEventListener("DOMContentLoaded", function () {

    const paginasPermitidas = [
        "/",
        "/estudiantes/",
        "/estudiantes/nuevo/",
        "/actas/",
        "/estudiantes/importar/"
    ];

    if (!paginasPermitidas.includes(window.location.pathname)) {
        return;
    }

    const main = document.querySelector("main");

    if (!main) {
        return;
    }


    function obtenerAlpha(color) {

        if (!color) {
            return 1;
        }

        const rgba = color.match(
            /rgba?\(\s*[\d.]+\s*,\s*[\d.]+\s*,\s*[\d.]+(?:\s*,\s*([\d.]+))?\s*\)/
        );

        if (!rgba) {
            return 1;
        }

        if (rgba[1] === undefined) {
            return 1;
        }

        return parseFloat(rgba[1]);
    }


    function numero(valor) {
        const n = parseFloat(valor);

        return Number.isNaN(n) ? 0 : n;
    }


    function debeSerPanel(elemento) {

        if (
            elemento === main ||
            elemento.tagName === "MAIN"
        ) {
            return false;
        }


        const estilo =
            window.getComputedStyle(elemento);

        const rect =
            elemento.getBoundingClientRect();


        if (
            rect.width < 180 ||
            rect.height < 45
        ) {
            return false;
        }


        const radio =
            Math.max(
                numero(estilo.borderTopLeftRadius),
                numero(estilo.borderTopRightRadius),
                numero(estilo.borderBottomLeftRadius),
                numero(estilo.borderBottomRightRadius)
            );


        const borde =
            Math.max(
                numero(estilo.borderTopWidth),
                numero(estilo.borderRightWidth),
                numero(estilo.borderBottomWidth),
                numero(estilo.borderLeftWidth)
            );


        const alpha =
            obtenerAlpha(
                estilo.backgroundColor
            );


        const tieneBlur =
            estilo.backdropFilter !== "none" ||
            estilo.webkitBackdropFilter !== "none";


        const tieneFondo =
            estilo.backgroundImage !== "none";


        const tieneSombra =
            estilo.boxShadow !== "none";


        const esVisualmentePanel =
            radio >= 8 ||
            borde > 0 ||
            tieneSombra;


        const tieneTransparencia =
            alpha < 0.98 ||
            tieneBlur ||
            tieneFondo;


        return (
            esVisualmentePanel &&
            tieneTransparencia
        );
    }


    function corregirPanel(elemento) {

        elemento.classList.add(
            "solid-auto-panel"
        );

        elemento.style.setProperty(
            "background-color",
            "#091D2C",
            "important"
        );

        elemento.style.setProperty(
            "background-image",
            "none",
            "important"
        );

        elemento.style.setProperty(
            "opacity",
            "1",
            "important"
        );

        elemento.style.setProperty(
            "backdrop-filter",
            "none",
            "important"
        );

        elemento.style.setProperty(
            "-webkit-backdrop-filter",
            "none",
            "important"
        );
    }


    function buscarPaneles() {

        const elementos =
            main.querySelectorAll(
                "div, section, article, form, fieldset"
            );


        elementos.forEach(function (elemento) {

            if (debeSerPanel(elemento)) {
                corregirPanel(elemento);
            }

        });

    }


    buscarPaneles();


    /* Algunas páginas construyen partes mediante JS */
    setTimeout(buscarPaneles, 300);
    setTimeout(buscarPaneles, 1000);

});


