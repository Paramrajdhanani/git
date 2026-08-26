from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView, View
from django.contrib import messages
from .services import GitHubAPIService, SkillAnalyzerService, AISummaryService, GitHubAPIError
from .utils import generate_repos_csv, format_date, format_size_kb
from history.models import SearchHistory
from favorites.models import FavoriteProfile

TRENDING_DEVELOPERS = [
    {'username': 'torvalds', 'name': 'Linus Torvalds', 'avatar_url': 'https://avatars.githubusercontent.com/u/10240?v=4', 'bio': 'Creator of Linux & Git', 'lang': 'C'},
    {'username': 'gvanrossum', 'name': 'Guido van Rossum', 'avatar_url': 'https://avatars.githubusercontent.com/u/152588?v=4', 'bio': 'Creator of Python programming language', 'lang': 'Python'},
    {'username': 'gaearon', 'name': 'Dan Abramov', 'avatar_url': 'https://avatars.githubusercontent.com/u/810438?v=4', 'bio': 'Co-author of Redux & Create React App', 'lang': 'JavaScript'},
    {'username': 'yyx99', 'name': 'Evan You', 'avatar_url': 'https://avatars.githubusercontent.com/u/499550?v=4', 'bio': 'Creator of Vue.js & Vite', 'lang': 'TypeScript'},
    {'username': 'karpathy', 'name': 'Andrej Karpathy', 'avatar_url': 'https://avatars.githubusercontent.com/u/241138?v=4', 'bio': 'AI researcher, creator of nanoGPT & minGPT', 'lang': 'Python'},
    {'username': 'sindresorhus', 'name': 'Sindre Sorhus', 'avatar_url': 'https://avatars.githubusercontent.com/u/170270?v=4', 'bio': 'Full-time Open-Sourcerer & module creator', 'lang': 'TypeScript'},
    {'username': 'tj', 'name': 'TJ Holowaychuk', 'avatar_url': 'https://avatars.githubusercontent.com/u/25254?v=4', 'bio': 'Apex, Go & Node.js open-source pioneer', 'lang': 'Go'},
    {'username': 'Rich-Harris', 'name': 'Rich Harris', 'avatar_url': 'https://avatars.githubusercontent.com/u/1162160?v=4', 'bio': 'Creator of Svelte framework & Rollup', 'lang': 'JavaScript'},
    {'username': 'mitsuhiko', 'name': 'Armin Ronacher', 'avatar_url': 'https://avatars.githubusercontent.com/u/7396?v=4', 'bio': 'Creator of Flask, Jinja2 & Sentry co-founder', 'lang': 'Rust'},
    {'username': 'mitchellh', 'name': 'Mitchell Hashimoto', 'avatar_url': 'https://avatars.githubusercontent.com/u/13316?v=4', 'bio': 'Creator of Vagrant, Terraform & Ghostty', 'lang': 'Go'},
    {'username': 'shadcn', 'name': 'shadcn', 'avatar_url': 'https://avatars.githubusercontent.com/u/124599?v=4', 'bio': 'Creator of shadcn/ui component library', 'lang': 'TypeScript'},
    {'username': 'dhh', 'name': 'David Heinemeier Hansson', 'avatar_url': 'https://avatars.githubusercontent.com/u/2741?v=4', 'bio': 'Creator of Ruby on Rails & 37signals founder', 'lang': 'Ruby'},
    {'username': 'addyosmani', 'name': 'Addy Osmani', 'avatar_url': 'https://avatars.githubusercontent.com/u/110953?v=4', 'bio': 'Engineering Lead on Google Chrome & Web Performance', 'lang': 'JavaScript'},
    {'username': 'antirez', 'name': 'Salvatore Sanfilippo', 'avatar_url': 'https://avatars.githubusercontent.com/u/65632?v=4', 'bio': 'Creator of Redis database', 'lang': 'C'},
    {'username': 'octocat', 'name': 'The Octocat', 'avatar_url': 'https://avatars.githubusercontent.com/u/583231?v=4', 'bio': 'GitHub mascot & official test account', 'lang': 'Ruby'},
]

