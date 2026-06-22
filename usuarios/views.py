from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from .models import Cidade, UF, Usuario
from .services import (
    ServicoMunicipiosIndisponivel,
    validar_municipio_ibge,
)


@require_GET
def listar_ufs(request):
    ufs = (
        UF.objects
        .order_by("sigla")
        .values(
            "id",
            "sigla",
            "nome_estado",
        )
    )

    return JsonResponse({
        "ufs": list(ufs)
    })


@require_GET
def cidades_por_uf(request, uf_id):
    uf = get_object_or_404(UF, pk=uf_id)

    cidades = (
        Cidade.objects
        .filter(uf=uf)
        .order_by("nome_cidade")
        .values(
            "id",
            "nome_cidade",
        )
    )

    return JsonResponse({
        "cidades": list(cidades)
    })


@require_POST
def cadastrar_cidade(request):
    nome = " ".join(
        request.POST.get(
            "nome_cidade",
            ""
        ).split()
    )

    uf_id = request.POST.get(
        "uf",
        ""
    ).strip()

    if not nome:
        return JsonResponse(
            {
                "erro": "Digite o nome da cidade."
            },
            status=400
        )

    try:
        uf = UF.objects.get(pk=uf_id)

    except UF.DoesNotExist:
        return JsonResponse(
            {
                "erro": "UF não encontrada."
            },
            status=404
        )

    try:
        municipio = validar_municipio_ibge(
            nome,
            uf.sigla
        )

    except ServicoMunicipiosIndisponivel:
        return JsonResponse(
            {
                "erro": (
                    "O serviço do IBGE está "
                    "temporariamente indisponível."
                )
            },
            status=503
        )

    except Exception:
        return JsonResponse(
            {
                "erro": "Erro ao validar cidade."
            },
            status=400
        )

    if not municipio:
        return JsonResponse(
            {
                "erro": "Cidade não encontrada no IBGE."
            },
            status=400
        )

    cidade, created = Cidade.objects.get_or_create(
        nome_cidade=municipio["nome"],
        uf=uf,
    )

    if not created:
        return JsonResponse(
            {
                "mensagem": (
                    "Esta cidade já estava cadastrada."
                ),
                "cidade": {
                    "id": cidade.pk,
                    "nome": str(cidade),
                    "uf": uf.sigla,
                },
            },
            status=200,
        )

    return JsonResponse(
        {
            "cidade": {
                "id": cidade.pk,
                "nome": str(cidade),
                "uf": uf.sigla,
            }
        },
        status=201,
    )


@require_GET
def listar_usuarias(request):
    usuarias = (
        Usuario.objects
        .filter(tipo_usuario="USUARIA")
        .select_related("cidade")
    )

    dados = [
        {
            "id": u.id,
            "nome_completo": u.nome_completo,
            "apelido": u.apelido,
            "email": u.email,
            "cpf": u.cpf_mascarado,
            "cidade": (
                str(u.cidade)
                if u.cidade
                else None
            ),
        }
        for u in usuarias
    ]

    return JsonResponse({
        "usuarias": dados
    })