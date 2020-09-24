"""
Django AppConfig module for the Gating app
"""


from django.apps import AppConfig


class GatingConfig(AppConfig):
    """
    Django AppConfig class for the gating app
    """
    name = 'gating'

    def ready(self):
        pass
