from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import SearchHistory

def get_recent_searches(request):
    if request.user.is_authenticated:
        qs = SearchHistory.objects.filter(user=request.user)[:10]
    else:
        if not request.session.session_key:
            request.session.create()
        qs = SearchHistory.objects.filter(session_key=request.session.session_key)[:10]
    
    data = [{'username': item.username, 'avatar_url': item.avatar_url, 'searched_at': item.searched_at.isoformat()} for item in qs]
    return JsonResponse({'status': 'success', 'history': data})

@require_POST
def clear_history(request):
    if request.user.is_authenticated:
        SearchHistory.objects.filter(user=request.user).delete()
    else:
        if request.session.session_key:
            SearchHistory.objects.filter(session_key=request.session.session_key).delete()
    return JsonResponse({'status': 'success', 'message': 'Search history cleared successfully.'})
