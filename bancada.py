import time

# Estado interno da bancada
_estado = {
    "ligada": False,
    "inicio": None
}

def iniciar():
    """Inicializa o módulo da bancada."""
    print("Módulo bancada iniciado.")

def atuar(acao, objeto, contexto=None):
    """Ativa ou desativa o sistema de monitoramento da bancada."""
    global _estado

    if acao == "ligar" and objeto in ["sistema", "bancada"]:
        if not _estado["ligada"]:
            _estado["ligada"] = True
            _estado["inicio"] = time.time()
            print("[BANCADA] Sistema da bancada LIGADO.")
        else:
            print("[BANCADA] Sistema já estava ligado.")

    elif acao == "desligar" and objeto in ["sistema", "bancada"]:
        if _estado["ligada"]:
            duracao = time.time() - _estado["inicio"] if _estado["inicio"] else 0
            _estado["ligada"] = False
            _estado["inicio"] = None
            print(f"[BANCADA] Sistema da bancada DESLIGADO. Duração da sessão: {duracao:.1f}s")
        else:
            print("[BANCADA] Sistema já estava desligado.")
    else:
        print(f"[BANCADA] Comando não reconhecido: {acao} {objeto}")

def get_estado():
    return dict(_estado)
