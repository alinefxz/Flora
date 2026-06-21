import json
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.core.cache import cache


IBGE_MUNICIPIOS_URL = (
    "https://servicodados.ibge.gov.br/api/v1/localidades/"
    "estados/{uf}/municipios"
)


class ServicoMunicipiosIndisponivel(Exception):
    """Indica que o IBGE não pôde ser consultado."""


def normalizar_texto(valor):
    texto = unicodedata.normalize("NFKD", (valor or "").strip())
    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )

    return " ".join(texto.split()).casefold()


def municipios_oficiais(uf):
    sigla = (uf or "").strip().upper()
    cache_key = f"flora:ibge:municipios:{sigla}"

    municipios = cache.get(cache_key)

    if municipios is not None:
        return municipios

    request = Request(
        IBGE_MUNICIPIOS_URL.format(uf=sigla),
        headers={
            "User-Agent": "Flora/1.0 - validacao de municipios"
        },
    )

    try:
        with urlopen(request, timeout=8) as response:
            dados = json.load(response)
    except (HTTPError, URLError, TimeoutError, ValueError) as erro:
        raise ServicoMunicipiosIndisponivel from erro

    municipios = [
        {
            "id_ibge": item["id"],
            "nome": item["nome"],
        }
        for item in dados
        if item.get("id") and item.get("nome")
    ]

    cache.set(
        cache_key,
        municipios,
        timeout=60 * 60 * 24 * 7,
    )

    return municipios


def validar_municipio_ibge(nome, uf):
    nome_normalizado = normalizar_texto(nome)

    if len(nome_normalizado) < 2:
        return None

    for municipio in municipios_oficiais(uf):
        nome_oficial = normalizar_texto(municipio["nome"])

        if nome_oficial == nome_normalizado:
            return municipio

    return None