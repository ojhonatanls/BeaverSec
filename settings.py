from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Configurações sensíveis vêm de variáveis de ambiente
    shodan_api_key: Optional[str] = None
    nvd_api_key: Optional[str] = None
    securitytrails_api_key: Optional[str] = None
    
    # Configurações do arquivo
    rate_limit: int = 200
    http_timeout: int = 30
    proxy_url: Optional[str] = None
    
    class Config:
        env_prefix = "BEAVERSEC_"
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
