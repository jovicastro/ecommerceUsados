import json
import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, DetailView, ListView
from .forms import CustomUserCreationForm
from .models import *


class Homepage(ListView):
    template_name = 'entrada/index.html'
    model = Estacoe
    context_object_name = "estacoes"

class Desenvolvedores(TemplateView):
    template_name = 'entrada/desenvolvedores.html'


class Sobre(TemplateView):
    template_name = 'entrada/sobre.html' 


class Contato(TemplateView):
    template_name = 'entrada/contato.html'


class Leaderboard(ListView):
    model = User
    template_name = 'entrada/leaderboard.html'
    context_object_name = 'users_list'  # Alterado para corresponder ao template

    def get_queryset(self):
        from .models import UserProfile, Estacoe

        # Obter o filtro de área da query string
        area_filter = self.request.GET.get('area')

        # Iniciar o queryset base
        queryset = UserProfile.objects.select_related('user', 'area')

        # Aplicar filtro por área se fornecido
        if area_filter and area_filter != 'all':
            queryset = queryset.filter(area__nome=area_filter)

        # Ordenar por porcentagem de conclusão
        return queryset.order_by('-ebook_completion_percentage')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Estacoe

        # Adicionar todas as áreas/estações ao contexto para o filtro
        context['areas'] = Estacoe.objects.all()

        # Adicionar a área selecionada ao contexto
        context['selected_area'] = self.request.GET.get('area', 'all')

        return context



class DetalhesEstacaoView(DetailView):
    model = Estacoe
    template_name = 'estacoes/detalhes_estacao.html'
    context_object_name = 'estacao'

    def get_object(self):
        nome_estacao = self.kwargs.get('nome')
        return Estacoe.objects.get(nome=nome_estacao)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Pega a estação atual
        estacao_atual = self.get_object()        
        # Carregar instâncias de cada modelo
        context['estacoes'] = Estacoe.objects.all()
        context['paleta_cor_list'] = Paleta_Core.objects.filter(nome=estacao_atual.cor)
        context['img_equipes'] = Imagens_equipe.objects.filter(estacao=estacao_atual)
        context['img_beneficios_cores'] = Imagens_Beneficios_Core.objects.filter(cor=estacao_atual.cor)[:3]
        context['img_ideais_para'] = Imagens_Ideal_Para_Core.objects.filter(cor=estacao_atual.cor)[:3]

        context['range_simulado'] = range(1, 4)

        return context



@login_required
def add_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            try:
                user.save()

                # Adicionar o usuário ao grupo selecionado
                group = form.cleaned_data.get('groups')
                if group:
                    group.user_set.add(user)

                messages.success(request, f'Usuário {user.username} foi criado com sucesso!')
                return redirect('Core:sobre')  # Redirecione para uma página apropriada
            except Exception as e:
                messages.error(request, f'Ocorreu um erro ao salvar o usuário: {str(e)}')
        else:
            # Caso o formulário não seja válido, podemos passar os erros de forma mais específica
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo {field}: {error}")

    else:
        form = CustomUserCreationForm()

    return render(request, 'entrada/add_user.html', {'form': form})



@login_required
def add_investidor(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            try:
                user.save()

                # Adicionar o usuário ao grupo selecionado
                group = form.cleaned_data.get('groups')
                if group:
                    group.user_set.add(user)

                messages.success(request, f'Investidor {user.username} foi criado com sucesso!')
                return redirect('Core:sobre') 
            except Exception as e:
                messages.error(request, f'Ocorreu um erro ao salvar o investidor: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo {field}: {error}")

    else:
        form = CustomUserCreationForm()

    return render(request, 'entrada/add_investidor.html', {'form': form})


OLLAMA_API_URL = "http://localhost:11434/api/generate"

def chat_page_view(request):
    return render(request, 'entrada/chatbot.html')


@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt')

            if not prompt:
                return JsonResponse({'error': 'Nenhum prompt fornecido.'}, status=400)
            payload = {
                "model": "phi3:mini",
                "prompt": prompt,
                "stream": False
            }

            response = requests.post(OLLAMA_API_URL, json=payload)
            response.raise_for_status()

            ollama_data = response.json()
            return JsonResponse({'response': ollama_data.get('response')})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido.'}, status=400)
        except requests.RequestException as e:
            return JsonResponse({'error': f'Erro ao comunicar com o Ollama: {e}'}, status=500)
        except Exception as e:
            return JsonResponse({'error': f'Ocorreu um erro inesperado: {e}'}, status=500)

    return JsonResponse({'error': 'Método não permitido.'}, status=405)
