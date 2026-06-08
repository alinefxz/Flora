from django import forms
from django.forms import modelform_factory
from django.utils.text import slugify

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
from usuarios.models import (
    Admin,
    Cidade,
    Especialista,
    PerfilHormonal,
    Pessoa,
    UF,
    Usuario,
)
from .models import (
    ArmarioItem,
    CicloMenstrual,
    RegistroSintoma,
    Sintoma,
)


DATE_FIELDS = {
    "data_nasc",
    "data_inicio",
    "data_fim",
    "data_ocorrencia",
}


class FloraModelForm(forms.ModelForm):
    disabled_fields = set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "usuario" in self.fields:
            self.fields["usuario"].queryset = Pessoa.objects.filter(
                tipo_usuario="USUARIA",
                ativo=True,
            )

        if "especialista" in self.fields:
            self.fields["especialista"].queryset = Pessoa.objects.filter(
                tipo_usuario="ESPECIALISTA",
                ativo=True,
            )

        for name, field in self.fields.items():
            if name in DATE_FIELDS:
                field.widget = forms.DateInput(
                    format="%Y-%m-%d",
                    attrs={"type": "date"},
                )

            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 4)

            field.widget.attrs.setdefault("placeholder", field.label)

            if name in self.disabled_fields:
                field.disabled = True
                field.required = False


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "placeholder": "voce@email.com",
            }
        ),
    )
    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "placeholder": "Sua senha",
            }
        ),
    )


class CadastroForm(FloraModelForm):
    TIPO_CHOICES = [
        ("USUARIA", "Sou usuária"),
        ("ESPECIALISTA", "Sou especialista"),
    ]

    CONSELHO_CHOICES = [
        ("CRM", "CRM"),
        ("CRF", "CRF"),
        ("CRQ", "CRQ"),
        ("COREN", "COREN"),
        ("CRN", "CRN"),
        ("OUTRO", "Outro"),
    ]

    tipo_usuario = forms.ChoiceField(
        label="Tipo de perfil",
        choices=TIPO_CHOICES,
        widget=forms.RadioSelect,
    )
    conselho = forms.ChoiceField(
        label="Conselho profissional",
        choices=CONSELHO_CHOICES,
        required=False,
    )
    numero_registro = forms.CharField(
        label="Número e UF do registro",
        required=False,
        help_text="Exemplo: SP 123456",
    )
    senha = forms.CharField(
        label="Senha",
        min_length=8,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    confirmar_senha = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = Pessoa
        fields = [
            "tipo_usuario",
            "nome_completo",
            "email",
            "cpf",
            "data_nasc",
            "cidade",
            "apelido",
            "foto_perfil",
            "conselho",
            "numero_registro",
            "especialidade",
            "biografia",
            "senha",
            "confirmar_senha",
        ]

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get("tipo_usuario")

        if cleaned.get("senha") != cleaned.get("confirmar_senha"):
            self.add_error("confirmar_senha", "As senhas não conferem.")

        if tipo == "ESPECIALISTA":
            if not cleaned.get("conselho"):
                self.add_error("conselho", "Informe o conselho profissional.")

            if not cleaned.get("numero_registro"):
                self.add_error(
                    "numero_registro",
                    "Informe o número do registro profissional.",
                )

            if not cleaned.get("especialidade"):
                self.add_error(
                    "especialidade",
                    "Informe sua especialidade.",
                )

        return cleaned

    def criar_username(self, email):
        base = slugify(email.split("@")[0]) or "flora"
        username = base
        contador = 1

        while Pessoa.objects.filter(username=username).exists():
            contador += 1
            username = f"{base}{contador}"

        return username

    def save(self, commit=True):
        pessoa = super().save(commit=False)
        tipo = self.cleaned_data["tipo_usuario"]

        pessoa.username = self.criar_username(pessoa.email)
        pessoa.tipo_usuario = tipo
        pessoa.ativo = True
        pessoa.is_active = True
        pessoa.is_staff = False
        pessoa.is_superuser = False
        pessoa.nivel_acesso = ""
        pessoa.set_password(self.cleaned_data["senha"])

        if tipo == "ESPECIALISTA":
            conselho = self.cleaned_data["conselho"]
            numero = self.cleaned_data["numero_registro"].strip()
            pessoa.registro_profissional = f"{conselho}/{numero}"
            pessoa.apelido = ""
        else:
            pessoa.registro_profissional = ""
            pessoa.especialidade = ""
            pessoa.biografia = ""

        if commit:
            pessoa.save()

        return pessoa


class PessoaForm(FloraModelForm):
    senha = forms.CharField(
        label="Nova senha",
        required=False,
        widget=forms.PasswordInput,
        help_text="Deixe vazio para manter a senha atual.",
    )

    role_value = None

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
            "especialidade",
            "biografia",
            "nivel_acesso",
            "is_staff",
            "is_superuser",
            "senha",
        ]

    def save(self, commit=True):
        pessoa = super().save(commit=False)

        if self.role_value:
            pessoa.tipo_usuario = self.role_value

        senha = self.cleaned_data.get("senha")
        if senha:
            pessoa.set_password(senha)

        if pessoa.tipo_usuario == "ADMIN":
            pessoa.is_staff = True

        if commit:
            pessoa.save()
            self.save_m2m()

        return pessoa


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
            "senha",
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
            "senha",
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
            "senha",
        ]


