import random
from django.db import models
from django.contrib.auth.models import User
from Core.models import Estacoe

def generate_random_number():
    return random.randint(1000000000, 9999999999)  

OPCOES_STATUS = [
    ("Em_andamento", "Em_andamento"),
    ("Standy-by", "Standy-by"),
    ("Concluido", "Concluido"),
    ("Atrasado", "Atrasado"),
]

OPCOES_FASE = [
    ("Andamento", "Andamento"),
    ("Concluido", "Concluido"),
    ("Descontinuado", "Descontinuado"),
]

class Projeto(models.Model):
    estacao_projeto = models.ForeignKey(Estacoe, on_delete=models.CASCADE, null=True, blank=True) 
    id = models.BigIntegerField(unique=True, primary_key=True, default=f"{generate_random_number}") 
    nome_projeto = models.CharField(max_length=255)
    numero_desafio = models.IntegerField(unique=True)
    Proprietario = models.CharField(max_length=200)
    gestor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projetos_gestor')  # Adicionando related_name
    start_date = models.DateField()
    fase = models.CharField(max_length=100, choices=OPCOES_FASE, default="Andamento")
    end_date = models.DateField()
    status = models.CharField(max_length=255, choices=OPCOES_STATUS, default="Em_andamento")
    Progresso = models.IntegerField(default=0)
    integrantes = models.ManyToManyField(User, related_name='projetos_integrantes')  # Adicionando related_name

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_random_number()  
        super().save(*args, **kwargs)  

    def __str__(self):
        return f"Projeto {self.nome_projeto}, id do projeto ({self.id})"  

class Sprint(models.Model):
    id = models.BigIntegerField(unique=True, primary_key=True)  
    Projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    numero_sprint = models.IntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_random_number()  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.id})"

class Ebook(models.Model):
    titulo = models.CharField(max_length=200, unique=True)
    descricao = models.TextField(blank=True, null=True)

class Capitulo(models.Model):
    ebook = models.ForeignKey(Ebook, on_delete=models.CASCADE, related_name='capitulos')
    titulo = models.CharField(max_length=255)
    # O conteúdo pode ser um TextField com Markdown/HTML ou um FileField para PDFs
    conteudo = models.TextField(blank=True, null=True) 
    ordem = models.PositiveIntegerField(default=0, help_text="Define a ordem de exibição do capítulo")

    class Meta:
        ordering = ['ordem'] # Garante que os capítulos sempre venham ordenados

    def __str__(self):
        return f"{self.ebook.titulo} - Cap. {self.ordem}: {self.titulo}"

TIPO_SUBCAPITULO_CHOICES = [
    ('pdf', 'PDF'),
    ('video', 'Vídeo'),
    ('texto', 'Texto'),
    ('exercicio', 'Exercício'),
]

class SubCapitulo(models.Model):
    capitulo = models.ForeignKey(Capitulo, on_delete=models.CASCADE, related_name='subcapitulos')
    titulo = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPO_SUBCAPITULO_CHOICES, default='texto')
    conteudo = models.TextField(blank=True, null=True)
    arquivo = models.FileField(upload_to='subcapitulos/', blank=True, null=True)
    url_video = models.URLField(blank=True, null=True)
    ordem = models.PositiveIntegerField(default=0, help_text="Define a ordem de exibição do subcapítulo")

    class Meta:
        ordering = ['ordem']
        verbose_name = 'Subcapítulo'
        verbose_name_plural = 'Subcapítulos'

    def __str__(self):
        return f"{self.capitulo.titulo} - {self.get_tipo_display()}: {self.titulo}"

class ProgressoUsuarioEbook(models.Model):
    aluno = models.ForeignKey(User, on_delete=models.CASCADE)
    capitulo = models.ForeignKey(Capitulo, on_delete=models.CASCADE)
    concluido = models.BooleanField(default=False)
    data_conclusao = models.DateTimeField(auto_now=True)

    class Meta:
        # Garante que um usuário só tenha um registro de progresso por capítulo
        unique_together = ('aluno', 'capitulo') 

    def __str__(self):
        return f"Progresso de {self.aluno.username} em '{self.capitulo.titulo}'"

class ProgressoUsuarioSubCapitulo(models.Model):
    aluno = models.ForeignKey(User, on_delete=models.CASCADE)
    subcapitulo = models.ForeignKey(SubCapitulo, on_delete=models.CASCADE)
    concluido = models.BooleanField(default=False)
    data_conclusao = models.DateTimeField(auto_now=True)

    class Meta:
        # Garante que um usuário só tenha um registro de progresso por subcapítulo
        unique_together = ('aluno', 'subcapitulo')
        verbose_name = 'Progresso de Subcapítulo'
        verbose_name_plural = 'Progressos de Subcapítulos'

    def __str__(self):
        return f"Progresso de {self.aluno.username} em '{self.subcapitulo.titulo}'"
