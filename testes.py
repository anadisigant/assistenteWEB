"""
testes.py — Testes automatizados do Assistente de Laboratório de Robótica Educacional
Cobre: transcrição, processamento, validação de comandos e atuação de cada subsistema.
"""

from assistente import (
    iniciar, processar_transcricao, validar_comando,
    MAPA_COMANDOS
)
from transcritor import carregar_fala, transcrever_fala
import bancada
import experimento
import energia
import temperatura
import registro
import unittest
import torch
import time
import os

# ---------------------------------------------------------------------------
# Caminhos dos áudios de teste (pasta audios/)
# ---------------------------------------------------------------------------
AUDIO = {
    "ligar_bancada":             "audios/ligar-sistemaBancada.wav",
    "desligar_bancada":          "audios/desligar-sistemaBancada.wav",
    "iniciar_experimento":       "audios/iniciar-monitoramentoExperimento.wav",
    "encerrar_experimento":      "audios/encerrar-monitoramentoExperimento.wav",
    "iniciar_energia":           "audios/iniciar-monitoramentoEnergia.wav",
    "encerrar_energia":          "audios/encerrar-monitoramentoEnergia.wav",
    "iniciar_temperatura":       "audios/iniciar-monitoramentoTemperatura.wav",
    "encerrar_temperatura":      "audios/encerrar-monitoramentoTemperatura.wav",
    "iniciar_registro":          "audios/iniciar-registroAtividade.wav",
    "encerrar_registro":         "audios/encerrar-registroAtividade.wav",
}

