import csv
from io import StringIO
from datetime import datetime

def format_date(iso_string):
    if not iso_string:
        return ''
    try:
        dt = datetime.strptime(iso_string.split('T')[0], '%Y-%m-%d')
        return dt.strftime('%b %d, %Y')
    except Exception:
        return iso_string

def format_size_kb(size_in_kb):
    if not size_in_kb:
        return '0 KB'
    if size_in_kb >= 1024:
        return f"{round(size_in_kb / 1024, 1)} MB"
    return f"{size_in_kb} KB"

def generate_repos_csv(username, repos):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Repository Name', 'Description', 'Language', 'Stars', 
        'Forks', 'Watchers', 'Open Issues', 'License', 
        'Created At', 'Updated At', 'Size (KB)', 'URL'
    ])

    for repo in repos:
        license_name = repo.get('license', {}).get('name') if repo.get('license') else 'None'
        writer.writerow([
            repo.get('name', ''),
            repo.get('description', '') or '',
            repo.get('language', '') or 'N/A',
            repo.get('stargazers_count', 0),
            repo.get('forks_count', 0),
            repo.get('watchers_count', 0),
            repo.get('open_issues_count', 0),
            license_name,
            format_date(repo.get('created_at', '')),
            format_date(repo.get('updated_at', '')),
            repo.get('size', 0),
            repo.get('html_url', '')
        ])

    return output.getvalue()
