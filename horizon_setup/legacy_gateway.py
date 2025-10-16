# horizon_setup/legacy_gateway.py
"""
Gateway (Adapter) para o código legado.
O Controller chama somente aqui; por trás a gente importa GAPP/calcs.
Assim, na Fase 2 dá pra trocar o legado por Services sem quebrar a GUI.
"""
import importlib
from typing import Optional


class LegacyGatewayError(Exception):
    pass


class LegacyGateway:
    def __init__(self) -> None:
        self._gapp = None
        self._calcs = None

    def _load(self) -> None:
        if self._gapp is None or self._calcs is None:
            try:
                self._gapp = importlib.import_module("horizon_setup.legacy.GAPP")
            except Exception:
                self._gapp = None
            try:
                self._calcs = importlib.import_module("horizon_setup.legacy.calcs")
            except Exception:
                self._calcs = None

        if self._gapp is None and self._calcs is None:
            raise LegacyGatewayError("Não foi possível carregar o código legado (GAPP/calcs).")

    def calcular_setup(self, usuario: str, senha: str, sessao: str = "Corrida") -> None:
        """
        Dispara o fluxo de cálculo. Preferimos GAPP.main(); se não houver, tenta calcs.main().
        """
        self._load()
        try:
            if self._gapp and hasattr(self._gapp, "main"):
                self._gapp.main(usuario, senha, sessao)
                return
            if self._calcs and hasattr(self._calcs, "main"):
                self._calcs.main(usuario, senha, sessao)
                return
        except Exception as e:
            raise LegacyGatewayError(f"Erro ao executar cálculo no legado: {e}") from e

        raise LegacyGatewayError("Nenhum ponto de entrada (main) encontrado no legado.")

    def pos_corrida(self) -> None:
        """
        Apenas valida (por enquanto) que os scrapers pós-corrida existem.
        Na Fase 2, consolidaremos em um adapter único.
        """
        self._load()
        try:
            importlib.import_module("horizon_setup.legacy.PostRaceBS")
            importlib.import_module("horizon_setup.legacy.PostRaceXPath")
        except Exception as e:
            raise LegacyGatewayError(f"Erro ao carregar scrapers pós-corrida: {e}") from e
