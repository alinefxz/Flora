"""
Django settings for FLORA project.
Platform for mapping endocrine disruptors and women's health.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-flora-safe-key-change-this-in-production')

DEBUG = True

ALLOWED_HOSTS = ['*']

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    # Adicione bibliotecas de criptografia aqui se necessário (ex: 'encrypted_model_fields')
]

LOCAL_APPS = [
    'usuarios.apps.UsuariosConfig',  # Gerencia Pessoa, Usuária, Especialista, Admin, PerfilHormonal, Cidade, UF
    'produtos.apps.ProdutosConfig',  # Gerencia Categoria, Produto, Ingrediente, Substancia, TipoDesregulador, SugestaoTroca, Referencia
    'saude.apps.SaudeConfig',        # Gerencia ArmarioItem, Sintoma, RegistroSintoma, CicloMenstrual, Exposicao, AlertaRisco, Notificacao
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

#TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # ALTERE ESSA LINHA ABAIXO:
        'DIRS': [BASE_DIR / 'templates'],  # Diz ao Django para olhar a pasta templates da raiz
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = { 
    'default': { 
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'flora', 'USER': 'postgres', 
        'PASSWORD': '123456', 
        'HOST': 'localhost', 
        'PORT': '5432', 
        } 
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Essencial para que a classe Pessoa funcione como a base de autenticação do Django
AUTH_USER_MODEL = 'usuarios.Pessoa'

LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True

#ARQUIVOS ESTÁTICOS e DE MÍDIA
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 11. CONFIGURAÇÃO DE E-MAIL
# Em desenvolvimento, os e-mails serão exibidos diretamente no terminal do servidor
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Flora Plataforma <suporte@flora.org.br>'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Chave fictícia para criptografia simétrica de dados clínicos e CPF no backend
DATA_ENCRYPTION_KEY = os.environ.get('FLORA_ENCRYPTION_KEY', 'flora-secret-crypto-key-32-bytes-len!!')