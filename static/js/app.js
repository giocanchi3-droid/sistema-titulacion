document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("appSidebar");
    const overlay = document.getElementById("sidebarOverlay");
    const toggleButton = document.getElementById("sidebarToggle");
    const closeButton = document.getElementById("closeSidebar");

    function openSidebar() {
        sidebar?.classList.add("open");
        overlay?.classList.add("show");
        document.body.style.overflow = "hidden";
    }

    function closeSidebar() {
        sidebar?.classList.remove("open");
        overlay?.classList.remove("show");
        document.body.style.overflow = "";
        updateToggleState();
    }

    function updateToggleState() {
        const expanded = sidebar?.classList.contains("open");

        toggleButton?.setAttribute("aria-expanded", String(expanded));
        toggleButton?.setAttribute(
            "aria-label",
            expanded ? "Cerrar menú" : "Abrir menú"
        );
        toggleButton?.setAttribute(
            "title",
            expanded ? "Cerrar menú" : "Abrir menú"
        );
    }

    function toggleSidebar() {
        if (sidebar?.classList.contains("open")) {
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
    window.addEventListener("resize", function () {
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




