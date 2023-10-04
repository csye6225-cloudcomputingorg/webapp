import requests

def test_get_case():
    url = 'http://127.0.0.1:5000/healthz'
    response_get = requests.get(url)
    response_post = requests.post(url)
    response_not_found = requests.get(url+'/')
    assert response_get.status_code == 200
    assert response_post.status_code == 405
    assert response_not_found.status_code == 404