class HomeView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        if query:
            return redirect('finder:profile', username=query)

        # Recent searches from session or DB
        recent_searches = []
        if request.user.is_authenticated:
            recent_searches = SearchHistory.objects.filter(user=request.user)[:8]
        else:
            if request.session.session_key:
                recent_searches = SearchHistory.objects.filter(session_key=request.session.session_key)[:8]

        context = {
            'trending_devs': TRENDING_DEVELOPERS[:6],
            'recent_searches': recent_searches,
        }
        return render(request, 'finder/home.html', context)


class ProfileView(View):
    def get(self, request, username):
        username = username.strip().lower()
        try:
            profile = GitHubAPIService.get_user_profile(username)
            repos = GitHubAPIService.get_user_repos(username)
            user_orgs = GitHubAPIService.get_user_orgs(username)
            
            # Analytics & Summaries
            stats = SkillAnalyzerService.analyze_profile(repos, profile)
            ai_summary = AISummaryService.generate_summary(profile, stats)

            # Record in Search History
            try:
                user_obj = request.user if request.user.is_authenticated else None
                session_key = None if request.user.is_authenticated else request.session.session_key
                if not user_obj and not session_key:
                    request.session.create()
                    session_key = request.session.session_key
                
                # Check duplicate search within last minute
                SearchHistory.objects.create(
                    user=user_obj,
                    session_key=session_key,
                    username=username,
                    avatar_url=profile.get('avatar_url', '')
                )
            except Exception:
                pass

            # Check favorite status for user
            is_favorite = False
            if request.user.is_authenticated:
                is_favorite = FavoriteProfile.objects.filter(user=request.user, username=username).exists()

            # Format Dates, Sizes, & Download Links for Repos
            for repo in repos:
                repo['formatted_created'] = format_date(repo.get('created_at'))
                repo['formatted_updated'] = format_date(repo.get('updated_at'))
                repo['formatted_size'] = format_size_kb(repo.get('size', 0))
                default_branch = repo.get('default_branch', 'main')
                repo['zip_download_url'] = f"{repo.get('html_url')}/archive/refs/heads/{default_branch}.zip"
                repo['clone_url'] = repo.get('clone_url') or f"https://github.com/{username}/{repo.get('name')}.git"
                if isinstance(repo.get('license'), dict):
                    repo['license_name'] = repo.get('license', {}).get('spdx_id') or repo.get('license', {}).get('name') or ''
                else:
                    repo['license_name'] = ''

            context = {
                'profile': profile,
                'repos': repos,
                'stats': stats,
                'ai_summary': ai_summary,
                'user_orgs': user_orgs,
                'is_favorite': is_favorite,
                'created_formatted': format_date(profile.get('created_at')),
                'updated_formatted': format_date(profile.get('updated_at')),
            }
            return render(request, 'finder/profile.html', context)

        except GitHubAPIError as e:
            return render(request, 'finder/profile_error.html', {
                'username': username,
                'error_message': str(e),
                'status_code': e.status_code
            }, status=e.status_code)


class CompareView(View):
    def get(self, request):
        u1 = request.GET.get('u1', '').strip()
        u2 = request.GET.get('u2', '').strip()

        if not u1 or not u2:
            return render(request, 'finder/compare.html', {
                'u1': u1 or 'torvalds',
                'u2': u2 or 'gaearon',
                'comparison': None
            })

        try:
            p1 = GitHubAPIService.get_user_profile(u1)
            r1 = GitHubAPIService.get_user_repos(u1)
            s1 = SkillAnalyzerService.analyze_profile(r1, p1)

            p2 = GitHubAPIService.get_user_profile(u2)
            r2 = GitHubAPIService.get_user_repos(u2)
            s2 = SkillAnalyzerService.analyze_profile(r2, p2)

            comparison = {
                'user1': {'profile': p1, 'stats': s1},
                'user2': {'profile': p2, 'stats': s2},
                'winners': {
                    'followers': u1 if p1.get('followers', 0) >= p2.get('followers', 0) else u2,
                    'repos': u1 if p1.get('public_repos', 0) >= p2.get('public_repos', 0) else u2,
                    'stars': u1 if s1['total_stars'] >= s2['total_stars'] else u2,
                    'forks': u1 if s1['total_forks'] >= s2['total_forks'] else u2,
                }
            }

            return render(request, 'finder/compare.html', {
                'u1': u1,
                'u2': u2,
                'comparison': comparison
            })
        except GitHubAPIError as e:
            messages.error(request, f"Could not perform comparison: {str(e)}")
            return render(request, 'finder/compare.html', {'u1': u1, 'u2': u2, 'comparison': None})


