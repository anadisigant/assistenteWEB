import os
import time
import random
import threading

_estado = {
    "monitorando": False,
    "inicio": None,
    "consumo_total_wh": 0.0,
    "potencia_atual_w": 0.0,
    "historico": []
}

_thread_monitor = None
_parar_thread = threading.Event()

def iniciar():
    """Inicializa o módulo de monitoramento de energia."""
    print("Módulo de monitoramento de energia iniciado.")

def _simular_consumo():
    """Simula leitura contínua de consumo de energia."""
    while not _parar_thread.is_set():
        if _estado["monitorando"]:
            potencia = round(random.uniform(15.0, 45.0), 2)  # Watts
            _estado["potencia_atual_w"] = potencia
            # Acumula energia (kWh = W * h / 1000), intervalo de 1s
            _estado["consumo_total_wh"] += potencia / 3600.0
            _estado["historico"].append({
                "timestamp": time.strftime("%H:%M:%S"),
                "potencia_w": potencia,
                "consumo_total_wh": round(_estado["consumo_total_wh"], 4)
            })
            if len(_estado["historico"]) > 100:
                _estado["historico"] = _estado["historico"][-100:]
        time.sleep(1)

def atuar(acao, objeto, contexto=None):
    """Inicia ou encerra o monitoramento de energia."""
    global _estado, _thread_monitor, _parar_thread

    if acao == "iniciar" and objeto in ["monitoramento", "energia"]:
        if not _estado["monitorando"]:
            _estado["monitorando"] = True
            _estado["inicio"] = time.time()
            _estado["consumo_total_wh"] = 0.0
            _estado["historico"] = []
            _parar_thread.clear()
            _thread_monitor = threading.Thread(target=_simular_consumo, daemon=True)
            _thread_monitor.start()
            print("[ENERGIA] Monitoramento de energia INICIADO.")
        else:
            print("[ENERGIA] Monitoramento de energia já em andamento.")

    elif acao == "encerrar" and objeto in ["monitoramento", "energia"]:
        if _estado["monitorando"]:
            _estado["monitorando"] = False
            _parar_thread.set()
            duracao = time.time() - _estado["inicio"] if _estado["inicio"] else 0
            consumo = round(_estado["consumo_total_wh"] * 1000, 4)  # em mWh para precisão
            print(f"[ENERGIA] Monitoramento ENCERRADO. Duração: {duracao:.1f}s | Consumo estimado: {_estado['consumo_total_wh']:.4f} Wh")
            _estado["inicio"] = None
        else:
            print("[ENERGIA] Monitoramento de energia não estava ativo.")
    else:
        print(f"[ENERGIA] Comando não reconhecido: {acao} {objeto}")

def get_estado():
    return {
        "monitorando": _estado["monitorando"],
        "potencia_atual_w": _estado["potencia_atual_w"],
        "consumo_total_wh": round(_estado["consumo_total_wh"], 4),
        "historico": _estado["historico"][-10:]
    }