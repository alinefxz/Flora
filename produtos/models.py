from django.db import models
from usuarios.models import Especialista

class Categoria(models.Model):
    # RF06 - Gerenciar Categorias 
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome

class TipoDesregulador(models.Model):
    # RF11 - Gerenciar Eixos Hormonais
    nome = models.CharField(max_length=100, help_text="Ex: Estrogênico, Androgênico, Tireoidiano")
    descricao = models.TextField()

    def __str__(self):
        return self.nome

class Substancia(models.Model):
    # RF10 - Gerenciar Desreguladores
    nome = models.CharField(max_length=150)
    cas_number = models.CharField(max_length=50, unique=True, help_text="Identificador químico universal")
    nivel_risco = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text="Nota de 1 a 5")
    mecanismo_acao = models.TextField()
    descricao = models.TextField(blank=True)
    tipo_desregulador = models.ForeignKey(TipoDesregulador, on_delete=models.PROTECT, related_name='substancias')

    def __str__(self):
        return self.nome

class Produto(models.Model):
    # RF07 - Gerenciar Produtos
    nome = models.CharField(max_length=255)
    marca = models.CharField(max_length=100)
    codigo_barras = models.CharField(max_length=13, unique=True, help_text="Código GTIN/EAN")
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='produtos')
    descricao = models.TextField(blank=True)
    fabricante = models.CharField(max_length=150)
    nota_flora = models.FloatField(default=5.0, help_text="Calculada dinamicamente de 1 a 5 (RN03)")

    def __str__(self):
        return f"{self.nome} ({self.marca})"

class Ingrediente(models.Model):
    # RF08 - Gerenciar Ingredientes 
    nome = models.CharField(max_length=150)
    funcao_quimica = models.CharField(max_length=100, help_text="Ex: Conservante, Emulsificante")
    substancia = models.ForeignKey(Substancia, on_delete=models.SET_NULL, null=True, blank=True, related_name='ingredientes')

    def __str__(self):
        return self.nome

class ProdutoIngrediente(models.Model):
    # RF09 - Gerenciar Composição 
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='composicao')
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    concentracao_estimada = models.FloatField(help_text="Valor numérico bruto")
    unidade_concentracao = models.CharField(max_length=10, default='%', help_text="Ex: %, ppm, mg/kg")

    class Meta:
        unique_together = ('produto', 'ingrediente')

class SugestaoTroca(models.Model):
    # RF18 - Sugerir Substituições (RN07) 
    produto_risco = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='sugestoes_de_substituicao')
    produto_seguro = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='alternativas_seguras')
    justificativa_tecnica = models.TextField()
    origem_sugestao = models.CharField(max_length=100, default="Base de Dados Flora")
    confianca = models.FloatField(default=1.0, help_text="Grau de certeza estatística do algoritmo/médico")
    especialista = models.ForeignKey(Especialista, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Trocar {self.produto_risco.nome} por {self.produto_seguro.nome}"

class Referencia(models.Model):
    # RF19 - Gerenciar Referências 
    titulo_artigo = models.CharField(max_length=255)
    autores = models.TextField()
    ano_publicacao = models.IntegerField()
    link_doi = models.URLField()
    instituicao_fonte = models.CharField(max_length=255)
    substancia = models.ForeignKey(Substancia, on_delete=models.CASCADE, related_name='referencias')
    arquivo_artigo = models.FileField(upload_to='artigos_cientificos/', null=True, blank=True) # Atende UI-vi

    def __str__(self):
        return self.titulo_artigo