import requests
from datetime import datetime
from django.core.cache import cache
from django.conf import settings

BASE_URL = 'https://api.github.com'

class GitHubAPIError(Exception):
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.status_code = status_code

class GitHubAPIService:
    @staticmethod
    def _get_headers():
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Django-GitHub-Profile-Finder/1.0'
        }
        token = getattr(settings, 'GITHUB_TOKEN', '')
        if token:
            headers['Authorization'] = f'token {token}'
        return headers

    @classmethod
    def fetch_data(cls, endpoint, timeout=8):
        cache_key = f"gh_api_{endpoint.replace('/', '_')}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.get(url, headers=cls._get_headers(), timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                cache.set(cache_key, data, timeout=900)  # 15 mins cache
                return data
            elif response.status_code == 404:
                raise GitHubAPIError("GitHub user or resource not found.", status_code=404)
            elif response.status_code == 403:
                raise GitHubAPIError("GitHub API rate limit exceeded. Please try again later or add a GitHub Token in settings.", status_code=403)
            else:
                raise GitHubAPIError(f"GitHub API Error (HTTP {response.status_code})", status_code=response.status_code)
        except requests.Timeout:
            raise GitHubAPIError("GitHub API request timed out. Please try again.", status_code=504)
        except requests.RequestException as e:
            raise GitHubAPIError(f"Network error connecting to GitHub: {str(e)}", status_code=503)

    @classmethod
    def get_user_profile(cls, username):
        return cls.fetch_data(f"/users/{username}")

    @classmethod
    def get_user_repos(cls, username, per_page=100):
        return cls.fetch_data(f"/users/{username}/repos?per_page={per_page}&sort=updated")

    @classmethod
    def get_user_followers(cls, username, per_page=30):
        return cls.fetch_data(f"/users/{username}/followers?per_page={per_page}")

    @classmethod
    def get_user_following(cls, username, per_page=30):
        return cls.fetch_data(f"/users/{username}/following?per_page={per_page}")

    @classmethod
    def get_user_orgs(cls, username):
        try:
            return cls.fetch_data(f"/users/{username}/orgs")
        except Exception:
            return []

    @classmethod
    def get_org_details(cls, orgname):
        return cls.fetch_data(f"/orgs/{orgname}")

    @classmethod
    def get_org_repos(cls, orgname):
        return cls.fetch_data(f"/orgs/{orgname}/repos?per_page=100&sort=updated")

    @classmethod
    def get_rate_limit(cls):
        url = f"{BASE_URL}/rate_limit"
        try:
            res = requests.get(url, headers=cls._get_headers(), timeout=5)
            if res.status_code == 200:
                return res.json().get('resources', {}).get('core', {})
        except Exception:
            pass
        return {'limit': 60, 'remaining': 60, 'reset': 0}

    @classmethod
    def get_github_status(cls):
        try:
            res = requests.get("https://www.githubstatus.com/api/v2/status.json", timeout=4)
            if res.status_code == 200:
                return res.json().get('status', {})
        except Exception:
            pass
        return {'indicator': 'none', 'description': 'All Systems Operational'}


class SkillAnalyzerService:
    @staticmethod
    def analyze_profile(repos, profile_data):
        languages = {}
        total_stars = 0
        total_forks = 0
        total_watchers = 0
        top_repo = None
        most_popular_repo = None
        max_stars = -1

        for repo in repos:
            stars = repo.get('stargazers_count', 0)
            forks = repo.get('forks_count', 0)
            watchers = repo.get('watchers_count', 0)
            lang = repo.get('language')

            total_stars += stars
            total_forks += forks
            total_watchers += watchers

            if lang:
                languages[lang] = languages.get(lang, 0) + 1

            if stars > max_stars:
                max_stars = stars
                top_repo = repo
                most_popular_repo = repo

        # Sort languages
        sorted_languages = dict(sorted(languages.items(), key=lambda item: item[1], reverse=True))
        total_lang_repos = sum(sorted_languages.values()) or 1
        lang_percentages = {k: round((v / total_lang_repos) * 100, 1) for k, v in sorted_languages.items()}

        # Primary stack determination
        primary_lang = next(iter(sorted_languages), 'Polyglot')
        if primary_lang in ['Python', 'Django', 'Flask', 'FastAPI']:
            developer_type = 'Backend & Data Engineer'
        elif primary_lang in ['JavaScript', 'TypeScript', 'HTML', 'CSS', 'Vue', 'React']:
            developer_type = 'Frontend & Web Developer'
        elif primary_lang in ['Java', 'C#', 'Go', 'Rust', 'C++']:
            developer_type = 'Systems & Software Architect'
        else:
            developer_type = 'Full-Stack Developer'

        return {
            'total_stars': total_stars,
            'total_forks': total_forks,
            'total_watchers': total_watchers,
            'languages': sorted_languages,
            'lang_percentages': lang_percentages,
            'top_repo': top_repo,
            'most_popular_repo': most_popular_repo,
            'developer_type': developer_type,
            'primary_language': primary_lang,
            'repo_count': len(repos),
        }


class AISummaryService:
    @staticmethod
    def generate_summary(profile, stats):
        username = profile.get('login', '')
        name = profile.get('name') or username
        followers = profile.get('followers', 0)
        public_repos = profile.get('public_repos', 0)
        created_year = profile.get('created_at', '')[:4] if profile.get('created_at') else ''
        primary_lang = stats.get('primary_language', 'coding')
        total_stars = stats.get('total_stars', 0)
        dev_type = stats.get('developer_type', 'Software Engineer')

        bullets = []

        # Bullet 1: Experience & Focus
        if created_year:
            bullets.append(f"Active GitHub developer since {created_year}, primary specialization in **{primary_lang}** ({dev_type}).")
        else:
            bullets.append(f"Specialized in **{primary_lang}** development with {public_repos} public repositories.")

        # Bullet 2: Community & Impact
        if total_stars > 100 or followers > 50:
            bullets.append(f"High-impact open-source contributor with **{total_stars:,} total stars** and **{followers:,} followers**.")
        elif total_stars > 0:
            bullets.append(f"Earned **{total_stars} stars** across public repositories with a growing community presence.")
        else:
            bullets.append(f"Actively building public repositories with {public_repos} projects hosted on GitHub.")

        # Bullet 3: Highlight Repo
        top_repo = stats.get('top_repo')
        if top_repo and top_repo.get('stargazers_count', 0) > 0:
            bullets.append(f"Flagship repository: **[{top_repo.get('name')}]({top_repo.get('html_url')})** with {top_repo.get('stargazers_count')} stars.")
        elif public_repos > 0:
            bullets.append(f"Consistently publishes clean open-source code and project repositories.")

        # Bullet 4: Hireable signal
        if profile.get('hireable'):
            bullets.append("Status: **Open to job opportunities**.")

        return {
            'headline': f"{name} is a {dev_type} specializing in {primary_lang}.",
            'insights': bullets
        }
