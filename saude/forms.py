from django import forms

from produtos.models import (
    Categoria,
    Ingrediente,
    Produto,
    ProdutoIngrediente,
    Referencia,
    Substancia,
    SugestaoTroca,
    TipoDesregulador,
)
from usuarios.models import Admin, Cidade, Especialista, PerfilHormonal, Pessoa, UF, Usuario
from .models import (
    AlertaRisco,
    ArmarioItem,
    CicloMenstrual,
    Exposicao,
    ExposicaoDetalhe,
    Notificacao,
    RegistroSintoma,
    Sintoma,
)


class FloraModelForm(forms.ModelForm):
    senha = forms.CharField(
        label="Senha",
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Preencha apenas ao cadastrar ou quando quiser trocar a senha.",
    )

    role_value = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "senha" in self.fields and self.instance and self.instance.pk:
            self.fields["senha"].help_text = "Deixe em branco para manter a senha atual."

        if "usuario" in self.fields:
            self.fields["usuario"].queryset = Usuario.objects.filter(tipo_usuario="USUARIA")

        if "especialista" in self.fields:
            self.fields["especialista"].queryset = Especialista.objects.filter(tipo_usuario="ESPECIALISTA")

        for name, field in self.fields.items():
            css_class = "form-control"
            if isinstance(field.widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                css_class = "form-check-input"
            elif isinstance(field.widget, forms.Select):
                css_class = "form-select"

            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {css_class}".strip()

            if isinstance(field.widget, forms.DateInput):
                field.widget.input_type = "date"

            if name in {"cpf"}:
                field.widget.attrs.setdefault("placeholder", "000.000.000-00")

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.role_value:
            instance.tipo_usuario = self.role_value

        senha = self.cleaned_data.get("senha")
        if senha and hasattr(instance, "set_password"):
            instance.set_password(senha)

        if getattr(instance, "tipo_usuario", None) == "ADMIN":
            instance.is_staff = True

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class PessoaForm(FloraModelForm):
    class Meta:
        model = Pessoa
        fields = [
            "username",
            "email",
            "nome_completo",
            "cpf",
            "data_nasc",
            "ativo",
            "tipo_usuario",
            "cidade",
            "apelido",
            "foto_perfil",
            "registro_profissional",
            "biografia",
            "especialidade",
            "nivel_acesso",
            "is_staff",
            "is_superuser",
        ]


class UsuarioForm(PessoaForm):
    role_value = "USUARIA"

    class Meta(PessoaForm.Meta):
        model = Usuario
        fields = [
            "username",
            "email",
            "nome_completo",
            "cpf",
            "data_nasc",
            "ativo",
            "cidade",
            "apelido",
            "foto_perfil",
        ]


class EspecialistaForm(PessoaForm):
    role_value = "ESPECIALISTA"

    class Meta(PessoaForm.Meta):
        model = Especialista
        fields = [
            "username",
            "email",
            "nome_completo",
            "cpf",
            "data_nasc",
            "ativo",
            "cidade",
            "registro_profissional",
            "especialidade",
            "biografia",
        ]


class AdminFloraForm(PessoaForm):
    role_value = "ADMIN"

    class Meta(PessoaForm.Meta):
        model = Admin
        fields = [
            "username",
            "email",
            "nome_completo",
            "cpf",
            "data_nasc",
            "ativo",
            "cidade",
            "nivel_acesso",
            "is_superuser",
        ]


class UFForm(FloraModelForm):
    class Meta:
        model = UF
        fields = ["nome_estado", "sigla"]


class CidadeForm(FloraModelForm):
    class Meta:
        model = Cidade
        fields = ["nome_cidade", "uf"]


class PerfilHormonalForm(FloraModelForm):
    class Meta:
        model = PerfilHormonal
        fields = [
            "usuario",
            "uso_contraceptivo",
            "condicao_hormonal",
            "ciclo_regular",
            "duracao_ciclo",
            "fluxo_menstrual",
            "observacoes",
            "peso_sensibilidade",
        ]


class CategoriaForm(FloraModelForm):
    class Meta:
        model = Categoria
        fields = ["nome", "descricao"]


class TipoDesreguladorForm(FloraModelForm):
    class Meta:
        model = TipoDesregulador
        fields = ["nome", "descricao"]


class SubstanciaForm(FloraModelForm):
    class Meta:
        model = Substancia
        fields = ["nome", "cas_number", "nivel_risco", "mecanismo_acao", "descricao", "tipo_desregulador"]


class ProdutoForm(FloraModelForm):
    class Meta:
        model = Produto
        fields = ["nome", "marca", "codigo_barras", "imagem", "categoria", "descricao", "fabricante", "nota_flora"]


class IngredienteForm(FloraModelForm):
    class Meta:
        model = Ingrediente
        fields = ["nome", "funcao_quimica", "substancia"]


class ProdutoIngredienteForm(FloraModelForm):
    class Meta:
        model = ProdutoIngrediente
        fields = ["produto", "ingrediente", "concentracao_estimada", "unidade_concentracao"]


class SugestaoTrocaForm(FloraModelForm):
    class Meta:
        model = SugestaoTroca
        fields = [
            "produto_risco",
            "produto_seguro",
            "justificativa_tecnica",
            "origem_sugestao",
            "confianca",
            "especialista",
        ]


class ReferenciaForm(FloraModelForm):
    class Meta:
        model = Referencia
        fields = [
            "titulo_artigo",
            "autores",
            "ano_publicacao",
            "link_doi",
            "instituicao_fonte",
            "substancia",
            "arquivo_artigo",
        ]


class ArmarioItemForm(FloraModelForm):
    class Meta:
        model = ArmarioItem
        fields = ["usuario", "produto", "frequencia_uso"]


class SintomaForm(FloraModelForm):
    class Meta:
        model = Sintoma
        fields = ["nome", "descricao"]


class CicloMenstrualForm(FloraModelForm):
    class Meta:
        model = CicloMenstrual
        fields = ["usuario", "data_inicio", "data_fim", "duracao", "observacoes"]


class RegistroSintomaForm(FloraModelForm):
    class Meta:
        model = RegistroSintoma
        fields = ["usuario", "sintoma", "data_ocorrencia", "intensidade", "fase_ciclo", "observacoes"]


class ExposicaoForm(FloraModelForm):
    class Meta:
        model = Exposicao
        fields = ["usuario", "carga_estrogenica", "carga_androgenica", "carga_tireoidiana", "carga_total"]


class ExposicaoDetalheForm(FloraModelForm):
    class Meta:
        model = ExposicaoDetalhe
        fields = ["exposicao", "produto", "substancia", "valor_contribuicao"]


class AlertaRiscoForm(FloraModelForm):
    class Meta:
        model = AlertaRisco
        fields = ["usuario", "mensagem_alerta", "nivel_gravidade"]


class NotificacaoForm(FloraModelForm):
    class Meta:
        model = Notificacao
        fields = ["usuario", "mensagem", "tipo_notificacao", "lida"]
