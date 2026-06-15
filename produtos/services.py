import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.core.cache import cache


OPEN_BEAUTY_FACTS_URL = (
    "https://world.openbeautyfacts.org/api/v2/product/{codigo}.json"
)


class ServicoProdutosIndisponivel(Exception):
    """Indica que a base pública não pôde ser consultada."""


def limpar_codigo_barras(valor):
    return "".join(
        caractere
        for caractere in (valor or "")
        if caractere.isdigit()
    )


def gtin_valido(valor):
    codigo = limpar_codigo_barras(valor)

    if len(codigo) not in {8, 12, 13, 14}:
        return False

    corpo = codigo[:-1]

    soma = sum(
        int(digito) * (3 if indice % 2 == 0 else 1)
        for indice, digito in enumerate(reversed(corpo))
    )

    digito_verificador = (10 - soma % 10) % 10

    return digito_verificador == int(codigo[-1])


def consultar_produto_publico(valor):
    codigo = limpar_codigo_barras(valor)
    cache_key = f"flora:openbeautyfacts:{codigo}"

    produto_cache = cache.get(cache_key)

    if produto_cache is not None:
        return produto_cache or None

    request = Request(
        OPEN_BEAUTY_FACTS_URL.format(
            codigo=quote(codigo)
        ),
        headers={
            "User-Agent": "Flora/1.0 - catalogo de cosmeticos"
        },
    )

    try:
        with urlopen(request, timeout=8) as response:
            dados = json.load(response)

    except HTTPError as erro:
        if erro.code == 404:
            cache.set(cache_key, {}, timeout=60 * 60 * 6)
            return None

        raise ServicoProdutosIndisponivel from erro

    except (URLError, TimeoutError, ValueError) as erro:
        raise ServicoProdutosIndisponivel from erro

    if dados.get("status") != 1 or not dados.get("product"):
        cache.set(cache_key, {}, timeout=60 * 60 * 6)
        return None

    origem = dados["product"]

    produto = {
        "codigo_barras": codigo,
        "nome": (
            origem.get("product_name_pt")
            or origem.get("product_name")
            or ""
        ).strip(),
        "marca": (
            origem.get("brands") or ""
        ).split(",")[0].strip(),
        "fabricante": (
            origem.get("manufacturing_places") or ""
        ).strip(),
        "imagem": (
            origem.get("image_front_url")
            or origem.get("image_url")
            or ""
        ),
    }

    cache.set(
        cache_key,
        produto,
        timeout=60 * 60 * 24,
    )

    return produto