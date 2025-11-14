from ninja import Router
from django.shortcuts import get_object_or_404
from datetime import date
from validate_docbr import CPF
from tb_app.models import Plano, CondPagamento, Pessoa, Faturamento
from api.schemas import PlanoListSchema, AssinarPlanoInput, AssinarPlanoOutput

router = Router()

# -------------------------
# LISTAR PLANOS
# -------------------------
@router.get("/", response=PlanoListSchema)
def listar_planos(request):
    planos = Plano.objects.all()
    return {"planos": list(planos)}


# -------------------------
# ASSINAR PLANO
# -------------------------
# Exemplo de json:
# {
#   "cpf": "12345678909",
#   "numero_do_cartao": "4111111111111111",
#   "nome": "Nomeeeee",
#   "data_validade": "10/2030",
#   "cvv": "123",
#   "id_pessoa": 78,
#   "id_plano": 1
# }
@router.post("/assinar/", response=AssinarPlanoOutput)
def assinar_plano(request, payload: AssinarPlanoInput):

    pessoa = get_object_or_404(Pessoa, idpessoa=payload.id_pessoa)
    plano = get_object_or_404(Plano, id_plano=payload.id_plano)

    # validar CPF igual no site
    validador = CPF()
    if not validador.validate(payload.cpf):
        return 400, {"mensagem": "CPF inválido"}

    # criar CondPagamento
    cond = CondPagamento.objects.create(
        numero_do_cartao = payload.numero_do_cartao,
        nome = payload.nome,
        id_plano = plano.id_plano,
        data_validade = payload.data_validade,
        cvv = payload.cvv
    )

    # atualizar Pessoa
    pessoa.cpf = payload.cpf
    pessoa.id_plano = plano.id_plano
    pessoa.save()

    # criar Faturamento
    faturamento = Faturamento.objects.create(
        id_usuario = pessoa.idpessoa,
        id_plano = plano.id_plano,
        vencimento = payload.data_validade,
        data_compra = date.today().strftime("%d/%m/%Y")
    )

    return {
        "mensagem": "Plano assinado com sucesso!",
        "id_faturamento": faturamento.id_faturamento
    }
