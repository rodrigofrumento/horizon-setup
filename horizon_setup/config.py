from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass(frozen=True)
class ConfiguracaoApp:
    gpro_usuario: str
    gpro_senha: str
    modo_headless: bool = True

def carregar_configuracao() -> ConfiguracaoApp:
    usuario = os.getenv("GPRO_USUARIO", "")
    senha = os.getenv("GPRO_SENHA", "")
    modo_headless = os.getenv("APP_MODO_HEADLESS", "true").lower() == "true"
    return ConfiguracaoApp(gpro_usuario=usuario, gpro_senha=senha, modo_headless=modo_headless)
