from ninja import NinjaAPI
from api.routers import (
    exercicios,
    treinos,
    pessoa,
    planos,
)

api = NinjaAPI()

api.add_router("/exercicios", exercicios.router)
api.add_router("/treinos", treinos.router)
api.add_router("/pessoa", pessoa.router)
api.add_router("/planos", planos.router)