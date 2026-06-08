from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from usuarios.models import Especialista


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nome


class TipoDesregulador(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = 'Tipo de Desregulador'
        verbose_name_plural = 'Tipos de Desreguladores'

    def __str__(self):
        return self.nome


class Substancia(models.Model):
    nome = models.CharField(max_length=150)
    cas_number = models.CharField(max_length=50, unique=True)
    nivel_risco = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    mecanismo_acao = models.TextField()
    descricao = models.TextField(blank=True)
    tipo_desregulador = models.ForeignKey(TipoDesregulador, on_delete=models.PROTECT, related_name="substancias")

    class Meta:
        ordering = ["nome"]
        verbose_name = 'Substância'
        verbose_name_plural = 'Substâncias'

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=255)
    marca = models.CharField(max_length=100)
    codigo_barras = models.CharField(max_length=14, unique=True)
    imagem = models.ImageField(upload_to="produtos/", null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="produtos")
    descricao = models.TextField(blank=True)
    fabricante = models.CharField(max_length=150, blank=True)
    nota_flora = models.FloatField(default=5.0)

    class Meta:
        ordering = ["nome", "marca"]
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def recalcular_nota_flora(self, salvar=True):
        risco = 0.0
        for item in self.composicao.select_related("ingrediente__substancia"):
            substancia = item.ingrediente.substancia
            if substancia:
                risco += substancia.nivel_risco * max(item.concentracao_estimada, 0)

        self.nota_flora = 5.0 if risco == 0 else round(max(1.0, 5.0 - min(4.0, risco)), 2)

        if salvar:
            self.save(update_fields=["nota_flora"])

        return self.nota_flora

    def __str__(self):
        return f"{self.nome} ({self.marca})"


class Ingrediente(models.Model):
    nome = models.CharField(max_length=150)
    funcao_quimica = models.CharField(max_length=100, blank=True)
    substancia = models.ForeignKey(Substancia, on_delete=models.SET_NULL, null=True, blank=True, related_name="ingredientes")

    class Meta:
        ordering = ["nome"]
        verbose_name = 'Ingrediente'
        verbose_name_plural = 'Ingredientes'

    def __str__(self):
        return self.nome


class ProdutoIngrediente(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="composicao")
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, related_name="produtos")
    concentracao_estimada = models.FloatField(default=0.0)
    unidade_concentracao = models.CharField(max_length=20, default="%")

    class Meta:
        unique_together = ("produto", "ingrediente")
        verbose_name = 'Ingrediente do Produto'
        verbose_name_plural = 'Ingredientes dos Produtos'

    def __str__(self):
        return f"{self.ingrediente} em {self.produto}"


class SugestaoTroca(models.Model):
    produto_risco = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="sugestoes_de_substituicao")
    produto_seguro = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="alternativas_seguras")
    justificativa_tecnica = models.TextField()
    origem_sugestao = models.CharField(max_length=100, default="Base de Dados Flora")
    confianca = models.FloatField(default=1.0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    especialista = models.ForeignKey(Especialista, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.produto_risco} -> {self.produto_seguro}"


class Referencia(models.Model):
    titulo_artigo = models.CharField(max_length=255)
    autores = models.TextField()
    ano_publicacao = models.PositiveIntegerField()
    link_doi = models.URLField(blank=True)
    instituicao_fonte = models.CharField(max_length=255, blank=True)
    substancia = models.ForeignKey(Substancia, on_delete=models.CASCADE, related_name="referencias")
    arquivo_artigo = models.FileField(upload_to="artigos_cientificos/", null=True, blank=True)

    def __str__(self):
        return self.titulo_artigo
    

from django.conf import settings


class ComentarioProduto(models.Model):
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name="comentarios",
        verbose_name="Produto",
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comentarios_produtos",
        verbose_name="Autor",
    )
    texto = models.TextField("Comentário")
    ativo = models.BooleanField("Ativo", default=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Comentário de produto"
        verbose_name_plural = "Comentários de produtos"

    @property
    def total_curtidas(self):
        return self.curtidas.count()

    def __str__(self):
        return f"{self.autor} comentou em {self.produto}"


class CurtidaComentario(models.Model):
    comentario = models.ForeignKey(
        ComentarioProduto,
        on_delete=models.CASCADE,
        related_name="curtidas",
        verbose_name="Comentário",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comentarios_curtidos",
        verbose_name="Usuário",
    )
    criada_em = models.DateTimeField("Criada em", auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["comentario", "usuario"],
                name="curtida_unica_por_usuario",
            )
        ]
        verbose_name = "Curtida"
        verbose_name_plural = "Curtidas"

    def __str__(self):
        return f"{self.usuario} curtiu o comentário #{self.comentario_id}"