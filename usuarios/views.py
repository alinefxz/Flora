from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Cidade, UF, Usuario
from .services import (
    ServicoMunicipiosIndisponivel,
    validar_municipio_ibge,
)


def listar_ufs(request):
    dados = [
        {
            "id": uf.id,
            "sigla": uf.sigla,
            "nome_estado": uf.nome_estado,
        }
        for uf in UF.objects.all()
    ]

    return JsonResponse({"ufs": dados})


def cidades_por_uf(request, uf_id):
    cidades = Cidade.objects.filter(uf_id=uf_id)

    dados = [
        {
            "id": cidade.id,
            "nome_cidade": cidade.nome_cidade,
        }
        for cidade in cidades
    ]

    return JsonResponse({"cidades": dados})


@require_POST
def cadastrar_cidade(request):
    nome = request.POST.get("nome_cidade", "").strip()
    uf_id = request.POST.get("uf", "").strip()

    try:
        uf = UF.objects.get(pk=uf_id)
    except (UF.DoesNotExist, ValueError):
        return JsonResponse(
            {"erro": "Selecione um estado válido."},
            status=400,
        )

    try:
        municipio = validar_municipio_ibge(nome, uf.sigla)
    except ServicoMunicipiosIndisponivel:
        return JsonResponse(
            {
                "erro": (
                    "Não foi possível consultar o IBGE agora. "
                    "Tente novamente em alguns instantes."
                )
            },
            status=503,
        )

    if not municipio:
        return JsonResponse(
            {
                "erro": (
                    "Essa cidade não foi encontrada na lista oficial "
                    f"do IBGE para {uf.sigla}."
                )
            },
            status=400,
        )

    cidade = Cidade.objects.filter(
        nome_cidade__iexact=municipio["nome"],
        uf=uf,
    ).first()

    if not cidade:
        cidade = Cidade.objects.create(
            nome_cidade=municipio["nome"],
            uf=uf,
        )

    return JsonResponse(
        {
            "cidade": {
                "id": cidade.pk,
                "nome": str(cidade),
                "nome_cidade": cidade.nome_cidade,
                "uf": uf.sigla,
                "id_ibge": municipio["id_ibge"],
            }
        },
        status=201,
    )


def listar_usuarias(request):
    usuarias = Usuario.objects.select_related(
        "cidade",
        "cidade__uf",
    )

    dados = [
        {
            "id": usuaria.id,
            "nome_completo": usuaria.nome_completo,
            "apelido": usuaria.apelido,
            "email": usuaria.email,
            "cpf": usuaria.cpf_mascarado,
            "cidade": (
                str(usuaria.cidade)
                if usuaria.cidade
                else None
            ),
        }
        for usuaria in usuarias
    ]

    return JsonResponse({"usuarias": dados})