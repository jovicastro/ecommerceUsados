from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Core'
def ready(self):
    from Core.service import chatbot_service
    chatbot_service.setup_rag_chain()