from flask import Flask, Response, request, send_from_directory
from nltk import word_tokenize, corpus
from inicializador_modelo import *
from threading import Thread
from transcritor import *
import sounddevice
import soundfile
import secrets
import json
import os

import bancada
import experimento
import energia
import temperatura
import registro

LINGUAGEM = "portuguese"
CANAIS = 1
AMOSTRAS = 1024
TEMPO_GRAVACAO = 5
CAMINHO_AUDIO_FALAS = "temp"
CONFIGURACOES = "config.json"

MODO_LINHA_DE_COMANDO = 1
MODO_WEB = 2
MODO_DE_FUNCIONAMENTO = MODO_WEB
# MODO_DE_FUNCIONAMENTO = MODO_LINHA_DE_COMANDO

# Mapeamento de palavras-chave para ações e objetos normalizados
MAPA_COMANDOS = [
    # bancada
    {
        "palavras": ["ligar", "sistema", "bancada"],
        "acao": "ligar",
        "objeto": "sistema"
    },
    {
        "palavras": ["desligar", "sistema", "bancada"],
        "acao": "desligar",
        "objeto": "sistema"
    },
    # experimento
    {
        "palavras": ["iniciar", "monitoramento", "experimento"],
        "acao": "iniciar",
        "objeto": "experimento"
    },
    {
        "palavras": ["encerrar", "monitoramento", "experimento"],
        "acao": "encerrar",
        "objeto": "experimento"
    },
    # energia
    {
        "palavras": ["iniciar", "monitoramento", "energia"],
        "acao": "iniciar",
        "objeto": "energia"
    },
    {
        "palavras": ["encerrar", "monitoramento", "energia"],
        "acao": "encerrar",
        "objeto": "energia"
    },
    # temperatura
    {
        "palavras": ["iniciar", "monitoramento", "temperatura"],
        "acao": "iniciar",
        "objeto": "temperatura"
    },
    {
        "palavras": ["encerrar", "monitoramento", "temperatura"],
        "acao": "encerrar",
        "objeto": "temperatura"
    },
    # registro
    {
        "palavras": ["iniciar", "registro", "atividade"],
        "acao": "iniciar",
        "objeto": "atividade"
    },
    {
        "palavras": ["encerrar", "registro", "atividade"],
        "acao": "encerrar",
        "objeto": "atividade"
    },
]

ATUADORES = [
    {
        "nome": "bancada",
        "iniciar": bancada.iniciar,
        "atuar": bancada.atuar
    },
    {
        "nome": "experimento",
        "iniciar": experimento.iniciar,
        "atuar": experimento.atuar
    },
    {
        "nome": "energia",
        "iniciar": energia.iniciar,
        "atuar": energia.atuar
    },
    {
        "nome": "temperatura",
        "iniciar": temperatura.iniciar,
        "atuar": temperatura.atuar
    },
    {
        "nome": "registro",
        "iniciar": registro.iniciar,
        "atuar": registro.atuar
    }
]

def iniciar(dispositivo):
    iniciado, processador, modelo = iniciar_modelo(MODELOS[0], dispositivo)

    palavras_de_parada = set(corpus.stopwords.words(LINGUAGEM))

    with open(CONFIGURACOES, "r", encoding="utf-8") as arquivo_configuracoes:
        configuracoes = json.load(arquivo_configuracoes)
        acoes = configuracoes["acoes"]
        arquivo_configuracoes.close()

    for atuador in ATUADORES:
        atuador["iniciar"]()

    return iniciado, processador, modelo, palavras_de_parada, acoes

def capturar_fala():
    print("fale alguma coisa...")

    fala = sounddevice.rec(int(TEMPO_GRAVACAO * TAXA_AMOSTRAGEM), samplerate=TAXA_AMOSTRAGEM, channels=CANAIS)
    sounddevice.wait()

    print("fala capturada")

    return fala

def gravar_fala(fala):
    gravado, arquivo = False, f"{CAMINHO_AUDIO_FALAS}/{secrets.token_hex(32).lower()}.wav"

    try:
        soundfile.write(arquivo, fala, TAXA_AMOSTRAGEM)
        gravado = True
    except Exception as e:
        print(f"erro gravando arquivo de fala: {str(e)}")

    return gravado, arquivo

def processar_transcricao(transcricao, palavras_de_parada):
    """Extrai tokens relevantes da transcrição, removendo stopwords."""
    tokens = word_tokenize(transcricao.lower())
    return [t for t in tokens if t not in palavras_de_parada and t.isalpha()]

def validar_comando(tokens):
    """
    Usa correspondência por palavras-chave para identificar o comando.
    Retorna (valido, acao, objeto).
    """
    tokens_set = set(tokens)
    melhor_match = None
    melhor_score = 0

    for entrada in MAPA_COMANDOS:
        score = sum(1 for palavra in entrada["palavras"] if palavra in tokens_set)
        if score > melhor_score:
            melhor_score = score
            melhor_match = entrada

    # Exige pelo menos 2 palavras-chave para considerar válido
    if melhor_score >= 2 and melhor_match:
        return True, melhor_match["acao"], melhor_match["objeto"]

    return False, None, None

