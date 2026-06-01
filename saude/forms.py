from django import forms

from usuarios.models import Pessoa, Usuario, Especialista, Admin, UF, Cidade, PerfilHormonal
from produtos.models import Categoria, TipoDesregulador, Substancia, Produto, Ingrediente, ProdutoIngrediente, SugestaoTroca, Referencia
from saude.models import ArmarioItem, Sintoma, CicloMenstrual, RegistroSintoma, Exposicao, ExposicaoDetalhe, AlertaRisco, Notificacao


class FloraFormMixin:
    date_fields = {"data_nasc", "data_inicio", "data_fim", "data_ocorrencia"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "usuario" in self.fields:
            self.fields["usuario"].queryset = Usuario.objects.filter(tipo_usuario="USUARIA")

        if "especialista" in self.fields:
            self.fields["especialista"].queryset = Especialista.objects.filter(tipo_usuario="ESPECIALISTA")

        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"

            if name in self.date_fields:
                field.widget = forms.DateInput(
                    attrs={"type": "date", "class": "form-control"},
                    format="%Y-%m-%d",
                )


class PessoaForm(FloraFormMixin, forms.ModelForm):
    senha = forms.CharField(
        label="Senha",
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="Preencha ao cadastrar ou quando quiser alterar a senha.",
    )

    class Meta:
        model = Pessoa
        fields = [
            "username", "email", "nome_completo", "cpf", "data_nasc",
            "ativo", "tipo_usuario", "cidade",
            "apelido", "foto_perfil",
            "registro_profissional", "biografia", "especialidade",
            "nivel_acesso", "is_staff", "is_superuser",
        ]

    def save(self, commit=True):
        obj = super().save(commit=False)
        senha = self.cleaned_data.get("senha")

        if senha:
            obj.set_password(senha)

        if obj.tipo_usuario == "ADMIN":
            obj.is_staff = True

        if commit:
            obj.save()
            self.save_m2m()

        return obj


class UsuarioForm(PessoaForm):
    class Meta(PessoaForm.Meta):
        model = Usuario
        fields = [
            "username", "email", "nome_completo", "cpf", "data_nasc",
            "ativo", "cidade", "apelido", "foto_perfil",
        ]

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.tipo_usuario = "USUARIA"
        if commit:
            obj.save()
            self.save_m2m()
        return obj


class EspecialistaForm(PessoaForm):
    class Meta(PessoaForm.Meta):
        model = Especialista
        fields = [
            "username", "email", "nome_completo", "cpf", "data_nasc",
            "ativo", "cidade", "registro_profissional", "especialidade", "biografia",
        ]

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.tipo_usuario = "ESPECIALISTA"
        if commit:
            obj.save()
            self.save_m2m()
        return obj


class AdminFloraForm(PessoaForm):
    class Meta(PessoaForm.Meta):
        model = Admin
        fields = [
            "username", "email", "nome_completo", "cpf", "data_nasc",
            "ativo", "cidade", "nivel_acesso", "is_superuser",
        ]

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.tipo_usuario = "ADMIN"
        obj.is_staff = True
        if commit:
            obj.save()
            self.save_m2m()
        return obj


class UFForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = UF
        fields = "__all__"


class CidadeForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = Cidade
        fields = "__all__"


class PerfilHormonalForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = PerfilHormonal
        fields = "__all__"


class CategoriaForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = Categoria
        fields = "__all__"


class TipoDesreguladorForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = TipoDesregulador
        fields = "__all__"


class SubstanciaForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = Substancia
        fields = "__all__"


class ProdutoForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = Produto
        fields = "__all__"


class IngredienteForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = Ingrediente
        fields = "__all__"


class ProdutoIngredienteForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = ProdutoIngrediente
        fields = "__all__"


class SugestaoTrocaForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = SugestaoTroca
        fields = "__all__"


class ReferenciaForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = Referencia
        fields = "__all__"


class ArmarioItemForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = ArmarioItem
        fields = "__all__"


class SintomaForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = Sintoma
        fields = "__all__"


class CicloMenstrualForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = CicloMenstrual
        fields = "__all__"


class RegistroSintomaForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = RegistroSintoma
        fields = "__all__"


class ExposicaoForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = Exposicao
        fields = ["usuario", "carga_estrogenica", "carga_androgenica", "carga_tireoidiana", "carga_total"]


class ExposicaoDetalheForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = ExposicaoDetalhe
        fields = "__all__"


class AlertaRiscoForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = AlertaRisco
        fields = ["usuario", "mensagem_alerta", "nivel_gravidade"]


class NotificacaoForm(FloraFormMixin, forms.ModelForm):
    class Meta:
        model = Notificacao
        fields = ["usuario", "mensagem", "tipo_notificacao", "lida"]




from django.contrib.auth import get_user_model


class LoginForm(forms.Form):
    email = forms.EmailField(label="E-mail")
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput)


class CadastroForm(FloraFormMixin, forms.ModelForm):
    TIPO_CHOICES = [
        ("USUARIA", "Sou usuária"),
        ("ESPECIALISTA", "Sou especialista"),
    ]

    tipo_usuario = forms.ChoiceField(label="Tipo de cadastro", choices=TIPO_CHOICES)
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput)
    confirmar_senha = forms.CharField(label="Confirmar senha", widget=forms.PasswordInput)

    class Meta:
        model = Pessoa
        fields = [
            "tipo_usuario",
            "username",
            "email",
            "nome_completo",
            "cpf",
            "data_nasc",
            "cidade",
            "apelido",
            "foto_perfil",
            "registro_profissional",
            "especialidade",
            "biografia",
        ]

    def clean(self):
        cleaned = super().clean()

        if cleaned.get("senha") != cleaned.get("confirmar_senha"):
            self.add_error("confirmar_senha", "As senhas não conferem.")

        if cleaned.get("tipo_usuario") == "ESPECIALISTA":
            if not cleaned.get("registro_profissional"):
                self.add_error("registro_profissional", "Informe o registro profissional.")
            if not cleaned.get("especialidade"):
                self.add_error("especialidade", "Informe a especialidade.")

        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.tipo_usuario = self.cleaned_data["tipo_usuario"]
        obj.ativo = True
        obj.is_staff = False
        obj.is_superuser = False
        obj.set_password(self.cleaned_data["senha"])

        if obj.tipo_usuario == "USUARIA":
            obj.registro_profissional = ""
            obj.especialidade = ""
            obj.biografia = ""

        if obj.tipo_usuario == "ESPECIALISTA":
            obj.apelido = ""

        if commit:
            obj.save()

        return obj