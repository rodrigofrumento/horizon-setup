# horizon_setup/gui/gui_controller.py
import os
import threading
import queue
from typing import Callable
from horizon_setup.config import carregar_configuracao
from horizon_setup.legacy_gateway import LegacyGateway, LegacyGatewayError


class HorizonSetupController:
    """
    Controller coordena a View e chama o Gateway (legado).
    Regras:
      - Nada de chamado bloqueante na thread da GUI.
      - Uso de Queue para log seguro entre threads.
    """
    def __init__(self, view, log_poller_ms: int = 120) -> None:
        self.view = view
        self.gateway = LegacyGateway()
        self.log_queue: "queue.Queue[str]" = queue.Queue()
        self._bind_buttons()
        self._prefill_from_env()
        self._start_log_poller(log_poller_ms)

    # --------------------------------------------------------------------- UI
    def _bind_buttons(self) -> None:
        self.view.btn_setup.configure(command=self._on_setup_clicked)
        self.view.btn_pos.configure(command=self._on_pos_clicked)
        self.view.btn_salvar.configure(command=self._on_salvar_clicked)

    def _prefill_from_env(self) -> None:
        cfg = carregar_configuracao()
        if cfg.gpro_usuario:
            self.view.set_usuario(cfg.gpro_usuario)
        if cfg.gpro_senha:
            self.view.set_senha(cfg.gpro_senha)

    def _start_log_poller(self, interval_ms: int) -> None:
        def poll():
            try:
                while True:
                    line = self.log_queue.get_nowait()
                    self.view.append_log(line)
            except queue.Empty:
                pass
            # agenda próximo polling
            self.view.after(interval_ms, poll)

        self.view.after(interval_ms, poll)

    # -------------------------------------------------------------- Commands
    def _on_salvar_clicked(self) -> None:
        usuario = self.view.get_usuario()
        senha = self.view.get_senha()
        lines = [
            f"GPRO_USUARIO={usuario}",
            f"GPRO_SENHA={senha}",
            "APP_MODO_HEADLESS=true",
        ]
        with open(".env", "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        self.view.set_status("Configurações salvas em .env")
        self.log_queue.put("Configurações salvas (.env).")

    def _on_setup_clicked(self) -> None:
        usuario = self.view.get_usuario()
        senha = self.view.get_senha()
        sessao = self.view.get_sessao()  # Treino | Q1 | Q2 | Corrida
        self._run_async(self._run_setup_task, usuario, senha, sessao)

    def _on_pos_clicked(self) -> None:
        self._run_async(self._run_pos_task)

    # ----------------------------------------------------------- Worker Tasks
    def _run_setup_task(self, usuario: str, senha: str, sessao: str) -> None:
        self.view.set_status("Executando cálculo...")
        self.log_queue.put(f"Iniciando cálculo (sessão: {sessao})...")
        try:
            self.gateway.calcular_setup(usuario, senha, sessao)
            self.log_queue.put("Cálculo finalizado com sucesso.")
            self.view.set_status("Pronto.")
        except LegacyGatewayError as e:
            self.log_queue.put(f"[ERRO] {e}")
            self.view.set_status("Erro ao calcular. Veja os logs.")
        except Exception as e:
            self.log_queue.put(f"[ERRO inesperado] {e}")
            self.view.set_status("Erro inesperado. Veja os logs.")

    def _run_pos_task(self) -> None:
        self.view.set_status("Carregando scrapers de pós-corrida...")
        try:
            self.gateway.pos_corrida()
            self.log_queue.put("Scrapers de pós-corrida carregados com sucesso.")
            self.view.set_status("Pronto.")
        except LegacyGatewayError as e:
            self.log_queue.put(f"[ERRO] {e}")
            self.view.set_status("Erro no pós-corrida. Veja os logs.")
        except Exception as e:
            self.log_queue.put(f"[ERRO inesperado] {e}")
            self.view.set_status("Erro inesperado. Veja os logs.")

    # --------------------------------------------------------------- Helpers
    def _run_async(self, fn: Callable, *args) -> None:
        t = threading.Thread(target=fn, args=args, daemon=True)
        t.start()
