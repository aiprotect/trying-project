from django.apps import AppConfig

def ready(self):
    import account_module.signals
    
class PanelModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'panel_module'
