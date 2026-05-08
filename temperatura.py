import os
import time
import random
import threading

LIMITE_ALERTA_C = 45.0  # temperatura de alerta em Celsius

_estado = {
    "monitorando": False,
    "inicio": None,
    "temperatura_atual_c": 0.0,
    "alertas": [],
    "historico": []
}

_thread_monitor = None
_parar_thread = threading.Event()

def iniciar():
    """Inicializa o módulo de monitoramento de temperatura."""
    print("Módulo de monitoramento de temperatura iniciado.")

def _simular_temperatura():
    """Simula leitura contínua de temperatura dos componentes."""
    temp_base = random.uniform(24.0, 30.0)
    while not _parar_thread.is_set():
        if _estado["monitorando"]:
            variacao = random.uniform(-1.5, 2.0)
            temp_base = max(20.0, min(60.0, temp_base + variacao))
            temp = round(temp_base, 1)
            _estado["temperatura_atual_c"] = temp
            registro = {
                "timestamp": time.strftime("%H:%M:%S"),
                "temperatura_c": temp
            }
            _estado["historico"].append(registro)
            if len(_estado["historico"]) > 100:
                _estado["historico"] = _estado["historico"][-100:]

            if temp >= LIMITE_ALERTA_C:
                alerta = {
                    "timestamp": time.strftime("%H:%M:%S"),
                    "mensagem": f"ALERTA: Temperatura elevada {temp}°C (limite: {LIMITE_ALERTA_C}°C)"
                }
                _estado["alertas"].append(alerta)
                print(f"[TEMPERATURA] ⚠ {alerta['mensagem']}")
        time.sleep(2)

def atuar(acao, objeto, contexto=None):
    """Inicia ou encerra o monitoramento de temperatura."""
    global _estado, _thread_monitor, _parar_thread

    if acao == "iniciar" and objeto in ["monitoramento", "temperatura"]:
        if not _estado["monitorando"]:
            _estado["monitorando"] = True
            _estado["inicio"] = time.time()
            _estado["alertas"] = []
            _estado["historico"] = []
            _parar_thread.clear()
            _thread_monitor = threading.Thread(target=_simular_temperatura, daemon=True)
            _thread_monitor.start()
            print("[TEMPERATURA] Monitoramento de temperatura INICIADO.")
        else:
            print("[TEMPERATURA] Monitoramento de temperatura já em andamento.")

    elif acao == "encerrar" and objeto in ["monitoramento", "temperatura"]:
        if _estado["monitorando"]:
            _estado["monitorando"] = False
            _parar_thread.set()
            duracao = time.time() - _estado["inicio"] if _estado["inicio"] else 0
            total_alertas = len(_estado["alertas"])
            print(f"[TEMPERATURA] Monitoramento ENCERRADO. Duração: {duracao:.1f}s | Alertas gerados: {total_alertas}")
            _estado["inicio"] = None
        else:
            print("[TEMPERATURA] Monitoramento de temperatura não estava ativo.")
    else:
        print(f"[TEMPERATURA] Comando não reconhecido: {acao} {objeto}")

def get_estado():
    return {
        "monitorando": _estado["monitorando"],
        "temperatura_atual_c": _estado["temperatura_atual_c"],
        "alertas": _estado["alertas"][-5:],
        "historico": _estado["historico"][-10:]
    }
