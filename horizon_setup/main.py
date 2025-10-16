import typer
from .cli import executar_setup, executar_pos_corrida

app = typer.Typer(help="Horizon Setup — Assistente de Setup e Estratégia (GPRO)")

@app.command()
def setup(sessao: str = typer.Option("Corrida", help="Treino | Q1 | Q2 | Corrida")):
    raise SystemExit(executar_setup(sessao=sessao))

@app.command("pos-corrida")
def pos_corrida():
    raise SystemExit(executar_pos_corrida())

@app.command()
def gui():
    """
    Abre a interface gráfica (Tkinter).
    """
    from .gui.gui_view import HorizonSetupView
    from .gui.gui_controller import HorizonSetupController

    view = HorizonSetupView()
    HorizonSetupController(view)
    view.mainloop()

if __name__ == "__main__":
    app()
