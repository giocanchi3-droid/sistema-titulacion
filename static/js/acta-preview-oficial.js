
document.addEventListener(
    "DOMContentLoaded",
    function () {

        /* ===================================================
           UTILIDADES
        =================================================== */

        function normalizar(texto) {

            return (texto || "")
                .normalize("NFD")
                .replace(
                    /[\u0300-\u036f]/g,
                    ""
                )
                .toLowerCase()
                .trim();

        }


        function encontrarControlPorLabel(texto) {

            const objetivo =
                normalizar(texto);

            const labels =
                Array.from(
                    document.querySelectorAll("label")
                );

            const label =
                labels.find(function (item) {

                    return normalizar(
                        item.textContent
                    ).includes(objetivo);

                });


            if (!label) {
                return null;
            }


            if (label.htmlFor) {

                const control =
                    document.getElementById(
                        label.htmlFor
                    );

                if (control) {
                    return control;
                }

            }


            return (
                label.querySelector(
                    "input, select, textarea"
                ) ||
                label.parentElement?.querySelector(
                    "input, select, textarea"
                )
            );

        }


        function encontrarControlPorNombre(
            palabras
        ) {

            const controles =
                Array.from(
                    document.querySelectorAll(
                        "input, select, textarea"
                    )
                );


            return controles.find(
                function (control) {

                    const cadena =
                        normalizar(
                            [
                                control.name,
                                control.id,
                                control.placeholder
                            ].join(" ")
                        );


                    return palabras.some(
                        function (palabra) {

                            return cadena.includes(
                                normalizar(palabra)
                            );

                        }
                    );

                }
            ) || null;

        }


        function valorSelect(control) {

            if (!control) {
                return "";
            }


            if (
                control.tagName === "SELECT"
            ) {

                const opcion =
                    control.options[
                        control.selectedIndex
                    ];

                if (!opcion) {
                    return "";
                }


                const texto =
                    opcion.textContent.trim();


                if (
                    texto === "---------" ||
                    texto.toLowerCase().includes(
                        "seleccionar"
                    )
                ) {
                    return "";
                }


                return texto;
            }


            return control.value || "";

        }


        function escaparHtml(valor) {

            const div =
                document.createElement("div");

            div.textContent =
                valor || "";

            return div.innerHTML;

        }


        function fechaTexto(valor) {

            let fecha;

            if (valor) {

                const partes =
                    valor.split("-");

                if (partes.length === 3) {

                    fecha =
                        new Date(
                            Number(partes[0]),
                            Number(partes[1]) - 1,
                            Number(partes[2])
                        );

                }

            }


            if (!fecha || isNaN(fecha)) {
                fecha = new Date();
            }


            return fecha.toLocaleDateString(
                "es-EC",
                {
                    weekday: "long",
                    year: "numeric",
                    month: "long",
                    day: "numeric"
                }
            );

        }


        /* ===================================================
           ENCONTRAR VISTA PREVIA ACTUAL
        =================================================== */

        const titulos =
            Array.from(
                document.querySelectorAll(
                    "h1, h2, h3, h4, h5, h6"
                )
            );


        const tituloResumen =
            titulos.find(
                function (titulo) {

                    return normalizar(
                        titulo.textContent
                    ).includes(
                        "resumen del acta"
                    );

                }
            );


        if (!tituloResumen) {
            return;
        }


        let contenedor =
            tituloResumen.closest(
                [
                    ".preview-card",
                    ".preview-panel",
                    ".summary-panel",
                    "[class*='preview']",
                    "[class*='summary']",
                    ".card",
                    ".panel"
                ].join(",")
            );


        if (!contenedor) {

            contenedor =
                tituloResumen.parentElement;

        }


        if (!contenedor) {
            return;
        }


        contenedor.classList.add(
            "official-acta-container"
        );


        /* ===================================================
           CONTROLES DEL FORMULARIO
        =================================================== */

        const estudiante =
            encontrarControlPorLabel(
                "Estudiante"
            ) ||
            encontrarControlPorNombre(
                ["estudiante"]
            );


        const tipoActa =
            encontrarControlPorLabel(
                "Tipo de acta"
            ) ||
            encontrarControlPorNombre(
                [
                    "tipo_acta",
                    "tipo-acta",
                    "tipo"
                ]
            );


        const fecha =
            encontrarControlPorNombre(
                [
                    "fecha_grado",
                    "fecha_defensa",
                    "fecha"
                ]
            );


        const cedula =
            encontrarControlPorNombre(
                [
                    "cedula",
                    "identificacion"
                ]
            );


        /* ===================================================
           OBTENER DATOS
        =================================================== */

        function obtenerEstudiante() {

            let nombre =
                valorSelect(estudiante);


            if (!nombre) {
                nombre = "ESTUDIANTE SIN SELECCIONAR";
            }


            return nombre;

        }


        function obtenerCedula() {

            if (cedula && cedula.value) {
                return cedula.value;
            }


            if (
                estudiante &&
                estudiante.tagName === "SELECT"
            ) {

                const opcion =
                    estudiante.options[
                        estudiante.selectedIndex
                    ];


                if (opcion) {

                    return (
                        opcion.dataset.cedula ||
                        opcion.dataset.identificacion ||
                        opcion.dataset.documento ||
                        "Pendiente"
                    );

                }

            }


            return "Pendiente";

        }


        function obtenerTipo() {

            const texto =
                normalizar(
                    valorSelect(tipoActa)
                );


            if (
                texto.includes("complexivo")
            ) {
                return "complexivo";
            }


            return "trabajo";

        }


        /* ===================================================
           FIRMAS
        =================================================== */

        function firmasTrabajo() {

            return `
                <div class="official-signature">

                    <div class="official-signature-line">
                        Firma
                    </div>

                    <div class="official-signature-name">
                        Miembro del tribunal
                    </div>

                </div>

                <div class="official-signature">

                    <div class="official-signature-line">
                        Firma
                    </div>

                    <div class="official-signature-name">
                        Miembro del tribunal
                    </div>

                </div>

                <div class="official-signature">

                    <div class="official-signature-line">
                        Firma
                    </div>

                    <div class="official-signature-name">
                        Miembro del tribunal
                    </div>

                </div>

                <div class="official-signature">

                    <div class="official-signature-line">
                        Firma
                    </div>

                    <div class="official-signature-name">
                        Presidente / Responsable
                    </div>

                </div>
            `;

        }


        function firmasComplexivo() {

            return `
                <div class="official-signature">

                    <div class="official-signature-line">
                        Firma
                    </div>

                    <div class="official-signature-name">
                        Miembro del tribunal
                    </div>

                </div>

                <div class="official-signature">

                    <div class="official-signature-line">
                        Firma
                    </div>

                    <div class="official-signature-name">
                        Miembro del tribunal
                    </div>

                </div>

                <div class="official-signature">

                    <div class="official-signature-line">
                        Firma
                    </div>

                    <div class="official-signature-name">
                        Responsable
                    </div>

                </div>
            `;

        }


        /* ===================================================
           RENDER
        =================================================== */

        function renderizar() {

            const tipo =
                obtenerTipo();

            const nombre =
                escaparHtml(
                    obtenerEstudiante()
                );

            const numeroCedula =
                escaparHtml(
                    obtenerCedula()
                );

            const fechaActual =
                escaparHtml(
                    fechaTexto(
                        fecha?.value
                    )
                );


            let titulo;

            let presentacion;

            let tabla;

            let firmas;


            if (tipo === "complexivo") {

                titulo =
                    "Registro de Defensa Examen Complexivo";


                presentacion = `
                    se presenta a la defensa de
                    <strong>
                        Examen Complexivo
                    </strong>
                `;


                tabla = `
                    <table class="official-grade-table">

                        <tr>
                            <td>
                                CALIFICACIÓN DEL
                                EXAMEN TEÓRICO:
                            </td>

                            <td>
                                —
                            </td>
                        </tr>

                        <tr>
                            <td>
                                CALIFICACIÓN DEL
                                EXAMEN PRÁCTICO:
                            </td>

                            <td>
                                — /20
                            </td>
                        </tr>

                        <tr>
                            <td>
                                SUMA TOTAL:
                            </td>

                            <td>
                                — /50
                            </td>
                        </tr>

                    </table>
                `;


                firmas =
                    firmasComplexivo();

            }
            else {

                titulo =
                    "Registro de Defensa oral";


                presentacion = `
                    se presenta a la exposición oral
                    de su trabajo de titulación
                `;


                tabla = `
                    <table class="official-grade-table">

                        <tr>
                            <td>
                                CALIFICACIÓN DEL
                                TRABAJO ESCRITO:
                            </td>

                            <td>
                                —
                            </td>
                        </tr>

                        <tr>
                            <td>
                                CALIFICACIÓN DE LA
                                SUSTENTACIÓN ORAL:
                            </td>

                            <td>
                                — /20
                            </td>
                        </tr>

                        <tr>
                            <td>
                                SUMA TOTAL:
                            </td>

                            <td>
                                — /50
                            </td>
                        </tr>

                    </table>
                `;


                firmas =
                    firmasTrabajo();

            }


            contenedor.innerHTML = `

                <div class="official-preview-info">

                    <strong>
                        Vista previa oficial
                    </strong>

                    <span class="official-preview-badge">
                        ${tipo === "complexivo"
                            ? "Examen Complexivo"
                            : "Trabajo de titulación"}
                    </span>

                </div>


                <div class="official-acta-paper">


                    <div class="official-acta-header">


                        <div class="official-acta-logo-box">

                            <img
                                class="official-acta-logo"
                                src="/static/img/logo-puce-tec-actas.jpg"
                                alt="PUCE TEC"
                            >

                        </div>


                        <div class="official-acta-unit">

                            UNIDAD ACADÉMICA
                            ESPECIALIZADA EN

                            <br>

                            FORMACIÓN TÉCNICA Y
                            TECNOLÓGICA

                            <br>

                            <strong>
                                PUCE TEC
                            </strong>

                        </div>


                    </div>


                    <div class="official-acta-title">

                        ${titulo}

                    </div>


                    <p class="official-acta-paragraph">

                        En la Ciudad de Quito el día,

                        <strong>
                            ${fechaActual}
                        </strong>,

                        dando cumplimiento a las
                        disposiciones en la normativa
                        legal vigente, se deja constancia
                        que el estudiante

                        <span class="official-student-name">
                            ${nombre}
                        </span>

                        con número de cédula

                        <strong>
                            ${numeroCedula}
                        </strong>

                        ${presentacion}.

                    </p>


                    <p class="official-acta-paragraph">

                        Luego de la deliberación del
                        tribunal el estudiante ha obtenido
                        como resultado las siguientes
                        calificaciones, en la materia de

                        <strong>
                            Integración Curricular
                        </strong>.

                    </p>


                    ${tabla}


                    <div class="official-acta-notice">

                        Se informa que esta nota y este
                        evento no constituyen una ceremonia
                        de graduación.

                        De acuerdo con la normativa vigente
                        de la PUCE, la Secretaría certificará
                        el cumplimiento de todos los requisitos
                        y notificará al estudiante
                        correspondiente.

                    </div>


                    <div class="official-signatures">

                        ${firmas}

                    </div>


                </div>
            `;

        }


        /* ===================================================
           EVENTOS
        =================================================== */

        renderizar();


        [
            estudiante,
            tipoActa,
            fecha,
            cedula
        ]
        .filter(Boolean)
        .forEach(
            function (control) {

                control.addEventListener(
                    "change",
                    renderizar
                );

                control.addEventListener(
                    "input",
                    renderizar
                );

            }
        );

    }
);

