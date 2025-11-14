from ninja import Router
from typing import List
from django.shortcuts import get_object_or_404
from tb_app.models import Exercicios, NivelDificuldade, RelExerciciosMusculos, MusculosEnvolvidos
from api.schemas import ExerciciosListSchema, ExerciciosDetailSchema, MusculosEnvolvidosSchema, NivelDificuldadeSchema

router = Router(tags=["Exercícios"])

@router.get("/", response=List[ExerciciosListSchema])
def listar_exercicios(request):
    return Exercicios.objects.all()

@router.get("/{id}/", response=ExerciciosDetailSchema)
def exercicio_detail(request, id: int):
    ex = get_object_or_404(Exercicios, id_exercicios=id)

    nivel = None
    if ex.id_nivel_dificuldade_id is not None:
        nivel_obj = NivelDificuldade.objects.filter(pk=ex.id_nivel_dificuldade_id).first()
        if nivel_obj:
            nivel = NivelDificuldadeSchema.from_orm(nivel_obj)

    rels = RelExerciciosMusculos.objects.filter(id_exercicio=ex.id_exercicios)
    musculos = []
    # atenção: na sua model, RelExerciciosMusculos.armazena id_musculo (inteiro)
    mus_ids = [r.id_musculo for r in rels]
    if mus_ids:
        mus_objs = MusculosEnvolvidos.objects.filter(id_musculos_envolvidos__in=mus_ids)
        for m in mus_objs:
            musculos.append(MusculosEnvolvidosSchema.from_orm(m))

    # construir resposta conforme ExerciciosDetailSchema
    return {
        "id_exercicios": ex.id_exercicios,
        "nome_exercicio": ex.nome_exercicio,
        "descricao": ex.descricao,
        "nivel_dificuldade": nivel,
        "musculos": musculos,
        "imagem": ex.imagem.url if getattr(ex, "imagem", None) else None,
        "link_ia": getattr(ex, "link_ia", None),
        "video": getattr(ex, "video", None),
    }

@router.get("/buscar/nivel/{nivel_id}/", response=List[ExerciciosListSchema])
def buscar_por_nivel(request, nivel_id: int):
    return Exercicios.objects.filter(id_nivel_dificuldade=nivel_id)

@router.get("/buscar/nome/", response=List[ExerciciosListSchema])
def buscar_por_nome(request, q: str):
    """
    Filtro case-insensitive usando contains.
    Exemplo: /buscar/nome/?q=ab
    """
    return Exercicios.objects.filter(nome_exercicio__istartswith=q)