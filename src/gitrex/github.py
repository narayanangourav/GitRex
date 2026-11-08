"""GitHub public contribution collector (GitHub GraphQL + REST).

The GraphQL contribution calendar contains contribution activity, including
commits, pull requests, issues, and reviews. Do not label it raw commit count.
No private repository names or files are queried or written to output.
"""
from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

API = 'https://api.github.com'
GRAPHQL = 'https://api.github.com/graphql'
UA = 'GitRex/1.0 (+https://github.com)'
QUERY = '''
query($login:String!, $start:DateTime!, $end:DateTime!) {
 user(login:$login) {
   login
   createdAt
   contributionsCollection(from:$start, to:$end) {
     totalCommitContributions
     contributionCalendar { weeks { contributionDays { date contributionCount } } }
   }
 }
}
'''


class GithubError(RuntimeError):
    pass


def _json_request(url: str, token: str, payload: dict | None = None):
    headers = {'User-Agent': UA, 'Accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2022-11-28', 'Authorization': 'Bearer '+token}
    body = json.dumps(payload).encode('utf-8') if payload is not None else None
    if body:
        headers['Content-Type'] = 'application/json'
    req = Request(url, data=body, headers=headers)
    try:
        with urlopen(req, timeout=25) as response:
            return json.loads(response.read())
    except HTTPError as e:
        raise GithubError(f'GitHub returned HTTP {e.code}. Verify username, token and rate limit.') from e
    except (URLError, TimeoutError) as e:
        raise GithubError(f'GitHub request failed: {e}') from e


def _graphql(token, login, start, end):
    result = _json_request(GRAPHQL, token, {'query': QUERY, 'variables': {
        'login': login,
        'start': start.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'end': end.strftime('%Y-%m-%dT%H:%M:%SZ'),
    }})
    if result.get('errors'):
        raise GithubError('GitHub GraphQL error: '+str(result['errors'][0].get('message','unknown')))
    user = (result.get('data') or {}).get('user')
    if not user:
        raise GithubError(f'GitHub user not found: {login}')
    return user


def _languages(login, token, max_pages=5):
    """Approximate language prominence from public owned repositories.
    The repo size is an approximation, not exact per-language byte totals.
    """
    weights = {}
    colors = {'Python':'#3572a5','TypeScript':'#3178c6','JavaScript':'#f1e05a',
              'Java':'#b07219','Rust':'#dea584','Go':'#00add8','C++':'#f34b7d'}
    for page in range(1, max_pages+1):
        url = f'{API}/users/{quote(login, safe="")}/repos?type=owner&per_page=100&page={page}'
        repos = _json_request(url, token)
        if not isinstance(repos, list):
            raise GithubError('Malformed response to repositories query')
        for repo in repos:
            if repo.get('private') or repo.get('fork') or not repo.get('language'):
                continue
            language = repo['language']
            weights[language] = weights.get(language,0) + max(1,int(repo.get('size',1)))
        if len(repos) < 100:
            break
    return [{'name': name, 'weight': weight, 'color': colors.get(name, '#c8a67a')}
            for name, weight in sorted(weights.items(), key=lambda x:(-x[1],x[0]))[:8]]


def collect(login: str, token: str | None = None, today: date | None = None) -> dict:
    """Collect all available complete days; failing a query raises, never partial saves."""
    token = token or os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not token:
        raise GithubError('A GitHub token is required. Set GH_TOKEN, GITHUB_TOKEN, or use gh auth login.')
    if not login or not login.replace('-', '').isalnum():
        raise ValueError('Invalid GitHub username')
    now = today or datetime.now(timezone.utc).date()
    as_of = now - timedelta(days=1)
    # First request identifies account age. GitHub allows at most one year per window.
    first_start = datetime.combine(as_of-timedelta(days=364), datetime.min.time(), tzinfo=timezone.utc)
    first_end = datetime.combine(as_of, datetime.max.time(),tzinfo=timezone.utc).replace(microsecond=0)
    first = _graphql(token, login, first_start, first_end)
    created = date.fromisoformat(first['createdAt'][:10])
    if created > as_of:
        raise GithubError('Account has no completed contribution days yet')
    daily: dict[str,int] = {}
    total_commits = 0
    # Fixed 365-day segments: consistent boundaries, no leap-year double counting.
    cursor = created
    while cursor <= as_of:
        stop = min(cursor + timedelta(days=364), as_of)
        st = datetime.combine(cursor, datetime.min.time(), tzinfo=timezone.utc)
        en = datetime.combine(stop, datetime.max.time(), tzinfo=timezone.utc).replace(microsecond=0)
        collection = _graphql(token, login, st, en)['contributionsCollection']
        total_commits += int(collection.get('totalCommitContributions') or 0)
        for week in collection['contributionCalendar']['weeks']:
            for entry in week['contributionDays']:
                day = entry['date']
                if cursor.isoformat() <= day <= stop.isoformat():
                    if day in daily:
                        raise GithubError(f'Duplicate contribution day: {day}')
                    daily[day] = int(entry['contributionCount'])
        cursor = stop + timedelta(days=1)
    return {'schema_version':1, 'login':first['login'], 'as_of':as_of.isoformat(),
            'daily':daily, 'commits':total_commits,
            'languages':_languages(login,token),
            'counting':'Publicly visible GitHub contribution calendar (not raw commits).',
            'source':'GitHub GraphQL contributionsCollection + REST public owner repositories'}
