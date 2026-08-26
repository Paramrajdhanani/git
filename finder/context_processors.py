from django.conf import settings

def global_context(request):
    theme = 'dark'
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        theme = request.user.profile.theme_preference
    elif 'theme_preference' in request.session:
        theme = request.session['theme_preference']

    return {
        'current_theme': theme,
        'has_github_token': bool(settings.GITHUB_TOKEN),
    }
