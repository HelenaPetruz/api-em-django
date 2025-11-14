from ninja import Router
from django.contrib.auth.hashers import make_password, check_password
from django.core import signing
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from tb_app.models import Pessoa, RelUsuarioTreino, Treino
from api.schemas import (
    CadastroSchema, LoginSchema, LoginResponseSchema, 
    RecuperarSenhaSchema, TrocarSenhaSchema, MeusTreinosResponse
)

router = Router(tags=["Autenticação"])


# -----------------------------------------------------
# CADASTRO
# -----------------------------------------------------
# joson pra exemplo de cadastro
# {
#   "nome": "eu",
#   "email": "eu@gmail.com",
#   "senha1": "minhasenha123",
#   "senha2": "minhasenha123"
# }
@router.post("/cadastro")
def cadastro(request, payload: CadastroSchema):
    if Pessoa.objects.filter(email=payload.email).exists():
        return {"erro": "Esse email já existe!"}

    if payload.senha1 != payload.senha2:
        return {"erro": "As senhas não coincidem!"}

    pessoa = Pessoa.objects.create(
        nome_usuario=payload.nome,
        email=payload.email,
        senha=make_password(payload.senha1),
        id_plano=4,
        id_perfil=1,
    )

    # simulando sessão por token
    token = signing.dumps({"id": pessoa.idpessoa})

    return {
        "id": pessoa.idpessoa,
        "nome": pessoa.nome_usuario,
        "email": pessoa.email,
        "token_sessao": token,
        "mensagem": "Cadastro realizado com sucesso!"
    }


# joson pra exemplo de login
# {
#   "email": "eu@gmail.com",
#   "senha": "minhasenha123",
# }
@router.post("/login", response=LoginResponseSchema)
def login(request, payload: LoginSchema):

    try:
        pessoa = Pessoa.objects.get(email=payload.email)
    except Pessoa.DoesNotExist:
        return {"erro": "Email não encontrado :("}

    if not check_password(payload.senha, pessoa.senha):
        return {"erro": "Senha incorreta :("}

    token = signing.dumps({"id": pessoa.idpessoa})

    return {
        "id": pessoa.idpessoa,
        "nome": pessoa.nome_usuario,
        "email": pessoa.email,
        "token_sessao": token
    }


# aq pode enviar post com json vazio: {}
@router.post("/logout")
def logout(request):
    return {"mensagem": "Logout realizado."}

# -------------------------------
#  GERAR E VALIDAR TOKEN
# -------------------------------
def gerar_token(pessoa_id):
    return signing.dumps({"id": pessoa_id})

def validar_token(token):
    try:
        data = signing.loads(token, max_age=3600)  # 1h
        return data["id"]
    except signing.BadSignature:
        return None


# -------------------------------
#  RECUPERAR SENHA
# -------------------------------
# json de exemplo:
# {
#   "email": "eu@gmail.com"
# }
@router.post("/recuperar-senha")
def recuperar_senha(request, payload: RecuperarSenhaSchema):

    try:
        pessoa = Pessoa.objects.get(email=payload.email)
    except Pessoa.DoesNotExist:
        return {"erro": "Email não encontrado :("}

    uid = urlsafe_base64_encode(force_bytes(pessoa.idpessoa))
    token = gerar_token(pessoa.idpessoa)

    link = request.build_absolute_uri(f"/api/auth/trocar-senha/{uid}/{token}/")

    assunto = "Trainer Buddy: Redefinição de senha"
    mensagem = (
        f"Olá {pessoa.nome_usuario},\n\n"
        f"Clique no link para redefinir sua senha:\n{link}"
    )

    send_mail(assunto, mensagem, settings.DEFAULT_FROM_EMAIL, [pessoa.email])

    return {"mensagem": "Email de recuperação enviado com sucesso!"}

@router.post("/trocar-senha/{uidb64}/{token}/")
def trocar_senha(request, uidb64: str, token: str, payload: TrocarSenhaSchema):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        pessoa = Pessoa.objects.get(idpessoa=uid)
    except:
        return {"erro": "Usuário inválido!"}

    pessoa_id = validar_token(token)

    if not pessoa_id:
        return {"erro": "Token inválido ou expirado!"}

    if payload.senha1 != payload.senha2:
        return {"erro": "As senhas não coincidem!"}

    if check_password(payload.senha1, pessoa.senha):
        return {"erro": "A nova senha não pode ser igual à anterior!"}

    pessoa.senha = make_password(payload.senha1)
    pessoa.save()

    return {"mensagem": "Senha redefinida com sucesso!"}

# -------------------------------
#  MEUS TREINOS
# -------------------------------
@router.get("/meus-treinos/{id_pessoa}/", response=MeusTreinosResponse)
def meus_treinos(request, id_pessoa: int):
    pessoa = get_object_or_404(Pessoa, idpessoa=id_pessoa)
    rels = RelUsuarioTreino.objects.filter(id_pessoa=pessoa.idpessoa)
    ids_treinos = [rel.id_treino for rel in rels]
    treinos = Treino.objects.filter(id_treino__in=ids_treinos)
    return {"treinos": list(treinos)}