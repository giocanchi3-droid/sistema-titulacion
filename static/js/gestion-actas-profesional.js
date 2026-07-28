(function () {
    "use strict";

    const filas = Array.from(
        document.querySelectorAll("[data-acta-row]")
    );

    const contadores = {
        total: filas.length,
        generadas: 0,
        aprobadas: 0,
        anuladas: 0
    };

    filas.forEach(function (fila) {
        const estado = String(
            fila.dataset.actaStatus || ""
        ).toLowerCase();

        if (
            estado.includes("generad") ||
            estado.includes("emitid")
        ) {
            contadores.generadas += 1;
        }

        if (
            estado.includes("aprobad") ||
            estado.includes("valid")
        ) {
            contadores.aprobadas += 1;
        }

        if (
            estado.includes("anulad") ||
            estado.includes("cancelad")
        ) {
            contadores.anuladas += 1;
        }
    });

    const elementos = {
        total: document.getElementById(
            "actas-total-count"
        ),
        generadas: document.getElementById(
            "actas-generated-count"
        ),
        aprobadas: document.getElementById(
            "actas-approved-count"
        ),
        anuladas: document.getElementById(
            "actas-cancelled-count"
        )
    };

    if (elementos.total) {
        elementos.total.textContent =
            contadores.total;
    }

    if (elementos.generadas) {
        elementos.generadas.textContent =
            contadores.generadas;
    }

    if (elementos.aprobadas) {
        elementos.aprobadas.textContent =
            contadores.aprobadas;
    }

    if (elementos.anuladas) {
        elementos.anuladas.textContent =
            contadores.anuladas;
    }
})();
