from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from documentos.models import Acta
from estudiantes.models import RegistroTitulacion

from .decorators import superuser_required
from .forms import UsuarioForm
from .models import BackupArtifact, FieldPermission
from .permissions import permission_model_name
from .services_backups import crear_backup


User = get_user_model()


def _campos(modelo):
    return [
        (campo.name, campo.verbose_name)
        for campo in modelo._meta.fields
        if campo.editable and not campo.auto_created and campo.name != "id"
    ]


CATEGORIAS_ESTUDIANTE = [
    ("Información personal e institucional", {
        "id_banner", "nombres_completos", "cedula", "celular",
        "correo_personal", "correo_instituc", "sede", "programa", "programa_desc",
    }),
    ("Información académica", {
        "numero_cohorte", "periodo_ingreso", "nivel2", "modalidad_titulacion",
        "matricula_uic", "periodo_titulacion_senescyt", "estado", "cumplimiento_idioma",
    }),
    ("Prácticas y servicio comunitario", {
        "materia_practicas_pre_profesionales", "horas_240",
        "materia_servicio_comunitario", "horas_120",
    }),
    ("Tutor y proyecto", {"nombres_completos_tutor", "id_tutor", "tema"}),
    ("Tribunal", {
        "primer_miembro_tribunal", "primer_miembro_id_docente",
        "segundo_miembro_tribunal", "segundo_miembro_id_docente",
        "tercer_miembro_tribunal", "tercer_miembro_id_docente",
        "cuarto_miembro_tribunal", "cuarto_miembro_id_docente",
    }),
    ("Calificaciones", {
        "proyecto_escrito", "defensa_oral", "nota_final",
        "examen_teorico_complexivo", "examen_teorico_practico", "nota_final2",
    }),
    ("Observaciones y seguimiento", {
        "observacion_puce_tec", "observaciones_secretaria_general",
        "nueva_observacion_puce_tec", "estado_envio_registro", "fecha_grado",
        "observacion_secretaria",
    }),
]

CATEGORIAS_ACTA = [
    ("Datos del acta", {"registro", "numero_acta", "tipo_acta", "estado", "observaciones"}),
    ("Documentos y seguimiento", {
        "archivo_word", "archivo_pdf", "creado_por", "fecha_creacion",
        "fecha_generacion", "fecha_actualizacion",
    }),
]


def _grupos_campos(modelo, titulo, categorias, existentes):
    campos = dict(_campos(modelo))
    grupos = []
    usados = set()
    for categoria, nombres in categorias:
        items = [(nombre, campos[nombre]) for nombre in campos if nombre in nombres]
        if items:
            grupos.append({
                "titulo": categoria,
                "campos": items,
                "seleccionados": {nombre for nombre, _ in items if nombre in existentes},
            })
            usados.update(nombre for nombre, _ in items)
    restantes = [(nombre, etiqueta) for nombre, etiqueta in campos.items() if nombre not in usados]
    if restantes:
        grupos.append({
            "titulo": "Otros campos",
            "campos": restantes,
            "seleccionados": {nombre for nombre, _ in restantes if nombre in existentes},
        })
    return {"titulo": titulo, "modelo": permission_model_name(modelo), "secciones": grupos}


@superuser_required
def usuarios(request):
    return render(request, "core/administracion_usuarios.html", {
        "usuarios": User.objects.order_by("username"),
    })


@superuser_required
def usuario_nuevo(request):
    if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, "Usuario creado. Asigne sus permisos específicos.")
            return redirect("core:permisos_usuario", pk=usuario.pk)
    else:
        form = UsuarioForm()
    return render(request, "core/usuario_form.html", {"form": form, "titulo": "Crear usuario"})


@superuser_required
def usuario_editar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect("core:usuarios")
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, "core/usuario_form.html", {"form": form, "titulo": "Editar usuario", "usuario": usuario})


@superuser_required
def usuario_eliminar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario == request.user:
        messages.error(request, "No puede eliminar su propio usuario.")
        return redirect("core:usuarios")
    if request.method == "POST":
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente.")
    return redirect("core:usuarios")


@superuser_required
def permisos_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    modelos = [(RegistroTitulacion, "Información del estudiante"), (Acta, "Actas")]
    if request.method == "POST":
        FieldPermission.objects.filter(user=usuario).delete()
        for modelo, _ in modelos:
            permitidos = set(request.POST.getlist(permission_model_name(modelo)))
            validos = {nombre for nombre, _ in _campos(modelo)}
            FieldPermission.objects.bulk_create([
                FieldPermission(user=usuario, model_name=permission_model_name(modelo), field_name=nombre)
                for nombre in permitidos & validos
            ])
        messages.success(request, "Permisos actualizados correctamente.")
        return redirect("core:usuarios")
    existentes = set(FieldPermission.objects.filter(user=usuario).values_list("model_name", "field_name"))
    return render(request, "core/permisos_usuario.html", {
        "usuario": usuario,
        "grupos_campos": [
            _grupos_campos(
                modelo,
                titulo,
                CATEGORIAS_ESTUDIANTE if modelo is RegistroTitulacion else CATEGORIAS_ACTA,
                {field for model_name, field in existentes if model_name == permission_model_name(modelo)},
            )
            for modelo, titulo in modelos
        ],
    })


@superuser_required
def backups(request):
    if request.method == "POST":
        backup = crear_backup(request.user)
        messages.success(request, f"Backup generado: {backup.tamano} bytes.")
        return redirect("core:backups")
    return render(request, "core/backups.html", {"backups": BackupArtifact.objects.select_related("generado_por")})


@superuser_required
def descargar_backup(request, pk):
    backup = get_object_or_404(BackupArtifact, pk=pk)
    try:
        archivo = backup.archivo.open("rb")
    except (FileNotFoundError, OSError, ValueError):
        raise Http404("El backup no existe en el almacenamiento.")
    return FileResponse(archivo, as_attachment=True, filename=backup.archivo.name.rsplit("/", 1)[-1])