from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.models import User 
from .models import Ebook, Capitulo, ProgressoUsuarioEbook, Projeto, SubCapitulo, ProgressoUsuarioSubCapitulo
from Core.models import Estacoe
from .models import Ebook
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.http import HttpRequest, HttpResponse

# Protegendo views com LoginRequiredMixin
class IndexDashboardView(LoginRequiredMixin, ListView):
    template_name = "index_dash.html"
    model = Estacoe
    context_object_name = "estacoes_get"


class DetalhesProjetosEstacoes(LoginRequiredMixin, DetailView):
    model = Estacoe
    template_name = 'list_dashboard.html'
    context_object_name = 'estacao'

    def get_object(self):
        nome_estacao = self.kwargs.get('nome')
        return Estacoe.objects.get(nome=nome_estacao)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estação atual
        estacao_atual = self.get_object()

        # Projetos associados à estação atual
        projetos = Projeto.objects.filter(estacao_projeto=estacao_atual)

        # Calcular os números de status e fases
        context['projetos_get'] = projetos
        context['total_em_andamento'] = projetos.filter(status="Em_andamento").count()
        context['stand_by'] = projetos.filter(fase="Standy-by").count()
        context['concluido'] = projetos.filter(fase="Concluido").count()
        context['atrasado'] = projetos.filter(status="Atrasado").count()
        return context

class Visualizar_Projeto_individual(LoginRequiredMixin, DetailView):
    model = Projeto
    template_name = 'detalhes_projeto_indv.html'
    context_object_name = 'projeto'

    def get_object(self):
        projeto_id = self.kwargs.get('id')
        return Projeto.objects.get(id=projeto_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projeto'] = self.object  
        return context

class EbookEstacoesView(ListView):
    model = Ebook  # 1. Especifica qual modelo listar.
    template_name = 'ebook_estacoes.html'  # 2. Aponta para o seu template.
    context_object_name = 'ebooks_list'  # 3. Define o nome da lista de objetos no contexto.

class EbookDetailView(LoginRequiredMixin, DetailView):
    model = Ebook
    template_name = "att_ebooks/index_ebooks.html" #
    context_object_name = 'ebook'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ebook = self.get_object()
        aluno = self.request.user

        # 1. Pega todos os capítulos do E-book
        todos_capitulos = ebook.capitulos.all()
        context['todos_capitulos'] = todos_capitulos

        # 2. Lógica de cálculo da porcentagem
        total_capitulos_count = todos_capitulos.count()
        if total_capitulos_count > 0:
            capitulos_concluidos_count = ProgressoUsuarioEbook.objects.filter(
                aluno=aluno,
                capitulo__in=todos_capitulos,
                concluido=True
            ).count()

            percentual = (capitulos_concluidos_count / total_capitulos_count) * 100
            context['percentual_progresso'] = round(percentual)
        else:
            context['percentual_progresso'] = 0

        # 3. Passa os IDs dos capítulos concluídos para o template (para estilização)
        context['capitulos_concluidos_ids'] = list(ProgressoUsuarioEbook.objects.filter(
            aluno=aluno, concluido=True
        ).values_list('capitulo_id', flat=True))

        capitulo_id_da_url = self.kwargs.get('capitulo_id') 

        if capitulo_id_da_url:
            # Se a URL especificou um capítulo (ex: /ebook/1/capitulo/5/),
            # busca esse capítulo específico no banco de dados.
            context['capitulo_atual'] = get_object_or_404(Capitulo, id=capitulo_id_da_url, ebook=ebook)
        else:
            # Se a URL for genérica (ex: /ebook/1/), exibe o primeiro capítulo
            # como um ponto de partida padrão.
            context['capitulo_atual'] = todos_capitulos.first()

        # NOVO: Adiciona os subcapítulos do capítulo atual ao contexto
        if context['capitulo_atual']:
            context['subcapitulos'] = context['capitulo_atual'].subcapitulos.all()

            # Adiciona os IDs dos subcapítulos concluídos para estilização
            from .models import ProgressoUsuarioSubCapitulo
            context['subcapitulos_concluidos_ids'] = list(ProgressoUsuarioSubCapitulo.objects.filter(
                aluno=aluno, concluido=True
            ).values_list('subcapitulo_id', flat=True))

        return context

# View para a ação de marcar um capítulo como concluído.
# É uma função separada que só aceita POST para segurança.
@require_POST
def marcar_capitulo_concluido(request: HttpRequest, capitulo_id: int) -> HttpResponse:
    """
    Marca um capítulo como concluído para o usuário logado e avança para o próximo.
    """
    # 1. Buscamos o capítulo usando o ID da URL e o nomeamos 'capitulo'.
    # Este é o nome que usaremos dentro desta função.
    capitulo = get_object_or_404(Capitulo, id=capitulo_id)

    # 2. Criamos ou obtemos o registro de progresso.
    # Usamos a variável 'capitulo' que acabamos de definir.
    ProgressoUsuarioEbook.objects.update_or_create(
        aluno=request.user,
        capitulo=capitulo,
        defaults={'concluido': True}
    )

    # 3. Lógica para encontrar o próximo capítulo
    proximo_capitulo = Capitulo.objects.filter(
        ebook=capitulo.ebook,
        ordem__gt=capitulo.ordem
    ).order_by('ordem').first()

    # 4. Redirecionamento inteligente
    if proximo_capitulo:
        # Se houver um próximo, redireciona para ele.
        return redirect('Dashboard:capitulo_detalhe', pk=proximo_capitulo.ebook.pk, capitulo_id=proximo_capitulo.id)
    else:
        # Se não houver próximo capítulo, redireciona para a lista de capítulos do E-book.
        return redirect('Dashboard:ebook_detalhe', pk=capitulo.ebook.pk)


class PerfilUser(LoginRequiredMixin, TemplateView):
    template_name = "user.html"


@require_POST
def marcar_subcapitulo_concluido(request):
    """
    Marca um subcapítulo como concluído/não concluído para o usuário atual.
    """
    subcapitulo_id = request.POST.get('subcapitulo_id')
    
    if not subcapitulo_id:
        return redirect('Dashboard:index_estacao')
    
    try:
        subcapitulo = get_object_or_404(SubCapitulo, id=subcapitulo_id)
        aluno = request.user
        
        # Busca ou cria o progresso do usuário para este subcapítulo
        progresso, created = ProgressoUsuarioSubCapitulo.objects.get_or_create(
            aluno=aluno,
            subcapitulo=subcapitulo,
            defaults={'concluido': True}
        )
        
        if not created:
            # Se já existia, alterna o estado
            progresso.concluido = not progresso.concluido
            progresso.save()
        
        # Redireciona de volta para o capítulo do subcapítulo
        return redirect('Dashboard:capitulo_detalhe', pk=subcapitulo.capitulo.ebook.id, capitulo_id=subcapitulo.capitulo.id)
        
    except Exception as e:
        # Em caso de erro, redireciona para o dashboard
        return redirect('Dashboard:index_estacao')