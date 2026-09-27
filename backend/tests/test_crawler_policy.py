from fastapi.testclient import TestClient

from app.main import app


def test_robots_policy_blocks_cooperative_crawlers():
    with TestClient(app) as client:
        response = client.get('/robots.txt')

    assert response.status_code == 200
    assert response.headers['content-type'].startswith('text/plain')
    assert response.text == 'User-agent: *\nDisallow: /\n'
    assert response.headers['x-robots-tag'] == 'noindex, nofollow, noarchive, nosnippet'


def test_api_responses_are_marked_noindex():
    with TestClient(app) as client:
        response = client.get('/health')

    assert response.headers['x-robots-tag'] == 'noindex, nofollow, noarchive, nosnippet'
