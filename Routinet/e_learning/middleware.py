from django.utils import translation

class LanguageMiddleware:
    """Active la langue sur toutes les requêtes selon LANGUAGE_CODE"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = getattr(request, 'LANGUAGE_CODE', 'fr')
        translation.activate(lang)
        response = self.get_response(request)
        translation.deactivate()
        return response
