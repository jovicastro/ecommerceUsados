from django.urls import path 
from .views import (
    IndexDashboardView, DetalhesProjetosEstacoes, Visualizar_Projeto_individual, 
    EbookEstacoesView, PerfilUser, EbookDetailView, marcar_capitulo_concluido,
    marcar_subcapitulo_concluido,
)

app_name = "Dashboard"

urlpatterns = [
    path('', IndexDashboardView.as_view(), name="index_estacao"),
    path('listar_projetos/<str:nome>/', DetalhesProjetosEstacoes.as_view(), name="list_estacao"),
    path('visualizar_detalhes/<int:id>/', Visualizar_Projeto_individual.as_view(), name="visualizar_detalhes"),
    path('ebook/', EbookEstacoesView.as_view(), name="ebook_estacoes"),
    path('user/', PerfilUser.as_view(), name="user"),
    path('ebook/<int:pk>/capitulo/<int:capitulo_id>/', EbookDetailView.as_view(), name='capitulo_detalhe'),
    path('ebook/<int:pk>/', EbookDetailView.as_view(), name='ebook_detalhe'),
    path('capitulo/marcar-concluido/<int:capitulo_id>/', marcar_capitulo_concluido, name='marcar_concluido'),
    path('marcar_subcapitulo_concluido/', marcar_subcapitulo_concluido, name='marcar_subcapitulo_concluido'),
]
