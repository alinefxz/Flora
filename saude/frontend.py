from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from usuarios.models import Pessoa, Usuario, Especialista, Admin, UF, Cidade, PerfilHormonal
from produtos.models import Categoria, TipoDesregulador, Substancia, Produto, Ingrediente, ProdutoIngrediente, SugestaoTroca, Referencia
from saude.models import ArmarioItem, Sintoma, CicloMenstrual, RegistroSintoma, Exposicao, ExposicaoDetalhe, AlertaRisco, Notificacao
from saude.forms import (
    PessoaForm, UsuarioForm, EspecialistaForm, AdminFloraForm,
    UFForm, CidadeForm, PerfilHormonalForm,
    CategoriaForm, TipoDesreguladorForm, SubstanciaForm, ProdutoForm,
    IngredienteForm, ProdutoIngredienteForm, SugestaoTrocaForm, ReferenciaForm,
    ArmarioItemForm, SintomaForm, CicloMenstrualForm, RegistroSintomaForm,
    ExposicaoForm, ExposicaoDetalheForm, AlertaRiscoForm, NotificacaoForm,
)


ADMIN = "admin"
USUARIA = "usuaria"
ESPECIALISTA = "especialista"


ENTIDADES = {
    "pessoas": {
        "titulo": "Pessoas",
        "subtitulo": "Base geral de contas e perfis do sistema.",
        "grupo": ADMIN,
        "model": Pessoa,
        "form": PessoaForm,
        "campos": ["nome_completo", "email", "cpf", "tipo_usuario", "ativo"],
        "busca": ["nome_completo", "email", "cpf"],
    },
    "usuarias": {
        "titulo": "Usuárias",
        "subtitulo": "Cadastro de usuárias e dados pessoais.",
        "grupo": ADMIN,
        "model": Usuario,
        "form": UsuarioForm,
        "campos": ["nome_completo", "email", "cpf", "data_nasc", "apelido", "ativo"],
        "busca": ["nome_completo", "email", "cpf", "apelido"],
        "filtro": {"tipo_usuario": "USUARIA"},
    },
    "especialistas": {
        "titulo": "Especialistas",
        "subtitulo": "Profissionais responsáveis por análises e sugestões.",
        "grupo": ADMIN,
        "model": Especialista,
        "form": EspecialistaForm,
        "campos": ["nome_completo", "email", "registro_profissional", "especialidade", "ativo"],
        "busca": ["nome_completo", "email", "registro_profissional", "especialidade"],
        "filtro": {"tipo_usuario": "ESPECIALISTA"},
    },
    "administradores": {
        "titulo": "Administradores",
        "subtitulo": "Gestão de perfis administrativos.",
        "grupo": ADMIN,
        "model": Admin,
        "form": AdminFloraForm,
        "campos": ["nome_completo", "email", "nivel_acesso", "ativo", "is_superuser"],
        "busca": ["nome_completo", "email", "nivel_acesso"],
        "filtro": {"tipo_usuario": "ADMIN"},
    },
    "ufs": {
        "titulo": "UFs",
        "subtitulo": "Estados usados no cadastro de cidades.",
        "grupo": ADMIN,
        "model": UF,
        "form": UFForm,
        "campos": ["nome_estado", "sigla"],
        "busca": ["nome_estado", "sigla"],
    },
    "cidades": {
        "titulo": "Cidades",
        "subtitulo": "Cidades vinculadas às UFs.",
        "grupo": ADMIN,
        "model": Cidade,
        "form": CidadeForm,
        "campos": ["nome_cidade", "uf"],
        "busca": ["nome_cidade", "uf__sigla"],
    },
    "perfis-hormonais": {
        "titulo": "Perfis hormonais",
        "subtitulo": "Condições clínicas e sensibilidade hormonal.",
        "grupo": USUARIA,
        "model": PerfilHormonal,
        "form": PerfilHormonalForm,
        "campos": ["usuario", "uso_contraceptivo", "condicao_hormonal", "ciclo_regular", "duracao_ciclo", "fluxo_menstrual", "peso_sensibilidade"],
        "busca": ["usuario__nome_completo", "condicao_hormonal"],
    },
    "categorias": {
        "titulo": "Categorias",
        "subtitulo": "Grupos de produtos, como maquiagem, higiene e plásticos.",
        "grupo": ADMIN,
        "model": Categoria,
        "form": CategoriaForm,
        "campos": ["nome", "descricao"],
        "busca": ["nome", "descricao"],
    },
    "produtos": {
        "titulo": "Produtos",
        "subtitulo": "Produtos analisados pelo FLORA.",
        "grupo": ADMIN,
        "model": Produto,
        "form": ProdutoForm,
        "campos": ["nome", "marca", "codigo_barras", "categoria", "fabricante", "nota_flora"],
        "busca": ["nome", "marca", "codigo_barras", "fabricante"],
    },
    "ingredientes": {
        "titulo": "Ingredientes",
        "subtitulo": "Ingredientes rotulados e sua função química.",
        "grupo": ADMIN,
        "model": Ingrediente,
        "form": IngredienteForm,
        "campos": ["nome", "funcao_quimica", "substancia"],
        "busca": ["nome", "funcao_quimica", "substancia__nome"],
    },
    "composicoes": {
        "titulo": "Composição dos produtos",
        "subtitulo": "Relação entre produtos, ingredientes e concentrações.",
        "grupo": ADMIN,
        "model": ProdutoIngrediente,
        "form": ProdutoIngredienteForm,
        "campos": ["produto", "ingrediente", "concentracao_estimada", "unidade_concentracao"],
        "busca": ["produto__nome", "ingrediente__nome"],
    },
    "substancias": {
        "titulo": "Substâncias",
        "subtitulo": "Desreguladores endócrinos e seus mecanismos de ação.",
        "grupo": ADMIN,
        "model": Substancia,
        "form": SubstanciaForm,
        "campos": ["nome", "cas_number", "nivel_risco", "tipo_desregulador"],
        "busca": ["nome", "cas_number", "tipo_desregulador__nome"],
    },
    "tipos-desreguladores": {
        "titulo": "Eixos hormonais",
        "subtitulo": "Tipos de interferência hormonal.",
        "grupo": ADMIN,
        "model": TipoDesregulador,
        "form": TipoDesreguladorForm,
        "campos": ["nome", "descricao"],
        "busca": ["nome", "descricao"],
    },
    "armario": {
        "titulo": "Armário virtual",
        "subtitulo": "Produtos usados pelas usuárias e frequência de uso.",
        "grupo": USUARIA,
        "model": ArmarioItem,
        "form": ArmarioItemForm,
        "campos": ["usuario", "produto", "frequencia_uso"],
        "busca": ["usuario__nome_completo", "produto__nome"],
    },
    "sintomas": {
        "titulo": "Sintomas",
        "subtitulo": "Catálogo de sintomas acompanhados pelo FLORA.",
        "grupo": USUARIA,
        "model": Sintoma,
        "form": SintomaForm,
        "campos": ["nome", "descricao"],
        "busca": ["nome", "descricao"],
    },
    "registros-sintomas": {
        "titulo": "Registro de sintomas",
        "subtitulo": "Histórico cronológico de sintomas das usuárias.",
        "grupo": USUARIA,
        "model": RegistroSintoma,
        "form": RegistroSintomaForm,
        "campos": ["usuario", "sintoma", "data_ocorrencia", "intensidade", "fase_ciclo"],
        "busca": ["usuario__nome_completo", "sintoma__nome", "fase_ciclo"],
    },
    "ciclos": {
        "titulo": "Ciclos menstruais",
        "subtitulo": "Registro de início, fim e duração do ciclo.",
        "grupo": USUARIA,
        "model": CicloMenstrual,
        "form": CicloMenstrualForm,
        "campos": ["usuario", "data_inicio", "data_fim", "duracao"],
        "busca": ["usuario__nome_completo", "observacoes"],
    },
    "exposicoes": {
        "titulo": "Exposições",
        "subtitulo": "Carga hormonal consolidada.",
        "grupo": USUARIA,
        "model": Exposicao,
        "form": ExposicaoForm,
        "campos": ["usuario", "carga_estrogenica", "carga_androgenica", "carga_tireoidiana", "carga_total", "data_calculo"],
        "busca": ["usuario__nome_completo"],
    },
    "detalhes-exposicao": {
        "titulo": "Detalhes da exposição",
        "subtitulo": "Contribuição de produtos e substâncias no cálculo.",
        "grupo": ESPECIALISTA,
        "model": ExposicaoDetalhe,
        "form": ExposicaoDetalheForm,
        "campos": ["exposicao", "produto", "substancia", "valor_contribuicao"],
        "busca": ["produto__nome", "substancia__nome", "exposicao__usuario__nome_completo"],
    },
    "sugestoes": {
        "titulo": "Sugestões de troca",
        "subtitulo": "Produtos seguros equivalentes aos produtos de risco.",
        "grupo": ESPECIALISTA,
        "model": SugestaoTroca,
        "form": SugestaoTrocaForm,
        "campos": ["produto_risco", "produto_seguro", "confianca", "especialista"],
        "busca": ["produto_risco__nome", "produto_seguro__nome", "especialista__nome_completo"],
    },
    "referencias": {
        "titulo": "Referências científicas",
        "subtitulo": "Artigos, DOI e fontes vinculadas às substâncias.",
        "grupo": ESPECIALISTA,
        "model": Referencia,
        "form": ReferenciaForm,
        "campos": ["titulo_artigo", "autores", "ano_publicacao", "substancia"],
        "busca": ["titulo_artigo", "autores", "substancia__nome"],
    },
    "alertas": {
        "titulo": "Alertas de risco",
        "subtitulo": "Mensagens emitidas com base no perfil e exposição.",
        "grupo": USUARIA,
        "model": AlertaRisco,
        "form": AlertaRiscoForm,
        "campos": ["usuario", "nivel_gravidade", "mensagem_alerta", "data_emissao"],
        "busca": ["usuario__nome_completo", "mensagem_alerta", "nivel_gravidade"],
    },
    "notificacoes": {
        "titulo": "Notificações",
        "subtitulo": "Comunicações enviadas para usuárias.",
        "grupo": USUARIA,
        "model": Notificacao,
        "form": NotificacaoForm,
        "campos": ["usuario", "tipo_notificacao", "mensagem", "lida", "data_envio"],
        "busca": ["usuario__nome_completo", "tipo_notificacao", "mensagem"],
    },
}