class PerfilHormonalForm(FloraModelForm):
    class Meta:
        model = PerfilHormonal
        fields = [
            "usuario", "uso_contraceptivo", "condicao_hormonal",
            "ciclo_regular", "duracao_ciclo",
            "fluxo_menstrual", "observacoes",
        ]


class ProdutoForm(FloraModelForm):
    disabled_fields = {"nota_flora"}

    class Meta:
        model = Produto
        fields = "__all__"


class CicloMenstrualForm(FloraModelForm):
    class Meta:
        model = CicloMenstrual
        fields = "__all__"
        help_texts = {
            "data_fim": (
                "Opcional. Se ficar vazia, será calculada usando a duração."
            ),
            "duracao": "Duração da menstruação em dias.",
        }


class RegistroSintomaForm(FloraModelForm):
    sintoma_opcao = forms.ChoiceField(label="Qual sintoma você sentiu?")
    outro_sintoma = forms.CharField(
        label="Nome do sintoma",
        required=False,
    )
    descricao_outro = forms.CharField(
        label="Descreva o sintoma",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    class Meta:
        model = RegistroSintoma
        fields = [
            "usuario", "sintoma_opcao", "outro_sintoma",
            "descricao_outro", "data_ocorrencia",
            "intensidade", "observacoes",
        ]
        widgets = {
            "data_ocorrencia": forms.DateInput(attrs={"type": "date"}),
            "intensidade": forms.NumberInput(attrs={
                "min": 1, "max": 5,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sintomas = Sintoma.objects.order_by("nome")
        self.fields["sintoma_opcao"].choices = [
            ("", "Selecione um sintoma"),
            *[(str(item.pk), item.nome) for item in sintomas],
            ("OUTRO", "Não encontrei meu sintoma"),
        ]

        if self.instance.pk:
            self.initial["sintoma_opcao"] = str(
                self.instance.sintoma_id
            )

    def clean(self):
        cleaned = super().clean()
        opcao = cleaned.get("sintoma_opcao")

        if opcao == "OUTRO" and not cleaned.get("outro_sintoma"):
            self.add_error(
                "outro_sintoma",
                "Informe o nome do sintoma.",
            )

        return cleaned

    def save(self, commit=True):
        registro = super().save(commit=False)
        opcao = self.cleaned_data["sintoma_opcao"]

        if opcao == "OUTRO":
            sintoma, _ = Sintoma.objects.get_or_create(
                nome=self.cleaned_data["outro_sintoma"].strip(),
                defaults={
                    "descricao": self.cleaned_data.get(
                        "descricao_outro", ""
                    )
                },
            )
        else:
            sintoma = Sintoma.objects.get(pk=opcao)

        registro.sintoma = sintoma

        if commit:
            registro.save()

        return registro


def criar_model_form(model, disabled=()):
    form_class = modelform_factory(
        model,
        form=FloraModelForm,
        fields="__all__",
    )
    form_class.disabled_fields = set(disabled)
    return form_class


UFForm = criar_model_form(UF)
CidadeForm = criar_model_form(Cidade)
CategoriaForm = criar_model_form(Categoria)
TipoDesreguladorForm = criar_model_form(TipoDesregulador)
SubstanciaForm = criar_model_form(Substancia)
IngredienteForm = criar_model_form(Ingrediente)
ProdutoIngredienteForm = criar_model_form(ProdutoIngrediente)
SugestaoTrocaForm = criar_model_form(SugestaoTroca)
ReferenciaForm = criar_model_form(Referencia)
ArmarioItemForm = criar_model_form(ArmarioItem)
SintomaForm = criar_model_form(Sintoma)