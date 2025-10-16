import importlib
from rich import print
from rich.prompt import Prompt
from horizon_setup.config import carregar_configuracao

def _carregar_legado():
    try:
        gapp = importlib.import_module("horizon_setup.legacy.GAPP")
    except Exception as e:
        print(f"[red]Erro ao carregar GAPP.py:[/red] {e}")
        gapp = None

    try:
        calcs = importlib.import_module("horizon_setup.legacy.calcs")
    except Exception as e:
        print(f"[red]Erro ao carregar calcs.py:[/red] {e}")
        calcs = None

    return gapp, calcs

def executar_setup(sessao: str = "Corrida") -> int:
    """
    Executa o cálculo de setup e estratégia (modo legado).
    """
    cfg = carregar_configuracao()
    gapp, calcs = _carregar_legado()

    usuario = cfg.gpro_usuario or Prompt.ask("Usuário do GPRO")
    senha = cfg.gpro_senha or Prompt.ask("Senha do GPRO", password=True)

    try:
        if gapp and hasattr(gapp, "main"):
            gapp.main(usuario, senha, sessao)
        elif calcs and hasattr(calcs, "main"):
            calcs.main(usuario, senha, sessao)
        else:
            print("[yellow]Nenhum ponto de entrada (main) encontrado no legado.[/yellow]")
            return 1

        print("[green]Cálculo finalizado com sucesso![/green]")
        return 0
    except Exception as e:
        print(f"[red]Erro durante o cálculo:[/red] {e}")
        return 2

def executar_pos_corrida() -> int:
    """
    Carrega os scrapers de pós-corrida (serão unificados na Fase 2).
    """
    try:
        importlib.import_module("horizon_setup.legacy.PostRaceBS")
        importlib.import_module("horizon_setup.legacy.PostRaceXPath")
        print("[green]Scrapers de pós-corrida carregados.[/green]")
        return 0
    except Exception as e:
        print(f"[red]Erro ao importar scrapers de pós-corrida:[/red] {e}")
        return 1
