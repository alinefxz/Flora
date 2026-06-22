from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from .models import Cidade, UF, Pessoa, Usuario  # Adicionado Usuario para a listagem
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

@require_GET
def listar_ufs(request):
    garantir_ufs()
    dados = [{"id": uf.id, "sigla": uf.sigla, "nome_estado": uf.nome_estado} 
             for uf in UF.objects.order_by("sigla")]
    return JsonResponse({"ufs": dados})

@require_GET
def cidades_por_uf(request, uf_id):
    cidades = Cidade.objects.filter(uf_id=uf_id).select_related("uf")
    dados = [{"id": city.id, "nome_cidade": city.nome_cidade, "nome": str(city)} 
             for city in cidades]
    return JsonResponse({"cidades": dados})

@require_POST
def cadastrar_cidade(request):
    # CORREÇÃO 1: Removido o parêntese extra que causava SyntaxError no final da linha
    nome = " ".join(request.POST.get("nome_cidade", "").split())
    uf_id = request.POST.get("uf", "").strip()
    
    if not nome:
        return JsonResponse({"erro": "Digite o nome da cidade."}, status=400)
        
    # CORREÇÃO 2: Separação dos blocos de erro para dar respostas mais precisas
    try:
        uf = UF.objects.get(pk=uf_id)
    except (UF.DoesNotExist, ValueError):
        return JsonResponse({"erro": "Estado (UF) não encontrado ou inválido."}, status=404)

    try:
        municipio = validar_municipio_ibge(nome, uf.sigla)
    except ServicoMunicipiosIndisponivel:
        # Usando a exceção que estava importada mas sem uso
        return JsonResponse({"erro": "O serviço do IBGE está indisponível no momento. Tente novamente mais tarde."}, status=503)
    except Exception:
        return JsonResponse({"erro": "Erro inesperado ao validar a cidade junto ao IBGE."}, status=400)

    if not municipio:
        return JsonResponse({"erro": "Cidade não encontrada no registro oficial do IBGE."}, status=400)

    cidade, created = Cidade.objects.get_or_create(nome_cidade=municipio["nome"], uf=uf)
    
    if not created:
        return JsonResponse({
            "mensagem": "Esta cidade já estava cadastrada no sistema.",
            "cidade": {"id": cidade.pk, "nome": str(cidade), "uf": uf.sigla}
        }, status=200)

    return JsonResponse({
        "cidade": {"id": cidade.pk, "nome": str(cidade), "uf": uf.sigla}
    }, status=201)

@require_GET
def listar_usuarias(request):
    # CORREÇÃO 3: Alterado de Pessoa para Usuario para evitar erros caso 'apelido' pertença apenas ao model Usuario.
    # CORREÇÃO 4: Adicionado .select_related("cidade") para evitar o problema de N+1 queries no banco de dados.
    usuarias = Usuario.objects.select_related("cidade").all()
    
    dados = [{
        "id": u.id, 
        "nome_completo": u.nome_completo, 
        "apelido": getattr(u, "apelido", None), # Seguro contra falhas estruturais
        "email": u.email, 
        "cpf": getattr(u, "cpf_mascarado", u.cpf), 
        "cidade": str(u.cidade) if u.cidade else None
    } for u in usuarias]
    
    return JsonResponse({"usuarias": dados})

