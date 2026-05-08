import os
import time
import json

_estado = {
    "registrando": False,
    "inicio": None,
    "data_inicio": None,
    "relatorio": None
}

PASTA_RELATORIOS = "relatorios"

def iniciar():
    """Inicializa o módulo de registro de atividade."""
    os.makedirs(PASTA_RELATORIOS, exist_ok=True)
    print("Módulo de registro de atividade iniciado.")

def atuar(acao, objeto, contexto=None):
    """Inicia ou encerra o registro da atividade."""
    global _estado

    if acao == "iniciar" and objeto in ["registro", "atividade"]:
        if not _estado["registrando"]:
            _estado["registrando"] = True
            _estado["inicio"] = time.time()
            _estado["data_inicio"] = time.strftime("%Y-%m-%d %H:%M:%S")
            _estado["relatorio"] = {
                "data": _estado["data_inicio"],
                "duracao_s": None,
                "medicoes": [],
                "anotacoes": [],
                "status": "em andamento"
            }
            print(f"[REGISTRO] Registro da atividade INICIADO em {_estado['data_inicio']}.")
        else:
            print("[REGISTRO] Já existe um registro em andamento.")

    elif acao == "encerrar" and objeto in ["registro", "atividade"]:
        if _estado["registrando"]:
            duracao = time.time() - _estado["inicio"] if _estado["inicio"] else 0
            _estado["relatorio"]["duracao_s"] = round(duracao, 1)
            _estado["relatorio"]["status"] = "concluído"

            # Salva relatório em arquivo JSON
            nome_arquivo = f"relatorio_{time.strftime('%Y%m%d_%H%M%S')}.json"
            caminho = os.path.join(PASTA_RELATORIOS, nome_arquivo)
            try:
                with open(caminho, "w", encoding="utf-8") as f:
                    json.dump(_estado["relatorio"], f, indent=4, ensure_ascii=False)
                print(f"[REGISTRO] Relatório salvo em: {caminho}")
            except Exception as e:
                print(f"[REGISTRO] Erro ao salvar relatório: {e}")

            _estado["registrando"] = False
            _estado["inicio"] = None
            print(f"[REGISTRO] Registro ENCERRADO. Duração: {duracao:.1f}s")
        else:
            print("[REGISTRO] Nenhum registro em andamento.")
    else:
        print(f"[REGISTRO] Comando não reconhecido: {acao} {objeto}")

def adicionar_medicao(medicao):
    """Adiciona uma medição ao relatório corrente."""
    if _estado["registrando"] and _estado["relatorio"]:
        _estado["relatorio"]["medicoes"].append({
            "timestamp": time.strftime("%H:%M:%S"),
            "valor": medicao
        })

def adicionar_anotacao(anotacao):
    """Adiciona uma anotação ao relatório corrente."""
    if _estado["registrando"] and _estado["relatorio"]:
        _estado["relatorio"]["anotacoes"].append({
            "timestamp": time.strftime("%H:%M:%S"),
            "texto": anotacao
        })

def get_estado():
    return {
        "registrando": _estado["registrando"],
        "data_inicio": _estado["data_inicio"],
        "relatorio": _estado["relatorio"]
    }
