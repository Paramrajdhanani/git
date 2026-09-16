from django.urls import path
from . import views

app_name = 'finder'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('user/<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('user/<str:username>/export/csv/', views.ExportCSVView.as_view(), name='export_csv'),
    path('user/<str:username>/export/json/', views.ExportJSONView.as_view(), name='export_json'),
    path('compare/', views.CompareView.as_view(), name='compare'),
    path('org/<str:orgname>/', views.OrgDetailView.as_view(), name='org_detail'),
    path('rate-limit/', views.RateLimitStatusView.as_view(), name='rate_limit'),
    path('trending/', views.TrendingView.as_view(), name='trending'),
    path('search/repos/', views.RepoSearchView.as_view(), name='search_repos'),
    path('api/repo/readme/', views.RepoReadmeView.as_view(), name='repo_readme'),
    path('api/user/<str:username>/events/', views.UserEventsView.as_view(), name='user_events'),
    path('api/autocomplete/', views.AutocompleteView.as_view(), name='autocomplete'),
]