def atuar(acao, objeto):
    for atuador in ATUADORES:
        print(f"enviando comando para {atuador['nome']}")
        atuacao = Thread(target=atuador["atuar"], args=[acao, objeto])
        atuacao.start()

def get_status():
    """Retorna o estado atual de todos os subsistemas."""
    return {
        "bancada": bancada.get_estado(),
        "experimento": experimento.get_estado(),
        "energia": energia.get_estado(),
        "temperatura": temperatura.get_estado(),
        "registro": registro.get_estado()
    }

############################## linha de comando

def ativar_linha_de_comando(dispositivo, modelo, processador, palavras_de_parada, acoes):
    while True:
        fala = capturar_fala()
        gravado, arquivo = gravar_fala(fala)
        if gravado:
            fala = carregar_fala(arquivo)
            transcricao = transcrever_fala(dispositivo, fala, modelo, processador)

            if os.path.exists(arquivo):
                os.remove(arquivo)

            tokens = processar_transcricao(transcricao, palavras_de_parada)
            print(f"tokens: {tokens}")

            valido, acao, objeto = validar_comando(tokens)
            if valido:
                print(f"executando {acao} sobre {objeto}")
                atuar(acao, objeto)
            else:
                print("comando inválido")
        else:
            print("ocorreu um erro gravando a fala")

############################## servico web

servico = Flask("assistente", static_folder="public")

@servico.get("/")
def acessar_pagina():
    return send_from_directory("public", "index.html")

@servico.get("/<path:caminho>")
def acessar_pasta_estatica(caminho):
    return send_from_directory("public", caminho)

@servico.get("/status")
def obter_status():
    """Endpoint que retorna o estado atual de todos os subsistemas."""
    try:
        return Response(json.dumps(get_status(), ensure_ascii=False), status=200, content_type="application/json")
    except Exception as e:
        print(f"erro ao obter status: {str(e)}")
        return Response(status=500)

@servico.post("/reconhecer_comando")
def reconhecer_comando():
    if "fala" not in request.files:
        return Response(status=400)

    fala = request.files["fala"]
    caminho_arquivo = f"{CAMINHO_AUDIO_FALAS}/{secrets.token_hex(32).lower()}.wav"
    fala.save(caminho_arquivo)

    try:
        transcricao = transcrever_fala(
            servico.config["dispositivo"],
            carregar_fala(caminho_arquivo),
            servico.config["modelo"],
            servico.config["processador"]
        )

        tokens = processar_transcricao(transcricao, servico.config["palavras_de_parada"])
        valido, acao, objeto = validar_comando(tokens)

        if valido:
            print(f"comando válido: {acao} {objeto} — executando atuação")
            atuar(acao, objeto)

            # Determina mensagem de feedback
            msgs = {
                ("ligar", "sistema"): "✅ Sistema da bancada LIGADO",
                ("desligar", "sistema"): "🔴 Sistema da bancada DESLIGADO",
                ("iniciar", "experimento"): "🔬 Monitoramento do experimento INICIADO",
                ("encerrar", "experimento"): "⏹ Monitoramento do experimento ENCERRADO",
                ("iniciar", "energia"): "⚡ Monitoramento de energia INICIADO",
                ("encerrar", "energia"): "⏹ Monitoramento de energia ENCERRADO",
                ("iniciar", "temperatura"): "🌡 Monitoramento de temperatura INICIADO",
                ("encerrar", "temperatura"): "⏹ Monitoramento de temperatura ENCERRADO",
                ("iniciar", "atividade"): "📋 Registro da atividade INICIADO",
                ("encerrar", "atividade"): "✅ Registro da atividade ENCERRADO",
            }
            feedback = msgs.get((acao, objeto), f"Comando executado: {acao} {objeto}")

            return Response(
                json.dumps({"transcricao": transcricao, "feedback": feedback, "acao": acao, "objeto": objeto}, ensure_ascii=False),
                status=200,
                content_type="application/json"
            )
        else:
            return Response(
                json.dumps({"transcricao": transcricao, "feedback": "Comando não reconhecido. Tente novamente.", "acao": None, "objeto": None}, ensure_ascii=False),
                status=200,
                content_type="application/json"
            )
    except Exception as e:
        print(f"erro ao processar fala: {str(e)}")
        return Response(status=500)
    finally:
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)

def ativar_web(dispositivo, modelo, processador, palavras_de_parada, acoes):
    servico.config["dispositivo"] = dispositivo
    servico.config["modelo"] = modelo
    servico.config["processador"] = processador
    servico.config["palavras_de_parada"] = palavras_de_parada
    servico.config["acoes"] = acoes

    servico.run(host="0.0.0.0", port=7001)

if __name__ == "__main__":
    dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"

    iniciado, processador, modelo, palavras_de_parada, acoes = iniciar(dispositivo)

    if iniciado:
        if MODO_DE_FUNCIONAMENTO == MODO_LINHA_DE_COMANDO:
            ativar_linha_de_comando(dispositivo, modelo, processador, palavras_de_parada, acoes)
        elif MODO_DE_FUNCIONAMENTO == MODO_WEB:
            ativar_web(dispositivo, modelo, processador, palavras_de_parada, acoes)
        else:
            print("modo de funcionamento não implementado")
    else:
        print("ocorre um erro de inicialização")