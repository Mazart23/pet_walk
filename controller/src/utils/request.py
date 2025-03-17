import requests

from .apps import Service


def send_request(method: str, to: Service | str, endpoint = '/', json_data={}, files={}, json_input=True, json_output=True, headers={}, timeout=30) -> requests.Response:
    if isinstance(to, Service):
        url = f'{to.http}://{to.ip}:{to.port}{endpoint}'
    else:
        url = f'{to}{endpoint}'

    if files:
        response = requests.post(url, files=files, timeout=timeout, headers=headers)
    else:
        if not headers:
            headers = {}
            if json_input:
                headers['Content-Type'] = 'application/json'
            if json_output:
                headers['Accept'] = 'application/json'
    
        match method:
            case 'GET':
                if headers.keys().get('Content-Type') == 'application/json':
                    headers.pop('Content-Type')
                response = requests.get(url, params=json_data, timeout=timeout, headers=headers)
            case 'POST':
                response = requests.post(url, json=json_data, timeout=timeout, headers=headers)
            case 'PUT':
                response = requests.put(url, params=json_data, timeout=timeout, headers=headers)
    
    return response
