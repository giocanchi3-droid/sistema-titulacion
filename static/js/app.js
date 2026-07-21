document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("appSidebar");
    const overlay = document.getElementById("sidebarOverlay");
    const openButton = document.getElementById("openSidebar");
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
    }

    openButton?.addEventListener("click", openSidebar);
    closeButton?.addEventListener("click", closeSidebar);
    overlay?.addEventListener("click", closeSidebar);

    document
        .querySelectorAll("[data-close-message]")
        .forEach(function (button) {
            button.addEventListener("click", function () {
                button.closest(".app-message")?.remove();
            });
        });
});
