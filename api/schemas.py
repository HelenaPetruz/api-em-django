from ninja import ModelSchema, Schema
from typing import Optional, List
from tb_app.models import (
    Perfil,
    Pessoa,
    RelUsuarioTreino,
    Plano,
    CondPagamento,
    NivelDificuldade,
    Exercicios,
    Treino,
    RelExerciciosMusculos,
    RelPlanoTreino,
    RelTreinoExercicio,
    MusculosEnvolvidos,
    Faturamento,
)

# ---------------------------
# PERFIL
# ---------------------------
class PerfilSchema(ModelSchema):
    class Meta:
        model = Perfil
        fields = "__all__"

# ---------------------------
# PESSOA (usuário)
# ---------------------------
class PessoaSchema(ModelSchema):
    class Meta:
        model = Pessoa
        fields = "__all__"

# ---------------------------
# RELAÇÕES SIMPLES (schema direto das tabelas)
# ---------------------------
class RelUsuarioTreinoSchema(ModelSchema):
    class Meta:
        model = RelUsuarioTreino
        fields = "__all__"


class PlanoSchema(ModelSchema):
    class Meta:
        model = Plano
        fields = "__all__"

class CondPagamentoSchema(ModelSchema):
    class Meta:
        model = CondPagamento
        fields = "__all__"

class NivelDificuldadeSchema(ModelSchema):
    class Meta:
        model = NivelDificuldade
        fields = "__all__"

# ---------------------------
# MÚSCULOS
# ---------------------------
class MusculosEnvolvidosSchema(ModelSchema):
    class Meta:
        model = MusculosEnvolvidos
        fields = "__all__"

# ---------------------------
# EXERCICIOS - versão básica (usa id_nivel_dificuldade como FK existente)
# ---------------------------
class ExerciciosListSchema(ModelSchema):
    class Meta:
        model = Exercicios
        fields = ["id_exercicios", "nome_exercicio", "id_nivel_dificuldade", "imagem"]

# ---------------------------
# EXERCICIOS - versão detalhada (nivel incluído; músculos serão adicionados manualmente no endpoint)
# ---------------------------
class ExerciciosDetailSchema(Schema):
    id_exercicios: int
    nome_exercicio: str
    descricao: Optional[str]
    nivel_dificuldade: Optional[NivelDificuldadeSchema]
    musculos: List[MusculosEnvolvidosSchema]
    imagem: Optional[str]
    link_ia: Optional[str]
    video: Optional[str]

# ---------------------------
# RELAÇÃO TREINO/EXERCICIO
# ---------------------------
class TreinoExercicioSchema(Schema):
    id_exercicio: int
    numero_series: int
    numero_repeticoes: int
# ---------------------------
# TREINO
# ---------------------------
# LISTAGEM
class TreinoListSchema(ModelSchema):
    class Meta:
        model = Treino
        fields = ["id_treino", "nome_treino", "treino_do_buddy"]


# DETALHE
class TreinoDetailSchema(Schema):
    id_treino: int
    nome_treino: str
    treino_do_buddy: int
    exercicios: List[TreinoExercicioSchema]


# CRIAÇÃO
class TreinoCreateExercicioSchema(Schema):
    id_exercicio: int
    numero_series: int
    numero_repeticoes: int
class TreinoCreateSchema(Schema):
    nome_treino: str
    id_pessoa: int    
    exercicios: Optional[List[TreinoCreateExercicioSchema]] = None   # lista de IDs dos exercícios

# ATUALIZAÇÃO
class TreinoUpdateExercicioSchema(Schema):
    id_exercicio: int
    numero_series: int
    numero_repeticoes: int
class TreinoUpdateSchema(Schema):
    nome_treino: Optional[str] = None
    adicionar_exercicios: Optional[List[TreinoUpdateExercicioSchema]] = None
    remover_exercicios: Optional[List[int]] = None   # só ID do exercício

# MEUS TREINOS
class MeusTreinosResponse(Schema):
    treinos: List[TreinoListSchema]

# ---------------------------
# RELAÇÕES PLANO/TREINO e TREINO/EXERCICIO
# ---------------------------
class RelExerciciosMusculosSchema(ModelSchema):
    class Meta:
        model = RelExerciciosMusculos
        fields = "__all__"

class RelPlanoTreinoSchema(ModelSchema):
    class Meta:
        model = RelPlanoTreino
        fields = "__all__"

class RelTreinoExercicioSchema(ModelSchema):
    class Meta:
        model = RelTreinoExercicio
        fields = "__all__"

# ---------------------------
# FATURAMENTO
# ---------------------------
class FaturamentoSchema(ModelSchema):
    class Meta:
        model = Faturamento
        fields = "__all__"

# ---------------------------
# login cadastro
# ---------------------------
class CadastroSchema(Schema):
    nome: str
    email: str
    senha1: str
    senha2: str

class LoginSchema(Schema):
    email: str
    senha: str

class LoginResponseSchema(Schema):
    id: int
    nome: str
    email: str
    token_sessao: str

class RecuperarSenhaSchema(Schema):
    email: str

class TrocarSenhaSchema(Schema):
    senha1: str
    senha2: str

# ---------------------------
# Planos e fazer assinaturas
# ---------------------------
class PlanoSchema(Schema):
    id_plano: int
    nome_plano: str
    valor: float

class PlanoListSchema(Schema):
    planos: list[PlanoSchema]


class AssinarPlanoInput(Schema):
    cpf: str
    numero_do_cartao: str
    nome: str
    data_validade: str   # ex: "10/2030"
    cvv: str
    id_pessoa: int
    id_plano: int


class AssinarPlanoOutput(Schema):
    mensagem: str
    id_faturamento: int