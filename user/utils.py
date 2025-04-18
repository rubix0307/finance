import requests


def fetch_image_bytes(url: str) -> tuple[bytes, str]:
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.content

    if data[:2] == b'\xff\xd8':
        ext = 'jpg'
        return data, ext

    url, *params = url.rsplit('?', maxsplit=1)
    ext = url.split('.')[-1]
    return data, ext