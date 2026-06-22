from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from .models import Cidade, UF, Usuario
from .services import (
    ServicoMunicipiosIndisponivel,
    validar_municipio_ibge,
)

UFS_BRASIL = [
    ("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"),
    ("BA", "Bahia"), ("CE", "Ceará"), ("DF", "Distrito Federal"),
    ("ES", "Espírito Santo"), ("GO", "Goiás"), ("MA", "Maranhão"),
    ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"), ("MG", "Minas Gerais"),
    ("PA", "Pará"), ("PB", "Paraíba"), ("PR", "Paraná"), ("PE", "Pernambuco"),
    ("PI", "Piauí"), ("RJ", "Rio de Janeiro"), ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), ("RR", "Roraima"),
    ("SC", "Santa Catarina"), ("SP", "São Paulo"), ("SE", "Sergipe"),
    ("TO", "Tocantins"),
]


def garantir_ufs():
    existentes = set(UF.objects.values_list("sigla", flat=True))
    novas = [
        UF(sigla=sigla, nome_estado=nome)
        for sigla, nome in UFS_BRASIL
        if sigla not in existentes
    ]

    if novas:
        UF.objects.bulk_create(novas, ignore_conflicts=True)


UFS_BRASIL = [
    ("AC", "Acre"),
    ("AL", "Alagoas"),
    ("AP", "Amapá"),
    ("AM", "Amazonas"),
    ("BA", "Bahia"),
    ("CE", "Ceará"),
    ("DF", "Distrito Federal"),
    ("ES", "Espírito Santo"),
    ("GO", "Goiás"),
    ("MA", "Maranhão"),
    ("MT", "Mato Grosso"),
    ("MS", "Mato Grosso do Sul"),
    ("MG", "Minas Gerais"),
    ("PA", "Pará"),
    ("PB", "Paraíba"),
    ("PR", "Paraná"),
    ("PE", "Pernambuco"),
    ("PI", "Piauí"),
    ("RJ", "Rio de Janeiro"),
    ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"),
    ("RO", "Rondônia"),
    ("RR", "Roraima"),
    ("SC", "Santa Catarina"),
    ("SP", "São Paulo"),
    ("SE", "Sergipe"),
    ("TO", "Tocantins"),
]


def garantir_ufs():
    existentes = set(UF.objects.values_list("sigla", flat=True))
    novas = [
        UF(sigla=sigla, nome_estado=nome)
        for sigla, nome in UFS_BRASIL
        if sigla not in existentes
    ]

    if novas:
        UF.objects.bulk_create(novas, ignore_conflicts=True)


@require_GET
def listar_ufs(request):
    garantir_ufs()

    dados = [
        {
            "id": uf.id,
            "sigla": uf.sigla,
            "nome_estado": uf.nome_estado,
        }
        for uf in UF.objects.order_by("sigla")
    ]

    return JsonResponse({"ufs": dados})


@require_GET
def cidades_por_uf(request, uf_id):
    garantir_ufs()
    cidades = Cidade.objects.filter(uf_id=uf_id).select_related("uf")

    dados = [
        {
            "id": cidade.id,
            "nome_cidade": cidade.nome_cidade,
            "nome": str(cidade),
        }
        for cidade in cidades
    ]

    return JsonResponse({"cidades": dados})

@require_POST
def cadastrar_cidade(request):
    garantir_ufs()

    nome = " ".join(request.POST.get("nome_cidade", "").split())
    uf_id = request.POST.get("uf", "").strip()

    if not nome:
        return JsonResponse({"erro": "Digite o nome da cidade."}, status=400)

    try:
        uf = UF.objects.get(pk=uf_id)
    except (UF.DoesNotExist, ValueError):
        return JsonResponse({"erro": "Selecione um estado válido."}, status=400)

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

    cidade, _ = Cidade.objects.get_or_create(
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