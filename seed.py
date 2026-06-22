import os
import django
import random
from django.apps import apps
from django.db import models

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
try:
    django.setup()
except Exception:
    pass

# Importações dinâmicas via apps.get_model
UF = apps.get_model('usuarios', 'UF')
Cidade = apps.get_model('usuarios', 'Cidade')
Usuario = apps.get_model('usuarios', 'Usuario')
Pessoa = apps.get_model('usuarios', 'Pessoa')
Categoria = apps.get_model('produtos', 'Categoria')
Substancia = apps.get_model('produtos', 'Substancia')
Ingrediente = apps.get_model('produtos', 'Ingrediente')
Produto = apps.get_model('produtos', 'Produto')
ProdutoIngrediente = apps.get_model('produtos', 'ProdutoIngrediente')

try:
    TipoDesregulador = apps.get_model('produtos', 'TipoDesregulador')
except LookupError:
    TipoDesregulador = apps.get_model('produtos', 'TipobDesregulador')

try:
    Sintoma = apps.get_model('saude', 'Sintoma')
except LookupError:
    Sintoma = None

try:
    ArmarioItem = apps.get_model('saude', 'ArmarioItem')
except LookupError:
    try:
        ArmarioItem = apps.get_model('produtos', 'ArmarioItem')
    except LookupError:
        ArmarioItem = None

try:
    Exposicao = apps.get_model('saude', 'Exposicao')
except LookupError:
    Exposicao = None

print("🔄 Iniciando carga e interconexão total de dados...")

# 1. Criação de UFs e Cidades (removido o prefixo 'Metrópole' e mantido padrão)
ufs_dados = [
    ("SP", "São Paulo"), 
    ("RJ", "Rio de Janeiro"), 
    ("MG", "Minas Gerais"), 
    ("BA", "Bahia"), 
    ("PR", "Paraná")
]
cidades_instancias = []

for sigla, nome_est in ufs_dados:
    uf, _ = UF.objects.get_or_create(sigla=sigla, defaults={"nome_estado": nome_est})
    # Corrigido aqui: a cidade agora salva exatamente o nome correto
    cidade, _ = Cidade.objects.get_or_create(nome_cidade=nome_est, uf=uf)
    cidades_instancias.append(cidade)

# 2. Eixos de Desreguladores Hormonais
eixos_nomes = ["Estrogênico", "Androgênico", "Tireoidiano", "Metabólico", "Cortisol"]
eixos_instancias = []
for nome in eixos_nomes:
    eixo, _ = TipoDesregulador.objects.get_or_create(
        nome=nome, 
        defaults={"descricao": f"Impacto biológico no eixo {nome.lower()}"}
    )
    eixos_instancias.append(eixo)

# 3. Substâncias com Alta Classificação de Risco
substancias_dados = [
    {"nome": "Bisfenol A (BPA)", "cas": "80-05-7", "risco": 5, "eixo": eixos_instancias[0]},
    {"nome": "Ftalato de Dibutila (DBP)", "cas": "84-74-2", "risco": 5, "eixo": eixos_instancias[1]},
    {"nome": "Triclosan", "cas": "3380-34-5", "risco": 4, "eixo": eixos_instancias[2]},
    {"nome": "Parabeno de Metila", "cas": "99-76-3", "risco": 4, "eixo": eixos_instancias[3]},
    {"nome": "Filtro UV Benzofenona", "cas": "119-61-9", "risco": 4, "eixo": eixos_instancias[1]}
]

substancias_instancias = []
for s in substancias_dados:
    sub, _ = Substancia.objects.get_or_create(
        cas_number=s["cas"],
        defaults={
            "nome": s["nome"],
            "nivel_risco": s["risco"],
            "tipo_desregulador": s["eixo"],
            "mecanismo_acao": "Interferência direta nos receptores celulares hormonais."
        }
    )
    substancias_instancias.append(sub)

# 4. Ingredientes mapeados às Substâncias
ingredientes_instancias = []
for i, sub in enumerate(substancias_instancias):
    ing, _ = Ingrediente.objects.get_or_create(
        nome=f"Componente Químico Ativo {i+1}",
        defaults={
            "funcao_quimica": "Conservante / Plastificante Estabilizante",
            "substancia": sub
        }
    )
    ingredientes_instancias.append(ing)

# 5. Categorias
cat_nomes = ["Skincare", "Maquiagem", "Cabelo", "Corpo", "Higiene Íntima"]
categorias_instancias = []
for nome in cat_nomes:
    cat, _ = Categoria.objects.get_or_create(nome=nome)
    categorias_instancias.append(cat)

