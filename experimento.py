import os
import time

_estado = {
    "monitorando": False,
    "inicio": None,
    "eventos": []
}

def iniciar():
    """Inicializa o módulo de monitoramento de experimento."""
    print("Módulo de monitoramento de experimento iniciado.")

def atuar(acao, objeto, contexto=None):
    """Inicia ou encerra o monitoramento do experimento."""
    global _estado

    if acao == "iniciar" and objeto in ["monitoramento", "experimento"]:
        if not _estado["monitorando"]:
            _estado["monitorando"] = True
            _estado["inicio"] = time.time()
            _estado["eventos"] = []
            _registrar_evento("Monitoramento iniciado")
            print("[EXPERIMENTO] Monitoramento do experimento INICIADO.")
        else:
            print("[EXPERIMENTO] Monitoramento já em andamento.")

    elif acao == "encerrar" and objeto in ["monitoramento", "experimento"]:
        if _estado["monitorando"]:
            duracao = time.time() - _estado["inicio"] if _estado["inicio"] else 0
            _registrar_evento(f"Monitoramento encerrado após {duracao:.1f}s")
            _estado["monitorando"] = False
            _estado["inicio"] = None
            print(f"[EXPERIMENTO] Monitoramento ENCERRADO. Duração: {duracao:.1f}s")
        else:
            print("[EXPERIMENTO] Monitoramento não estava ativo.")
    else:
        print(f"[EXPERIMENTO] Comando não reconhecido: {acao} {objeto}")

def _registrar_evento(mensagem):
    _estado["eventos"].append({
        "timestamp": time.strftime("%H:%M:%S"),
        "mensagem": mensagem
    })

def get_estado():
    return dict(_estado)
