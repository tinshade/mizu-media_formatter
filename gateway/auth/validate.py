import os, requests


def token(request):
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None, ("Missing / Invalid Credentials", 401)
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization": authorization},
    )

    if response.status_code == 200:
        return response.txt, None
    return None, (response.txt, response.status_code)