# 6. Produtos com Risco Vinculado para Forçar Nota Baixa na Tela Inicial
produtos_instancias = []
for i in range(5):
    prod, _ = Produto.objects.get_or_create(
        codigo_barras=f"789123456000{i}",
        defaults={
            "nome": f"Produto de Risco Oculto {i+1}",
            "marca": f"Marca Comercial {i+1}",
            "categoria": categorias_instancias[i],
            "fabricante": "Indústria Cosmética S.A."
        }
    )
    
    ProdutoIngrediente.objects.get_or_create(
        produto=prod,
        ingrediente=ingredientes_instancias[i],
        defaults={
            "concentracao_estimada": 0.9,
            "unidade_concentracao": "%"
        }
    )
    
    if hasattr(prod, 'recalcular_nota_flora'):
        prod.recalcular_nota_flora(salvar=True)
    produtos_instancias.append(prod)

# 7. Sintomas
if Sintoma:
    sintomas = ["Acne Severa", "Enxaqueca", "Fadiga Crônica", "Queda de Cabelo", "Cólicas Intensas"]
    for s in sintomas:
        Sintoma.objects.get_or_create(nome=s, defaults={"descricao": f"Sintoma associado a desequilíbrios."})

# 8. Usuárias, Armários e Atualização da Tela Inicial (Radar)
for i in range(1, 6):
    username_usr = f"usuaria{i}"
    usr, created = Usuario.objects.get_or_create(
        username=username_usr,
        defaults={
            "email": f"{username_usr}@teste.com",
            "nome_completo": f"Usuária Simulação {i}",
            "cpf": f"0000000000{i}",
            "tipo_usuario": "USUARIA",
            "cidade": cidades_instancias[i-1]
        }
    )
    if created:
        usr.set_password("senha_segura123")
        usr.save()

    if ArmarioItem:
        for p in produtos_instancias[:3]:
            kwargs = {}
            for field in ArmarioItem._meta.fields:
                if field.is_relation and field.related_model in [Usuario, Pessoa]:
                    kwargs[field.name] = usr
                elif field.is_relation and field.related_model == Produto:
                    kwargs[field.name] = p
                elif field.name in ["frequencia", "frequencia_uso"]:
                    kwargs[field.name] = 3.0

            lookup_kwargs = {k: v for k, v in kwargs.items() if k in ["usuario", "pessoa", "user", "produto"]}
            ArmarioItem.objects.get_or_create(**lookup_kwargs, defaults=kwargs)

    # População do Gráfico do Radar da Tela Inicial
    if Exposicao:
        if not Exposicao.objects.filter(usuario=usr).exists():
            ce = round(random.uniform(3.8, 5.0), 2)
            ca = round(random.uniform(2.5, 4.2), 2)
            ct = round(random.uniform(2.0, 3.9), 2)
            Exposicao.objects.create(
                usuario=usr,
                carga_estrogenica=ce,
                carga_androgenica=ca,
                carga_tireoidiana=ct,
                carga_total=round(ce + ca + ct, 2)
            )

# Sincroniza também as contas principais do sistema para que os gráficos carreguem dados reais
for usuario_atual in Usuario.objects.filter(tipo_usuario="USUARIA"):
    if Exposicao and not Exposicao.objects.filter(usuario=usuario_atual).exists():
        try:
            Exposicao.objects.create(
                usuario=usuario_atual,
                carga_estrogenica=4.2, 
                carga_androgenica=3.1, 
                carga_tireoidiana=2.8,
                carga_total=10.1
            )
            if ArmarioItem:
                for p in produtos_instancias:
                    kwargs = {}
                    for field in ArmarioItem._meta.fields:
                        if field.is_relation and field.related_model in [Usuario, Pessoa]:
                            kwargs[field.name] = usuario_atual
                        elif field.is_relation and field.related_model == Produto:
                            kwargs[field.name] = p
                        elif field.name in ["frequencia", "frequencia_uso"]:
                            kwargs[field.name] = 3.0
                    lookup_kwargs = {k: v for k, v in kwargs.items() if k in ["usuario", "pessoa", "user", "produto"]}
                    ArmarioItem.objects.get_or_create(**lookup_kwargs, defaults=kwargs)
        except Exception:
            pass

print("\n✅ SEED CONCLUÍDO COM SUCESSO! Cidades corrigidas e tela inicial ajustada.")