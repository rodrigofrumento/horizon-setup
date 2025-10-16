# horizon_setup/gui/gui_view.py
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext


class HorizonSetupView(tk.Tk):
    """
    View (Tkinter) - NÃO contém regra de negócio.
    Expõe 'hooks' para o Controller atribuir callbacks.
    """
    def __init__(self) -> None:
        super().__init__()
        self.title("Horizon Setup")
        self.geometry("680x520")
        self.minsize(640, 480)

        # ---- Frame Credenciais ----
        cred_frame = ttk.LabelFrame(self, text="Credenciais do GPRO")
        cred_frame.pack(fill=tk.X, padx=12, pady=8)

        ttk.Label(cred_frame, text="Usuário:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.entry_usuario = ttk.Entry(cred_frame, width=30)
        self.entry_usuario.grid(row=0, column=1, sticky="w", padx=8, pady=6)

        ttk.Label(cred_frame, text="Senha:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.entry_senha = ttk.Entry(cred_frame, width=30, show="*")
        self.entry_senha.grid(row=1, column=1, sticky="w", padx=8, pady=6)

        ttk.Label(cred_frame, text="Sessão:").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        self.combo_sessao = ttk.Combobox(
            cred_frame,
            values=["Treino", "Q1", "Q2", "Corrida"],
            state="readonly",
            width=27
        )
        self.combo_sessao.set("Corrida")
        self.combo_sessao.grid(row=2, column=1, sticky="w", padx=8, pady=6)

        self.btn_salvar = ttk.Button(cred_frame, text="Salvar Config (.env)")
        self.btn_salvar.grid(row=0, column=2, rowspan=2, padx=10, pady=6)

        # ---- Frame Ações ----
        action_frame = ttk.LabelFrame(self, text="Ações")
        action_frame.pack(fill=tk.X, padx=12, pady=8)

        self.btn_setup = ttk.Button(action_frame, text="Calcular Setup")
        self.btn_setup.pack(side=tk.LEFT, padx=8, pady=8)

        self.btn_pos = ttk.Button(action_frame, text="Pós-corrida")
        self.btn_pos.pack(side=tk.LEFT, padx=8, pady=8)

        # ---- Log ----
        log_frame = ttk.LabelFrame(self, text="Logs")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        self.txt_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=18)
        self.txt_log.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # ---- Status ----
        self.status_var = tk.StringVar(value="Pronto.")
        status = ttk.Label(self, textvariable=self.status_var, anchor="w")
        status.pack(fill=tk.X, side=tk.BOTTOM, padx=12, pady=(0,8))

        # Grid tweaks
        cred_frame.grid_columnconfigure(1, weight=1)

    # Helpers p/ Controller
    def get_usuario(self) -> str:
        return self.entry_usuario.get().strip()

    def set_usuario(self, v: str) -> None:
        self.entry_usuario.delete(0, tk.END)
        self.entry_usuario.insert(0, v)

    def get_senha(self) -> str:
        return self.entry_senha.get()

    def set_senha(self, v: str) -> None:
        self.entry_senha.delete(0, tk.END)
        self.entry_senha.insert(0, v)

    def get_sessao(self) -> str:
        return self.combo_sessao.get()

    def append_log(self, line: str) -> None:
        self.txt_log.insert(tk.END, line + "\n")
        self.txt_log.see(tk.END)

    def set_status(self, msg: str) -> None:
        self.status_var.set(msg)
