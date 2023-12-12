import celery
from pydantic import Field
from pydantic_settings import BaseSettings
from authlib.integrations.starlette_client import OAuth


class Settings(BaseSettings):
    db_name: str = Field(..., env='DB_NAME')
    db_host: str = Field(..., env='DB_HOST')
    db_username: str = Field(..., env='DB_USERNAME')
    db_password: str = Field(..., env='DB_PASSWORD')
    db_port: str = Field(..., env='DB_PORT')
    celery_backend_url: str = Field(..., env='CELERY_BACKEND_URL')
    celery_broker_url: str = Field(..., env='CELERY_BROKER_URL')
    celery_result_backend: str = Field(..., env='CELERY_RESULT_BACKEND')
    compose_project_name: str = Field(..., env='COMPOSE_PROJECT_NAME')
    redis_url: str = Field(..., env='REDIS_URL')

    is_prod: str = Field(..., env='IS_PROD')
    oauth_client_id: str = Field(..., env='OAUTH_CLIENT_ID')
    oauth_client_secret: str = Field(..., env='OAUTH_CLIENT_SECRET')
    oauth_authorize_redirect_path: str = Field(..., env='OAUTH_AUTHORIZE_REDIRECT_PATH')
    faceit_api_key: str = Field(..., env='FACEIT_API_KEY')
    leaderboard_id: str = Field(..., env='LEADERBOARD_ID')
    game_id: str = 'cs2'
    jwt_secret_key: str = Field(..., env='JWT_SECRET_KEY')
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 1000
    bscscan_base_url: str = Field(..., env='BSCSCAN_BASE_URL')
    corporate_contract_admin_address: str = Field(...,env="CORPORATE_CONTRACT_ADMIN_ADDRESS")
    corporate_contract_admin_private_key: str = Field(...,env='CORPORATE_CONTRACT_ADMIN_PRIVATE_KEY')
    corporate_payouts_contract_address: str = Field(...,env='CORPORATE_PAYOUTS_CONTRACT_ADDRESS')
    bscscan_api_key :str = Field(...,env='BSCSCAN_API_KEY')
    bsc_node_url: str = Field(..., env='BSC_NODE_URL')

    class Config:
        env_file = 'docker/env_files/.env'


settings = Settings()
