from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from history.models import SearchHistory
from favorites.models import FavoriteProfile

@login_required
def index_view(request):
    favorites = FavoriteProfile.objects.filter(user=request.user)[:12]
    search_history = SearchHistory.objects.filter(user=request.user)[:15]
    total_favorites = FavoriteProfile.objects.filter(user=request.user).count()
    total_searches = SearchHistory.objects.filter(user=request.user).count()

    context = {
        'favorites': favorites,
        'search_history': search_history,
        'total_favorites': total_favorites,
        'total_searches': total_searches,
    }
    return render(request, 'dashboard/index.html', context)
