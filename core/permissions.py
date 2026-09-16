from django.core.exceptions import PermissionDenied

from .models import FieldPermission


def permission_model_name(model):
    return f"{model._meta.app_label}.{model._meta.model_name}"


def is_full_operator(user):
    if not user or not user.is_authenticated or not user.is_active:
        return False
    return user.is_superuser


def user_can_edit_field(user, model, field):
    if not user or not user.is_authenticated or not user.is_active:
        return False
    if is_full_operator(user):
        return True
    return FieldPermission.objects.filter(
        user=user,
        model_name=permission_model_name(model),
        field_name=field,
    ).exists()


def allowed_edit_fields(user, model):
    if is_full_operator(user):
        return {
            field.name
            for field in model._meta.fields
            if field.editable and not field.auto_created
        }
    model_name = permission_model_name(model)
    return set(
        FieldPermission.objects.filter(
            user=user,
            model_name=model_name,
        ).values_list("field_name", flat=True)
    )


def reject_unauthorized_fields(user, model, submitted_fields):
    unauthorized = set(submitted_fields) - allowed_edit_fields(user, model)
    if unauthorized:
        raise PermissionDenied(
            "No tiene permiso para modificar: "
            + ", ".join(sorted(unauthorized))
        )