class OrgDetailView(View):
    def get(self, request, orgname):
        orgname = orgname.strip()
        try:
            org = GitHubAPIService.get_org_details(orgname)
            repos = GitHubAPIService.get_org_repos(orgname)
            for repo in repos:
                repo['formatted_created'] = format_date(repo.get('created_at'))
                repo['formatted_updated'] = format_date(repo.get('updated_at'))
                repo['formatted_size'] = format_size_kb(repo.get('size', 0))
                default_branch = repo.get('default_branch', 'main')
                repo['zip_download_url'] = f"{repo.get('html_url')}/archive/refs/heads/{default_branch}.zip"
                repo['clone_url'] = repo.get('clone_url') or f"https://github.com/{orgname}/{repo.get('name')}.git"
            return render(request, 'finder/org_detail.html', {'org': org, 'repos': repos})
        except GitHubAPIError as e:
            messages.error(request, f"Organization Error: {str(e)}")
            return redirect('finder:home')


class RateLimitStatusView(View):
    def get(self, request):
        rate_info = GitHubAPIService.get_rate_limit()
        status_info = GitHubAPIService.get_github_status()
        
        limit = rate_info.get('limit', 60) or 60
        remaining = rate_info.get('remaining', 0)
        rate_info['percentage'] = round((remaining / limit) * 100) if limit else 0

        return render(request, 'finder/rate_limit.html', {
            'rate_limit': rate_info,
            'github_status': status_info
        })


class TrendingView(View):
    def get(self, request):
        return render(request, 'finder/trending.html', {'trending_devs': TRENDING_DEVELOPERS})


class ExportCSVView(View):
    def get(self, request, username):
        try:
            repos = GitHubAPIService.get_user_repos(username)
            csv_data = generate_repos_csv(username, repos)
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{username}_repositories.csv"'
            return response
        except Exception as e:
            messages.error(request, f"Could not generate CSV: {str(e)}")
            return redirect('finder:profile', username=username)


class ExportJSONView(View):
    def get(self, request, username):
        try:
            profile = GitHubAPIService.get_user_profile(username)
            repos = GitHubAPIService.get_user_repos(username)
            stats = SkillAnalyzerService.analyze_profile(repos, profile)
            ai_summary = AISummaryService.generate_summary(profile, stats)
            user_orgs = GitHubAPIService.get_user_orgs(username)

            import json
            export_data = {
                'profile': profile,
                'stats': stats,
                'ai_summary': ai_summary,
                'organizations': user_orgs,
                'repositories': repos,
                'exported_at': datetime.now().isoformat()
            }
            json_dump = json.dumps(export_data, indent=2)
            response = HttpResponse(json_dump, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{username}_profile.json"'
            return response
        except Exception as e:
            messages.error(request, f"Could not generate JSON export: {str(e)}")
            return redirect('finder:profile', username=username)


class AutocompleteView(View):
    def get(self, request):
        q = request.GET.get('q', '').strip().lower()
        if not q:
            return JsonResponse({'suggestions': []})

        # Match against popular dev list and search history
        suggestions = []
        for dev in TRENDING_DEVELOPERS:
            if q in dev['username'].lower() or q in dev['name'].lower():
                suggestions.append({
                    'username': dev['username'],
                    'name': dev['name'],
                    'avatar_url': dev['avatar_url']
                })
        
        # Also query search history for matching entries
        hist_matches = SearchHistory.objects.filter(username__icontains=q).values('username', 'avatar_url').distinct()[:5]
        for item in hist_matches:
            if not any(s['username'] == item['username'] for s in suggestions):
                suggestions.append({
                    'username': item['username'],
                    'name': item['username'],
                    'avatar_url': item['avatar_url'] or f"https://github.com/{item['username']}.png"
                })

        return JsonResponse({'suggestions': suggestions[:6]})
