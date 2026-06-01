from django import template

register = template.Library()


@register.filter
def get_attr(obj, attr):
    value = obj

    for part in attr.split("."):
        value = getattr(value, part, "")

    if callable(value):
        value = value()

    if value is True:
        return "Sim"

    if value is False:
        return "Não"

    if value is None or value == "":
        return "-"

    return value


@register.filter
def labelize(value):
    labels = {
        "cpf": "CPF",
        "uf": "UF",
        "id": "ID",
        "cas_number": "CAS",
        "data_nasc": "Data de nascimento",
        "data_inicio": "Data de início",
        "data_fim": "Data de fim",
        "data_ocorrencia": "Data da ocorrência",
        "data_calculo": "Data do cálculo",
        "data_emissao": "Data de emissão",
        "data_envio": "Data de envio",
        "carga_estrogenica": "Carga estrogênica",
        "carga_androgenica": "Carga androgênica",
        "carga_tireoidiana": "Carga tireoidiana",
        "carga_total": "Carga total",
        "nota_flora": "Nota FLORA",
        "tipo_usuario": "Tipo de usuário",
    }

    if value in labels:
        return labels[value]

    return str(value).replace("_", " ").capitalize()