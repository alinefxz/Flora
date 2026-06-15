from django.http import JsonResponse
from .models import Categoria, Produto, Substancia, SugestaoTroca, TipoDesregulador
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.views.decorators.http import require_GET, require_POST

from .services import (
    ServicoProdutosIndisponivel,
    consultar_produto_publico,
    gtin_valido,
    limpar_codigo_barras,
)

def listar_categorias(request):
    dados = [
        {
            "id": categoria.id,
            "nome": categoria.nome,
            "descricao": categoria.descricao,
            "total_produtos": categoria.produtos.count(),
        }
        for categoria in Categoria.objects.all()
    ]
    return JsonResponse({"categorias": dados})


def listar_produtos(request):
    produtos = Produto.objects.select_related("categoria").all()
    dados = [
        {
            "id": p.id,
            "nome": p.nome,
            "marca": p.marca,
            "codigo_barras": p.codigo_barras,
            "categoria": p.categoria.nome,
            "fabricante": p.fabricante,
            "nota_flora": p.nota_flora,
        }
        for p in produtos
    ]
    return JsonResponse({"produtos": dados})


def detalhe_produto(request, pk):
    produto = Produto.objects.select_related("categoria").prefetch_related("composicao__ingrediente__substancia").get(pk=pk)
    composicao = [
        {
            "ingrediente": item.ingrediente.nome,
            "funcao_quimica": item.ingrediente.funcao_quimica,
            "substancia": item.ingrediente.substancia.nome if item.ingrediente.substancia else None,
            "concentracao": item.concentracao_estimada,
            "unidade": item.unidade_concentracao,
        }
        for item in produto.composicao.all()
    ]

    return JsonResponse({
        "id": produto.id,
        "nome": produto.nome,
        "marca": produto.marca,
        "categoria": produto.categoria.nome,
        "nota_flora": produto.nota_flora,
        "composicao": composicao,
    })


def listar_substancias(request):
    substancias = Substancia.objects.select_related("tipo_desregulador")
    dados = [
        {
            "id": s.id,
            "nome": s.nome,
            "cas_number": s.cas_number,
            "nivel_risco": s.nivel_risco,
            "tipo_desregulador": s.tipo_desregulador.nome,
        }
        for s in substancias
    ]
    return JsonResponse({"substancias": dados})


def listar_eixos(request):
    dados = [
        {
            "id": eixo.id,
            "nome": eixo.nome,
            "descricao": eixo.descricao,
            "substancias": [s.nome for s in eixo.substancias.all()],
        }
        for eixo in TipoDesregulador.objects.prefetch_related("substancias")
    ]
    return JsonResponse({"eixos": dados})


def listar_sugestoes(request):
    sugestoes = SugestaoTroca.objects.select_related("produto_risco", "produto_seguro", "especialista")
    dados = [
        {
            "produto_risco": s.produto_risco.nome,
            "produto_seguro": s.produto_seguro.nome,
            "justificativa": s.justificativa_tecnica,
            "confianca": s.confianca,
            "especialista": s.especialista.nome_completo if s.especialista else None,
        }
        for s in sugestoes
    ]
    return JsonResponse({"sugestoes": dados})

def produto_json(produto, origem="flora"):
    return {
        "id": produto.pk,
        "nome": produto.nome,
        "marca": produto.marca,
        "codigo_barras": produto.codigo_barras,
        "categoria": produto.categoria.nome,
        "fabricante": produto.fabricante,
        "imagem": (
            produto.imagem.url
            if produto.imagem
            else ""
        ),
        "origem": origem,
    }


@require_GET
@login_required
def verificar_produto(request):
    codigo = limpar_codigo_barras(
        request.GET.get("codigo_barras")
    )

    existente = Produto.objects.select_related(
        "categoria"
    ).filter(
        codigo_barras=codigo
    ).first()

    if existente:
        return JsonResponse({
            "encontrado": True,
            "ja_cadastrado": True,
            "produto": produto_json(existente),
        })

    if not gtin_valido(codigo):
        return JsonResponse(
            {
                "erro": (
                    "O código informado não é um GTIN/EAN válido. "
                    "Confira os números da embalagem."
                )
            },
            status=400,
        )

    try:
        produto = consultar_produto_publico(codigo)
    except ServicoProdutosIndisponivel:
        return JsonResponse(
            {
                "erro": (
                    "A base pública de produtos está indisponível. "
                    "Tente novamente em alguns instantes."
                )
            },
            status=503,
        )

    if not produto:
        return JsonResponse(
            {
                "erro": (
                    "O código é válido, mas o produto não foi "
                    "encontrado na base pública de cosméticos."
                )
            },
            status=404,
        )

    return JsonResponse({
        "encontrado": True,
        "ja_cadastrado": False,
        "produto": {
            **produto,
            "origem": "Open Beauty Facts",
        },
    })


@require_POST
@login_required
def cadastrar_produto(request):
    codigo = limpar_codigo_barras(
        request.POST.get("codigo_barras")
    )

    existente = Produto.objects.select_related(
        "categoria"
    ).filter(
        codigo_barras=codigo
    ).first()

    if existente:
        return JsonResponse({
            "ja_cadastrado": True,
            "produto": produto_json(existente),
        })

    if not gtin_valido(codigo):
        return JsonResponse(
            {"erro": "Informe um código GTIN/EAN válido."},
            status=400,
        )

    try:
        origem = consultar_produto_publico(codigo)
    except ServicoProdutosIndisponivel:
        return JsonResponse(
            {"erro": "Não foi possível validar o produto agora."},
            status=503,
        )

    if not origem:
        return JsonResponse(
            {
                "erro": (
                    "Produto não confirmado na base pública. "
                    "O cadastro não foi realizado."
                )
            },
            status=400,
        )

    try:
        categoria = Categoria.objects.get(
            pk=request.POST.get("categoria")
        )
    except (Categoria.DoesNotExist, ValueError, TypeError):
        return JsonResponse(
            {"erro": "Selecione uma categoria válida."},
            status=400,
        )

    nome = (
        origem["nome"]
        or request.POST.get("nome", "")
    ).strip()

    marca = (
        origem["marca"]
        or request.POST.get("marca", "")
    ).strip()

    if not nome or not marca:
        return JsonResponse(
            {
                "erro": (
                    "Preencha o nome e a marca do produto."
                )
            },
            status=400,
        )

    semelhante = Produto.objects.select_related(
        "categoria"
    ).filter(
        nome__iexact=nome,
        marca__iexact=marca,
    ).first()

    if semelhante:
        return JsonResponse({
            "ja_cadastrado": True,
            "produto": produto_json(semelhante),
        })

    try:
        with transaction.atomic():
            produto = Produto.objects.create(
                nome=nome,
                marca=marca,
                codigo_barras=codigo,
                imagem=request.FILES.get("imagem"),
                categoria=categoria,
                fabricante=(
                    origem["fabricante"]
                    or request.POST.get("fabricante", "")
                ).strip(),
                descricao=request.POST.get(
                    "descricao", ""
                ).strip(),
            )

    except IntegrityError:
        produto = Produto.objects.select_related(
            "categoria"
        ).get(
            codigo_barras=codigo
        )

    return JsonResponse(
        {
            "ja_cadastrado": False,
            "produto": produto_json(produto),
        },
        status=201,
    )