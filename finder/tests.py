from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from finder.services import SkillAnalyzerService, AISummaryService

class FinderServicesTest(TestCase):
    def test_skill_analyzer(self):
        mock_repos = [
            {'name': 'repo1', 'stargazers_count': 10, 'forks_count': 2, 'watchers_count': 10, 'language': 'Python', 'size': 100},
            {'name': 'repo2', 'stargazers_count': 50, 'forks_count': 5, 'watchers_count': 50, 'language': 'Python', 'size': 500},
            {'name': 'repo3', 'stargazers_count': 5, 'forks_count': 1, 'watchers_count': 5, 'language': 'JavaScript', 'size': 200},
        ]
        profile = {'login': 'testdev', 'followers': 20, 'public_repos': 3}
        
        stats = SkillAnalyzerService.analyze_profile(mock_repos, profile)
        self.assertEqual(stats['total_stars'], 65)
        self.assertEqual(stats['total_forks'], 8)
        self.assertEqual(stats['primary_language'], 'Python')
        self.assertIn('Python', stats['languages'])

    def test_ai_summary_generator(self):
        profile = {
            'login': 'torvalds',
            'name': 'Linus Torvalds',
            'followers': 200000,
            'public_repos': 10,
            'created_at': '2011-09-03T15:26:22Z',
            'hireable': True
        }
        stats = {
            'primary_language': 'C',
            'total_stars': 150000,
            'developer_type': 'Systems Engineer',
            'top_repo': {'name': 'linux', 'html_url': 'https://github.com/torvalds/linux', 'stargazers_count': 170000}
        }
        
        summary = AISummaryService.generate_summary(profile, stats)
        self.assertIn('Linus Torvalds', summary['headline'])
        self.assertTrue(len(summary['insights']) >= 3)


class FinderViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page(self):
        response = self.client.get(reverse('finder:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "GitHub Finder")

    def test_trending_page(self):
        response = self.client.get(reverse('finder:trending'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Trending GitHub Developers")

    def test_rate_limit_page(self):
        response = self.client.get(reverse('finder:rate_limit'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "API Rate Limit Status")

    def test_autocomplete_api(self):
        response = self.client.get(reverse('finder:autocomplete') + '?q=torv')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn('suggestions', json_data)

    @patch('finder.views.GitHubAPIService.get_user_orgs')
    @patch('finder.views.GitHubAPIService.get_user_repos')
    @patch('finder.views.GitHubAPIService.get_user_profile')
    def test_export_json_endpoint(self, mock_profile, mock_repos, mock_orgs):
        mock_profile.return_value = {'login': 'octocat', 'name': 'The Octocat', 'followers': 100, 'public_repos': 1}
        mock_repos.return_value = [{'name': 'Hello-World', 'stargazers_count': 50, 'language': 'Python', 'size': 100}]
        mock_orgs.return_value = []

        response = self.client.get(reverse('finder:export_json', kwargs={'username': 'octocat'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn('octocat_profile.json', response['Content-Disposition'])
