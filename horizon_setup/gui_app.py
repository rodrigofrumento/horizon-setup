# horizon_setup/gui_app.py
import sys
import os

# Silencia avisos depreciação no macOS (opcional)
os.environ.setdefault("TK_SILENCE_DEPRECATION", "1")

def main() -> None:
    # IMPORTES AQUI, dentro da main, garantem que nada inicialize threads antes do Tk
    from horizon_setup.gui.gui_view import HorizonSetupView
    from horizon_setup.gui.gui_controller import HorizonSetupController

    view = HorizonSetupView()            # Tk nasce aqui, na *main thread*
    HorizonSetupController(view)         # Controller só agenda threads depois, via botões
    view.mainloop()

if __name__ == "__main__":
    # Rodar sempre este módulo direto garante *main thread* para Tk no macOS
    main()
