from authlib.integrations.starlette_client import OAuth
import hashlib
import base64
import secrets
from app.configuration.settings import settings


# Генерируем случайный code_verifier
def generate_code_verifier() -> str:
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode('utf-8')
    return code_verifier


# Вычисляем хэш-значение code_challenge
def calculate_code_challenge(code_verifier: str) -> str:
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).rstrip(b'=').decode('utf-8')
    return code_challenge


def register_oauth() -> OAuth:
    oauth = OAuth()
    code_verifier = generate_code_verifier()
    code_challenge = calculate_code_challenge(code_verifier)
    # Конфигурация OAuth клиента для стороннего сервиса
    oauth.register(
        name='Client_cs2',
        client_id=settings.oauth_client_id,
        client_secret=settings.oauth_client_secret,
        authorize_url='https://accounts.faceit.com',
        access_token_url='https://api.faceit.com/auth/v1/oauth/token',
        authorize_params=None,
        authorize_prompt=False,
        authorize_redirect_path='https://bbf1-92-248-188-134.ngrok-free.app/api/v1/users/login/callback',
        client_kwargs={
            'code_challenge_method': 'S256',  # Метод хэширования PKCE
            'code_challenge': code_challenge  # PKCE хэш
        },
        jwks={"keys": ["https://api.faceit.com/auth/v1/oauth/certs"]},
    )

    return oauth
