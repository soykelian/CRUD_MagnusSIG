"""Validaciones de captura para contactos e identificaciones colombianas."""

import re
import unicodedata

from django.core.exceptions import ValidationError


def validar_nit(valor):
    """Acepta NIT base de 8 a 10 dígitos, con DV opcional separado por guion."""
    nit = re.sub(r"[.\s]", "", (valor or "").strip())
    if not re.fullmatch(r"\d{8,10}(?:-\d)?", nit):
        raise ValidationError(
            "Ingresa un NIT de 8 a 10 dígitos; el dígito de verificación es opcional "
            "y, si lo incluyes, sepáralo con un guion."
        )
    return nit


def validar_documento_cliente(tipo, valor):
    """Valida el documento de identidad según el tipo seleccionado."""
    documento = (valor or "").strip().upper()
    if tipo == "CC":
        if not re.fullmatch(r"\d{1,10}", documento) or int(documento) == 0:
            raise ValidationError(
                "La cédula de ciudadanía debe contener de 1 a 10 dígitos "
                "y no puede estar compuesta solo por ceros."
            )
    elif tipo == "CE":
        if not re.fullmatch(r"\d{1,12}", documento):
            raise ValidationError(
                "La cédula de extranjería debe contener solo números "
                "y máximo 12 dígitos."
            )
    elif tipo == "NIT":
        return validar_nit(documento)
    elif tipo == "PASAPORTE":
        if not re.fullmatch(r"[A-Z0-9-]{5,20}", documento):
            raise ValidationError(
                "El pasaporte debe tener entre 5 y 20 caracteres alfanuméricos.")
    else:
        raise ValidationError("Selecciona un tipo de documento válido.")
    return documento


def validar_telefono_colombiano(valor):
    """Valida marcación nacional colombiana de 10 dígitos o formato internacional."""
    telefono = (valor or "").strip()
    if not telefono:
        return telefono

    if not re.fullmatch(r"[0-9+().\-\s]+", telefono):
        raise ValidationError(
            "Usa solo números, espacios y los signos + ( ) . -.")

    if telefono.count("+") > 1 or ("+" in telefono and not telefono.lstrip().startswith("+")):
        raise ValidationError(
            "El signo + solo puede aparecer una vez y al inicio del teléfono.")

    digitos = re.sub(r"\D", "", telefono)
    if len(digitos) == 10:
        return telefono
    if digitos.startswith("57") and len(digitos) == 12:
        return telefono
    if telefono.lstrip().startswith("+") and 8 <= len(digitos) <= 15:
        return telefono

    raise ValidationError(
        "En Colombia ingresa 10 dígitos; también se acepta +57 con esos 10 dígitos "
        "o un número internacional de hasta 15 dígitos."
    )


def validar_direccion(valor):
    """Rechaza direcciones vacías o con caracteres no permitidos."""
    direccion = " ".join((valor or "").split())
    if not direccion:
        return direccion
    if len(direccion) < 5:
        raise ValidationError("La dirección debe tener al menos 5 caracteres.")
    if any(unicodedata.category(caracter).startswith("C") for caracter in direccion):
        raise ValidationError(
            "La dirección contiene caracteres no permitidos.")
    if not re.fullmatch(r"[\w\s#.,'’()/\-º°:&+]+", direccion, flags=re.UNICODE):
        raise ValidationError(
            "Revisa la dirección; usa letras, números y signos "
            "habituales (#, -, /, .)."
        )
    if not any(caracter.isalpha() for caracter in direccion):
        raise ValidationError(
            "La dirección debe incluir una vía o referencia con letras.")
    return direccion


def validar_ciudad(valor):
    """Valida los caracteres admitidos en el campo de ciudad."""
    ciudad = " ".join((valor or "").split())
    if not ciudad:
        return ciudad
    if any(unicodedata.category(caracter).startswith("C") for caracter in ciudad):
        raise ValidationError("La ciudad contiene caracteres no permitidos.")
    if not re.fullmatch(r"[\w\s.'’\-]+", ciudad, flags=re.UNICODE):
        raise ValidationError(
            "La ciudad solo puede contener letras, números, espacios, "
            "puntos o guiones."
        )
    if not any(caracter.isalpha() for caracter in ciudad):
        raise ValidationError("Ingresa el nombre de una ciudad.")
    return ciudad
