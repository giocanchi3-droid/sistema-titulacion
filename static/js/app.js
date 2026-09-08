document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("appSidebar");
    const overlay = document.getElementById("sidebarOverlay");
    const toggleButton = document.getElementById("sidebarToggle");
    const closeButton = document.getElementById("closeSidebar");

    function esDesktop() {
        return window.matchMedia("(min-width: 1024px)").matches;
    }

    function sidebarExpanded() {
        return !sidebar?.classList.contains("is-collapsed");
    }

    function openSidebar() {
        if (esDesktop()) {
            sidebar?.classList.remove("is-collapsed");
            updateToggleState();
            return;
        }
        sidebar?.classList.add("open");
        overlay?.classList.add("show");
        sidebar?.setAttribute("aria-hidden", "false");
        overlay?.setAttribute("aria-hidden", "false");
    }

    function closeSidebar() {
        if (esDesktop()) {
            sidebar?.classList.add("is-collapsed");
            updateToggleState();
            return;
        }
        sidebar?.classList.remove("open");
        overlay?.classList.remove("show");
        sidebar?.setAttribute("aria-hidden", "true");
        overlay?.setAttribute("aria-hidden", "true");
        updateToggleState();
    }

    function updateToggleState() {
        const expanded = esDesktop()
            ? sidebarExpanded()
            : sidebar?.classList.contains("open");

        sidebar?.setAttribute("aria-hidden", String(!expanded));
        overlay?.setAttribute("aria-hidden", String(!expanded));
        toggleButton?.setAttribute("aria-expanded", String(expanded));
        toggleButton?.setAttribute(
            "aria-label",
            expanded ? "Cerrar menú" : "Abrir menú"
        );
        toggleButton?.setAttribute(
            "title",
            expanded ? "Cerrar menú" : "Abrir menú"
        );
        if (toggleButton) {
            toggleButton.querySelector("span")?.replaceChildren(
                document.createTextNode(expanded ? "×" : "☰")
            );
        }
    }

    function toggleSidebar() {
        if (esDesktop() && sidebarExpanded()) {
            closeSidebar();
        } else if (!esDesktop() && sidebar?.classList.contains("open")) {
            closeSidebar();
        } else {
            openSidebar();
        }

        updateToggleState();
    }

    toggleButton?.addEventListener("click", toggleSidebar);
    closeButton?.addEventListener("click", closeSidebar);
    overlay?.addEventListener("click", closeSidebar);
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && sidebar?.classList.contains("open")) {
            closeSidebar();
        }
    });
    document.querySelectorAll("#appSidebar a").forEach(function (link) {
        link.addEventListener("click", function () {
            if (window.matchMedia("(max-width: 1023px)").matches) {
                closeSidebar();
            }
        });
    });

    window.addEventListener("resize", function () {
        if (esDesktop()) {
            sidebar?.classList.remove("open");
            overlay?.classList.remove("show");
            document.body.style.overflow = "";
        } else {
            sidebar?.classList.remove("is-collapsed");
        }
        updateToggleState();
    });

    updateToggleState();

    document
        .querySelectorAll("[data-close-message]")
        .forEach(function (button) {
            button.addEventListener("click", function () {
                button.closest(".app-message")?.remove();
            });
        });
});