def menu_context():
    grupos = {
        ADMIN: [],
        USUARIA: [],
        ESPECIALISTA: [],
    }

    for slug, config in ENTIDADES.items():
        grupos[config["grupo"]].append({"slug": slug, "titulo": config["titulo"]})

    return grupos


def get_config(slug):
    if slug not in ENTIDADES:
        raise PermissionDenied("Página não encontrada.")
    return ENTIDADES[slug]


def get_queryset(config, request):
    qs = config["model"].objects.all()

    if "filtro" in config:
        qs = qs.filter(**config["filtro"])

    q = request.GET.get("q", "").strip()
    if q:
        filtro = Q()
        for campo in config.get("busca", []):
            filtro |= Q(**{f"{campo}__icontains": q})
        qs = qs.filter(filtro)

    return qs


def dashboard(request):
    total_usuarias = Usuario.objects.filter(tipo_usuario="USUARIA").count()
    total_produtos = Produto.objects.count()
    total_substancias = Substancia.objects.count()
    total_alertas = AlertaRisco.objects.count()
    exposicao = Exposicao.objects.order_by("-data_calculo").first()

    contexto = {
        "menu": menu_context(),
        "total_usuarias": total_usuarias,
        "total_produtos": total_produtos,
        "total_substancias": total_substancias,
        "total_alertas": total_alertas,
        "exposicao": exposicao,
    }
    return render(request, "dashboard.html", contexto)


