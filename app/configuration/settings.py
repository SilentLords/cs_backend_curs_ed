import celery
from pydantic import Field
from pydantic_settings import BaseSettings
from authlib.integrations.starlette_client import OAuth


class Settings(BaseSettings):
    db_name: str = Field(..., env='DB_NAME')
    db_username: str = Field(..., env='DB_USERNAME')
    db_password: str = Field(..., env='DB_PASSWORD')
    db_port: str = Field(..., env='DB_PORT')
    celery_backend_url: str = Field(..., env='CELERY_BACKEND_URL')
    is_prod: str = Field(..., env='IS_PROD')
    oauth_client_id: str = Field(..., env='OAUTH_CLIENT_ID')
    oauth_client_secret: str = Field(..., env='OAUTH_CLIENT_SECRET')
    oauth_authorize_redirect_path: str = Field(..., env='OAUTH_AUTHORIZE_REDIRECT_PATH')
    faceit_api_key: str = Field(..., env='FACEIT_API_KEY')
    leaderboard_id: str = Field(..., env='LEADERBORD_ID')
    game_id: str =  'cs2'
    jwt_secret_key: str = Field(..., env='JWT_SECRET_KEY')
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 1000


settings = Settings()
