from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Projeto)
admin.site.register(Sprint)
class CapituloInline(admin.TabularInline):
    model = Capitulo
    extra = 1  # Quantos formulários de capítulo em branco mostrar por padrão.
    ordering = ['ordem']


class SubCapituloInline(admin.TabularInline):
    model = SubCapitulo
    extra = 1  # Quantos formulários de subcapítulo em branco mostrar por padrão.
    ordering = ['ordem']


@admin.register(Ebook)
class EbookAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo',)
    search_fields = ('titulo',)
    # A linha abaixo "anexa" a administração de capítulos à de ebooks.
    inlines = [CapituloInline]


@admin.register(Capitulo)
class CapituloAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'ebook', 'ordem')
    list_filter = ('ebook',)
    search_fields = ('titulo',)
    list_editable = ('ordem',) # Permite editar a ordem diretamente na lista.
    inlines = [SubCapituloInline]


@admin.register(SubCapitulo)
class SubCapituloAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'capitulo', 'tipo', 'ordem')
    list_filter = ('capitulo', 'tipo')
    search_fields = ('titulo',)
    list_editable = ('ordem',) # Permite editar a ordem diretamente na lista.


@admin.register(ProgressoUsuarioEbook)
class ProgressoUsuarioEbookAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'get_capitulo_titulo', 'concluido', 'data_conclusao')
    list_filter = ('concluido', 'aluno')
    search_fields = ('aluno__username', 'capitulo__titulo')

    # Função para buscar o título do capítulo de forma mais elegante.
    @admin.display(description='Capítulo', ordering='capitulo__titulo')
    def get_capitulo_titulo(self, obj):
        return obj.capitulo.titulo


@admin.register(ProgressoUsuarioSubCapitulo)
class ProgressoUsuarioSubCapituloAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'get_subcapitulo_titulo', 'get_subcapitulo_tipo', 'concluido', 'data_conclusao')
    list_filter = ('concluido', 'aluno', 'subcapitulo__tipo')
    search_fields = ('aluno__username', 'subcapitulo__titulo', 'subcapitulo__capitulo__titulo')

    # Função para buscar o título do subcapítulo de forma mais elegante.
    @admin.display(description='Subcapítulo', ordering='subcapitulo__titulo')
    def get_subcapitulo_titulo(self, obj):
        return obj.subcapitulo.titulo

    # Função para buscar o tipo do subcapítulo de forma mais elegante.
    @admin.display(description='Tipo', ordering='subcapitulo__tipo')
    def get_subcapitulo_tipo(self, obj):
        return obj.subcapitulo.get_tipo_display()
