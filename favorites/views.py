import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from .models import FavoriteProfile

@require_POST
def toggle_favorite(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'unauthenticated', 
            'message': 'Please login to save favorites permanently to your dashboard.'
        }, status=401)
    
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        name = data.get('name', '').strip()
        avatar_url = data.get('avatar_url', '').strip()
        bio = data.get('bio', '').strip()

        if not username:
            return JsonResponse({'status': 'error', 'message': 'Username is required.'}, status=400)

        favorite, created = FavoriteProfile.objects.get_or_create(
            user=request.user,
            username=username,
            defaults={'name': name, 'avatar_url': avatar_url, 'bio': bio}
        )

        if not created:
            favorite.delete()
            return JsonResponse({'status': 'success', 'is_favorite': False, 'message': f'Removed @{username} from favorites.'})
        else:
            return JsonResponse({'status': 'success', 'is_favorite': True, 'message': f'Added @{username} to your favorites!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_GET
def check_favorite_status(request, username):
    if not request.user.is_authenticated:
        return JsonResponse({'is_favorite': False})
    
    is_fav = FavoriteProfile.objects.filter(user=request.user, username=username).exists()
    return JsonResponse({'is_favorite': is_fav})
