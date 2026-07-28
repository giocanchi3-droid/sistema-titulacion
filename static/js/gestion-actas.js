(function () {
    "use strict";

    const rows = Array.from(
        document.querySelectorAll("[data-ga-row]")
    );

    const counters = {
        total: rows.length,
        generated: 0,
        approved: 0,
        cancelled: 0
    };

    function normalize(value) {
        return String(value || "")
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .trim();
    }

    rows.forEach(function (row) {
        const status = normalize(
            row.dataset.gaStatus
        );

        const label = row.querySelector(
            "[data-ga-status-label]"
        );

        if (
            status.includes("generad") ||
            status.includes("emitid")
        ) {
            counters.generated += 1;

            if (label) {
                label.classList.add(
                    "ga-status-generada"
                );
            }
        }

        if (
            status.includes("aprobad") ||
            status.includes("validad")
        ) {
            counters.approved += 1;

            if (label) {
                label.classList.add(
                    "ga-status-aprobada"
                );
            }
        }

        if (
            status.includes("anulad") ||
            status.includes("cancelad")
        ) {
            counters.cancelled += 1;

            if (label) {
                label.classList.add(
                    "ga-status-anulada"
                );
            }
        }

        if (status.includes("borrador")) {
            if (label) {
                label.classList.add(
                    "ga-status-borrador"
                );
            }
        }
    });

    const elements = {
        total: document.getElementById("ga-total"),
        generated: document.getElementById(
            "ga-generated"
        ),
        approved: document.getElementById(
            "ga-approved"
        ),
        cancelled: document.getElementById(
            "ga-cancelled"
        )
    };

    if (elements.total) {
        elements.total.textContent = counters.total;
    }

    if (elements.generated) {
        elements.generated.textContent =
            counters.generated;
    }

    if (elements.approved) {
        elements.approved.textContent =
            counters.approved;
    }

    if (elements.cancelled) {
        elements.cancelled.textContent =
            counters.cancelled;
    }
})();