import gzip
import json
from io import BytesIO
from itertools import chain

from django.core import serializers
from django.db import connection
from django.utils import timezone

from .models import BackupArtifact


def crear_backup(usuario):
    objetos = serializers.serialize(
        "json",
        chain.from_iterable(
            model.objects.all() for model in _modelos_de_aplicacion()
        ),
        use_natural_foreign_keys=False,
        use_natural_primary_keys=False,
    )
    payload = {
        "version": 1,
        "database_engine": connection.vendor,
        "created_at": timezone.now().isoformat(),
        "restore": "python manage.py migrate && python manage.py loaddata data.json",
        "data": json.loads(objetos),
    }
    contenido = gzip.compress(
        json.dumps(payload, ensure_ascii=False).encode("utf-8")
    )
    nombre = f"backup-{timezone.now():%Y%m%d-%H%M%S}.json.gz"
    backup = BackupArtifact(generado_por=usuario, formato="json.gz")
    backup.archivo.save(nombre, BytesIO(contenido), save=False)
    backup.tamano = len(contenido)
    backup.save()
    return backup


def _modelos_de_aplicacion():
    from django.apps import apps

    return [
        model
        for model in apps.get_models()
        if model._meta.app_label not in {"admin", "contenttypes", "sessions"}
    ]