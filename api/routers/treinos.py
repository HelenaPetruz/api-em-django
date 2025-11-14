from ninja import Router
from typing import List
from django.shortcuts import get_object_or_404
from tb_app.models import Treino, RelTreinoExercicio, RelUsuarioTreino
from api.schemas import (
    TreinoListSchema,
    TreinoDetailSchema,
    TreinoCreateSchema,
    TreinoUpdateSchema,
    TreinoExercicioSchema
)

router = Router(tags=["Treino"])

@router.get("/", response=List[TreinoListSchema])
def listar_treinos(request):
    return Treino.objects.all()

@router.get("/{id}/", response=TreinoDetailSchema)
def treino_detail(request, id: int):
    treino = get_object_or_404(Treino, id_treino=id)
    rels = RelTreinoExercicio.objects.filter(id_treino=id)

    exercicios = []
    for r in rels:
        exercicios.append({
            "id_exercicio": r.id_exercicio,
            "numero_series": r.numero_series,
            "numero_repeticoes": r.numero_repeticoes,
        })

    return {
        "id_treino": treino.id_treino,
        "nome_treino": treino.nome_treino,
        "treino_do_buddy": treino.treino_do_buddy,
        "exercicios": exercicios,
    }


@router.post("/", response=TreinoListSchema)
def criar_treino(request, payload: TreinoCreateSchema):
    treino = Treino.objects.create(
        nome_treino=payload.nome_treino,
        treino_do_buddy=0,
    )

    if payload.exercicios:
        for item in payload.exercicios:
            RelTreinoExercicio.objects.create(
                id_treino=treino.id_treino,
                id_exercicio=item.id_exercicio,
                numero_series=item.numero_series,
                numero_repeticoes=item.numero_repeticoes,
            )

    RelUsuarioTreino.objects.create(
        id_treino=treino.id_treino,
        id_pessoa=payload.id_pessoa
    )
    return treino

# Exemplo de json pra criar treino
# {
#   "nome_treino": "Treino A",
#   "id_pessoa": 78,
#   "exercicios": [
#     {
#       "id_exercicio": 1,
#       "numero_series": 4,
#       "numero_repeticoes": 12
#     }
#   ]
# }


@router.put("/{id}/", response=TreinoListSchema)
def editar_treino(request, id: int, payload: TreinoUpdateSchema):
    treino = get_object_or_404(Treino, id_treino=id)

    if payload.nome_treino is not None:
        treino.nome_treino = payload.nome_treino
        treino.save()

    # adicionar exercícios
    if payload.adicionar_exercicios:
        for item in payload.adicionar_exercicios:
            RelTreinoExercicio.objects.update_or_create(
                id_treino=id,
                id_exercicio=item.id_exercicio,
                defaults={
                    "numero_series": item.numero_series,
                    "numero_repeticoes": item.numero_repeticoes,
                }
            )

    # remover exercícios
    if payload.remover_exercicios:
        RelTreinoExercicio.objects.filter(
            id_treino=treino.id_treino,
            id_exercicio__in=payload.remover_exercicios
        ).delete()

    return treino

# Exemplo de json pra edição (nao precisa passar todos os paramentros)
#lembra de passar o id do treino na url, e o metodo é PUT!!!!
# {
#   "nome_treino": "Treino B Completo",
#   "adicionar_exercicios": [
#     {
#       "id_exercicio": 1,
#       "numero_series": 5,
#       "numero_repeticoes": 8
#     }
#   ],
#   "remover_exercicios": [17]
# }

@router.delete("/{id}/")
def excluir_treino(request, id: int):
    treino = get_object_or_404(Treino, id_treino=id)
    treino.delete()
    return {"mensagem": "Treino excluído com sucesso"}

@router.get("/buscar/treino_do_buddy/", response=List[TreinoListSchema])
def buscar_por_treino_do_buddy(request):
    """
    Retorna apenas treinos onde treino_do_buddy = 1.
    """
    return Treino.objects.filter(treino_do_buddy=1)