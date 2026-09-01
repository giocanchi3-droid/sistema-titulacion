(function () {
    "use strict";

    const form = document.querySelector("#acta-main-form");
    const idBanner = document.querySelector("#id_id_banner");
    const cedula = document.querySelector("#id_cedula");
    if (!form || !idBanner || !cedula) return;

    async function buscar(campo, valor) {
        if (!valor.trim()) return;
        const url = new URL("/estudiantes/buscar/", window.location.origin);
        url.searchParams.set(campo, valor.trim());
        const respuesta = await fetch(url, {headers: {"Accept": "application/json"}});
        const datos = await respuesta.json();
        if (!datos.encontrado) {
            window.alert("No existe un estudiante con ese dato. Puede continuar normalmente.");
            return;
        }
        Object.entries(datos.estudiante).forEach(function (entrada) {
            const elemento = document.querySelector("#id_" + entrada[0]);
            if (!elemento) return;
            elemento.value = entrada[1];
            elemento.dispatchEvent(new Event("change", {bubbles: true}));
        });
        window.alert("Ya existe un estudiante con estos datos. Se cargó su información para revisión.");
    }

    [
        [idBanner, "id_banner"],
        [cedula, "cedula"]
    ].forEach(function (configuracion) {
        configuracion[0].addEventListener("keydown", function (event) {
            if (event.key !== "Enter") return;
            event.preventDefault();
            buscar(configuracion[1], configuracion[0].value).catch(function () {
                window.alert("No fue posible consultar el estudiante.");
            });
        });
    });
}());