def lista(request, slug):
    config = get_config(slug)
    objetos = get_queryset(config, request)

    contexto = {
        "menu": menu_context(),
        "slug": slug,
        "config": config,
        "objetos": objetos,
        "campos": config["campos"],
        "q": request.GET.get("q", ""),
    }
    return render(request, "lista.html", contexto)


def detalhe(request, slug, pk):
    config = get_config(slug)
    obj = get_object_or_404(config["model"], pk=pk)

    contexto = {
        "menu": menu_context(),
        "slug": slug,
        "config": config,
        "obj": obj,
        "campos": [field.name for field in obj._meta.fields],
    }
    return render(request, "detalhe.html", contexto)


def criar(request, slug):
    config = get_config(slug)
    form_class = config["form"]

    if request.method == "POST":
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Registro criado com sucesso.")
            return redirect("saude:lista", slug=slug)
    else:
        form = form_class()

    return render(request, "formulario.html", {
        "menu": menu_context(),
        "slug": slug,
        "config": config,
        "form": form,
        "modo": "Novo registro",
    })


def editar(request, slug, pk):
    config = get_config(slug)
    obj = get_object_or_404(config["model"], pk=pk)
    form_class = config["form"]

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Registro atualizado com sucesso.")
            return redirect("saude:lista", slug=slug)
    else:
        form = form_class(instance=obj)

    return render(request, "formulario.html", {
        "menu": menu_context(),
        "slug": slug,
        "config": config,
        "form": form,
        "modo": "Editar registro",
    })


def excluir(request, slug, pk):
    config = get_config(slug)
    obj = get_object_or_404(config["model"], pk=pk)

    if request.method == "POST":
        obj.delete()
        messages.success(request, "Registro excluído com sucesso.")
        return redirect("saude:lista", slug=slug)

    return render(request, "confirmar_exclusao.html", {
        "menu": menu_context(),
        "slug": slug,
        "config": config,
        "obj": obj,
    })