# ---------------------------------------------------------------------------
# Classe auxiliar: inicializa modelo uma única vez para toda a suite
# ---------------------------------------------------------------------------
class BaseTesteTranscricao(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
        cls.iniciado, cls.processador, cls.modelo, cls.palavras_de_parada, cls.acoes = \
            iniciar(cls.dispositivo)

    def _pipeline(self, chave_audio, acao_esperada, objeto_esperado):
        """
        Executa o pipeline completo: carrega → transcreve → processa → valida.
        Retorna (valido, acao, objeto) e falha o teste se qualquer etapa falhar.
        """
        caminho = AUDIO[chave_audio]
        self.assertTrue(os.path.exists(caminho),
                        f"Arquivo de áudio não encontrado: {caminho}")

        fala = carregar_fala(caminho)
        self.assertIsNotNone(fala)

        transcricao = transcrever_fala(
            self.dispositivo, fala, self.modelo, self.processador)
        self.assertIsNotNone(transcricao)
        self.assertIsInstance(transcricao, str)
        print(f"\n  [{chave_audio}] transcrição: \"{transcricao}\"")

        tokens = processar_transcricao(transcricao, self.palavras_de_parada)
        self.assertIsNotNone(tokens)

        valido, acao, objeto = validar_comando(tokens)
        self.assertTrue(valido,
                        f"Comando não reconhecido. Tokens: {tokens} | Transcrição: \"{transcricao}\"")
        self.assertEqual(acao, acao_esperada,
                         f"Ação esperada '{acao_esperada}', obtida '{acao}'")
        self.assertEqual(objeto, objeto_esperado,
                         f"Objeto esperado '{objeto_esperado}', obtido '{objeto}'")
        return valido, acao, objeto


# ===========================================================================
# 1. Testes de infraestrutura
# ===========================================================================
class Teste01Infraestrutura(BaseTesteTranscricao):

    def testar_01_modelo_iniciado(self):
        """O modelo Wav2Vec2 deve inicializar sem erros."""
        self.assertTrue(self.iniciado, "Falha ao inicializar o modelo de transcrição.")

    def testar_02_audios_existem(self):
        """Todos os arquivos de áudio de teste devem existir na pasta audios/."""
        for chave, caminho in AUDIO.items():
            with self.subTest(audio=chave):
                self.assertTrue(os.path.exists(caminho),
                                f"Arquivo ausente: {caminho}")

    def testar_03_mapa_comandos_completo(self):
        """MAPA_COMANDOS deve conter exatamente os 10 comandos previstos."""
        self.assertEqual(len(MAPA_COMANDOS), 10,
                         f"Esperados 10 comandos, encontrados {len(MAPA_COMANDOS)}")


# ===========================================================================
# 2. Testes de transcrição e validação — Bancada
# ===========================================================================
class Teste02Bancada(BaseTesteTranscricao):

    def testar_01_ligar_sistema_bancada(self):
        """Áudio 'ligar sistema da bancada' deve gerar ação=ligar, objeto=sistema."""
        self._pipeline("ligar_bancada", "ligar", "sistema")

    def testar_02_desligar_sistema_bancada(self):
        """Áudio 'desligar sistema da bancada' deve gerar ação=desligar, objeto=sistema."""
        self._pipeline("desligar_bancada", "desligar", "sistema")


# ===========================================================================
# 3. Testes de transcrição e validação — Experimento
# ===========================================================================
class Teste03Experimento(BaseTesteTranscricao):

    def testar_01_iniciar_monitoramento_experimento(self):
        """Áudio 'iniciar monitoramento do experimento' → ação=iniciar, objeto=experimento."""
        self._pipeline("iniciar_experimento", "iniciar", "experimento")

    def testar_02_encerrar_monitoramento_experimento(self):
        """Áudio 'encerrar monitoramento do experimento' → ação=encerrar, objeto=experimento."""
        self._pipeline("encerrar_experimento", "encerrar", "experimento")


# ===========================================================================
# 4. Testes de transcrição e validação — Energia
# ===========================================================================
class Teste04Energia(BaseTesteTranscricao):

    def testar_01_iniciar_monitoramento_energia(self):
        """Áudio 'iniciar monitoramento de energia' → ação=iniciar, objeto=energia."""
        self._pipeline("iniciar_energia", "iniciar", "energia")

    def testar_02_encerrar_monitoramento_energia(self):
        """Áudio 'encerrar monitoramento de energia' → ação=encerrar, objeto=energia."""
        self._pipeline("encerrar_energia", "encerrar", "energia")


# ===========================================================================
# 5. Testes de transcrição e validação — Temperatura
# ===========================================================================
class Teste05Temperatura(BaseTesteTranscricao):

    def testar_01_iniciar_monitoramento_temperatura(self):
        """Áudio 'iniciar monitoramento de temperatura' → ação=iniciar, objeto=temperatura."""
        self._pipeline("iniciar_temperatura", "iniciar", "temperatura")

    def testar_02_encerrar_monitoramento_temperatura(self):
        """Áudio 'encerrar monitoramento de temperatura' → ação=encerrar, objeto=temperatura."""
        self._pipeline("encerrar_temperatura", "encerrar", "temperatura")


# ===========================================================================
# 6. Testes de transcrição e validação — Registro
# ===========================================================================
class Teste06Registro(BaseTesteTranscricao):

    def testar_01_iniciar_registro_atividade(self):
        """Áudio 'iniciar registro da atividade' → ação=iniciar, objeto=atividade."""
        self._pipeline("iniciar_registro", "iniciar", "atividade")

    def testar_02_encerrar_registro_atividade(self):
        """Áudio 'encerrar registro da atividade' → ação=encerrar, objeto=atividade."""
        self._pipeline("encerrar_registro", "encerrar", "atividade")


# ===========================================================================
# 7. Testes de atuação dos módulos (sem modelo de transcrição)
# ===========================================================================
class Teste07AtuacaoModulos(unittest.TestCase):
    """Testa a lógica de estado de cada módulo de forma isolada (sem áudio)."""

    def setUp(self):
        # Garante que cada teste começa com módulos no estado inicial
        bancada.iniciar()
        experimento.iniciar()
        energia.iniciar()
        temperatura.iniciar()
        registro.iniciar()

    # ---- Bancada ----
    def testar_01_bancada_ligar(self):
        bancada.atuar("ligar", "sistema")
        self.assertTrue(bancada.get_estado()["ligada"])

    def testar_02_bancada_desligar(self):
        bancada.atuar("ligar", "sistema")
        bancada.atuar("desligar", "sistema")
        self.assertFalse(bancada.get_estado()["ligada"])

    def testar_03_bancada_ligar_duplicado(self):
        """Ligar duas vezes não deve alterar o estado (idempotente)."""
        bancada.atuar("ligar", "sistema")
        bancada.atuar("ligar", "sistema")
        self.assertTrue(bancada.get_estado()["ligada"])

    # ---- Experimento ----
    def testar_04_experimento_iniciar(self):
        experimento.atuar("iniciar", "experimento")
        self.assertTrue(experimento.get_estado()["monitorando"])

    def testar_05_experimento_encerrar(self):
        experimento.atuar("iniciar", "experimento")
        experimento.atuar("encerrar", "experimento")
        self.assertFalse(experimento.get_estado()["monitorando"])

    # ---- Energia ----
    def testar_06_energia_iniciar(self):
        energia.atuar("iniciar", "energia")
        self.assertTrue(energia.get_estado()["monitorando"])

    def testar_07_energia_encerrar(self):
        energia.atuar("iniciar", "energia")
        time.sleep(0.1)
        energia.atuar("encerrar", "energia")
        self.assertFalse(energia.get_estado()["monitorando"])

    def testar_08_energia_acumula_consumo(self):
        """Após iniciar e aguardar 2s, o consumo acumulado deve ser > 0."""
        energia.atuar("iniciar", "energia")
        time.sleep(2)
        estado = energia.get_estado()
        energia.atuar("encerrar", "energia")
        self.assertGreater(estado["consumo_total_wh"], 0.0)

    # ---- Temperatura ----
    def testar_09_temperatura_iniciar(self):
        temperatura.atuar("iniciar", "temperatura")
        self.assertTrue(temperatura.get_estado()["monitorando"])

    def testar_10_temperatura_encerrar(self):
        temperatura.atuar("iniciar", "temperatura")
        time.sleep(0.1)
        temperatura.atuar("encerrar", "temperatura")
        self.assertFalse(temperatura.get_estado()["monitorando"])

    def testar_11_temperatura_leitura_simulada(self):
        """Após 3s de monitoramento, deve haver pelo menos 1 leitura no histórico."""
        temperatura.atuar("iniciar", "temperatura")
        time.sleep(3)
        estado = temperatura.get_estado()
        temperatura.atuar("encerrar", "temperatura")
        self.assertGreater(len(estado["historico"]), 0)

    # ---- Registro ----
    def testar_12_registro_iniciar(self):
        registro.atuar("iniciar", "atividade")
        self.assertTrue(registro.get_estado()["registrando"])

    def testar_13_registro_encerrar_salva_relatorio(self):
        """Encerrar o registro deve criar um arquivo JSON na pasta relatorios/."""
        registro.atuar("iniciar", "atividade")
        time.sleep(0.1)
        arquivos_antes = set(os.listdir("relatorios")) if os.path.exists("relatorios") else set()
        registro.atuar("encerrar", "atividade")
        arquivos_depois = set(os.listdir("relatorios")) if os.path.exists("relatorios") else set()
        novos = arquivos_depois - arquivos_antes
        self.assertEqual(len(novos), 1, "Deveria ter sido gerado exatamente 1 relatório JSON.")
        novo_arquivo = novos.pop()
        self.assertTrue(novo_arquivo.endswith(".json"))

    def testar_14_registro_nao_ativo_apos_encerrar(self):
        registro.atuar("iniciar", "atividade")
        registro.atuar("encerrar", "atividade")
        self.assertFalse(registro.get_estado()["registrando"])


# ===========================================================================
# 8. Testes de validação com texto direto (sem transcrição)
# ===========================================================================
class Teste08ValidacaoTexto(unittest.TestCase):
    """Testa validar_comando usando tokens já conhecidos (ignora transcrição)."""

    @classmethod
    def setUpClass(cls):
        cls.dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
        _, _, _, cls.palavras_de_parada, _ = iniciar(cls.dispositivo)

    def _validar(self, transcricao, acao_esp, objeto_esp):
        tokens = processar_transcricao(transcricao, self.palavras_de_parada)
        valido, acao, objeto = validar_comando(tokens)
        self.assertTrue(valido, f"Esperava comando válido para: \"{transcricao}\"")
        self.assertEqual(acao, acao_esp)
        self.assertEqual(objeto, objeto_esp)

    def testar_01_ligar_bancada_texto(self):
        self._validar("ligar sistema da bancada", "ligar", "sistema")

    def testar_02_desligar_bancada_texto(self):
        self._validar("desligar sistema bancada", "desligar", "sistema")

    def testar_03_iniciar_experimento_texto(self):
        self._validar("iniciar monitoramento do experimento", "iniciar", "experimento")

    def testar_04_encerrar_experimento_texto(self):
        self._validar("encerrar monitoramento experimento", "encerrar", "experimento")

    def testar_05_iniciar_energia_texto(self):
        self._validar("iniciar monitoramento de energia", "iniciar", "energia")

    def testar_06_encerrar_energia_texto(self):
        self._validar("encerrar monitoramento energia", "encerrar", "energia")

    def testar_07_iniciar_temperatura_texto(self):
        self._validar("iniciar monitoramento de temperatura", "iniciar", "temperatura")

    def testar_08_encerrar_temperatura_texto(self):
        self._validar("encerrar monitoramento temperatura", "encerrar", "temperatura")

    def testar_09_iniciar_registro_texto(self):
        self._validar("iniciar registro da atividade", "iniciar", "atividade")

    def testar_10_encerrar_registro_texto(self):
        self._validar("encerrar registro atividade", "encerrar", "atividade")

    def testar_11_comando_invalido_rejeitado(self):
        """Uma frase aleatória sem palavras-chave suficientes deve ser rejeitada."""
        tokens = processar_transcricao("o robô está funcionando bem", self.palavras_de_parada)
        valido, _, _ = validar_comando(tokens)
        self.assertFalse(valido)


if __name__ == "__main__":
    unittest.main(verbosity=2)