# 🤖 RoboLab — Assistente Inteligente de Laboratório

> Trabalho avaliativo da disciplina de **Inteligência Artificial**  
> Curso de Engenharia / Ciência da Computação

---

## 📋 Descrição

O **RoboLab** é um assistente virtual baseado em reconhecimento de fala em língua portuguesa, desenvolvido para controlar e monitorar um laboratório de robótica educacional por meio de **comandos de voz**.

O sistema utiliza o modelo de deep learning **Wav2Vec2** para transcrever falas capturadas pelo microfone do usuário, processa os tokens resultantes com **NLP** (remoção de stopwords via NLTK) e executa ações nos subsistemas do laboratório de forma assíncrona. A interface é acessível pelo navegador, servida por um backend em **Flask**.

---

## 🎯 Objetivos do Projeto

- Aplicar técnicas de **Processamento de Linguagem Natural (PLN)** para interpretar comandos em português.
- Integrar um modelo de **reconhecimento automático de fala (ASR)** pré-treinado via Hugging Face Transformers.
- Desenvolver uma arquitetura modular de **atuadores** que respondem a comandos de voz.
- Criar uma interface web em tempo real que exiba o estado de todos os subsistemas monitorados.

---

## 🧠 Conceitos de IA Aplicados

| Conceito | Tecnologia / Técnica Utilizada |
|---|---|
| Reconhecimento de Fala (ASR) | Wav2Vec2 (`lgris/wav2vec2-large-xlsr-open-brazilian-portuguese-v2`) |
| Processamento de Linguagem Natural | Tokenização e remoção de stopwords com NLTK |
| Inferência com Redes Neurais | PyTorch + HuggingFace Transformers |
| Correspondência por palavras-chave | Algoritmo de score com mapeamento semântico |
| Aceleração por GPU | Suporte automático a CUDA (`cuda:0`) |

---

## ⚙️ Arquitetura do Sistema

```
assistente.py          ← Ponto de entrada; orquestra o sistema
│
├── transcritor.py     ← Carrega e executa o modelo Wav2Vec2 (ASR)
├── inicializador_modelo.py  ← Inicialização do modelo Wav2Vec2
├── inicializador_nltk.py    ← Configuração do NLTK
│
├── bancada.py         ← Atuador: liga/desliga o sistema da bancada
├── experimento.py     ← Atuador: inicia/encerra monitoramento do experimento
├── energia.py         ← Atuador: monitora consumo energético em tempo real
├── temperatura.py     ← Atuador: monitora temperatura com alertas de limite
├── registro.py        ← Atuador: registra a atividade e gera relatório JSON
│
├── config.json        ← Mapeamento de ações e dispositivos reconhecidos
│
└── public/
    ├── index.html     ← Interface web do assistente
    ├── style.css      ← Estilização (dark mode, glassmorphism)
    └── script.js      ← Lógica de gravação de áudio e comunicação com a API
```

### Fluxo de Processamento

```
[Microfone] → [Captura de Áudio] → [Arquivo .wav temporário]
     ↓
[Wav2Vec2: Transcrição da fala em texto]
     ↓
[NLTK: Tokenização + Remoção de stopwords]
     ↓
[Validação de Comando: Score por palavras-chave]
     ↓
[Despacho para Atuador via Thread]
     ↓
[Atualização do Estado em Tempo Real na Interface Web]
```

---

## 🗣️ Comandos de Voz Reconhecidos

| Frase Exemplo | Ação |
|---|---|
| *"Ligar sistema da bancada"* | Liga o sistema principal |
| *"Desligar sistema da bancada"* | Desliga o sistema principal |
| *"Iniciar monitoramento do experimento"* | Inicia o rastreamento do experimento |
| *"Encerrar monitoramento do experimento"* | Para o rastreamento do experimento |
| *"Iniciar monitoramento de energia"* | Começa a medir consumo energético |
| *"Encerrar monitoramento de energia"* | Para a medição de energia |
| *"Iniciar monitoramento de temperatura"* | Ativa a leitura de temperatura |
| *"Encerrar monitoramento de temperatura"* | Desativa a leitura de temperatura |
| *"Iniciar registro da atividade"* | Inicia a gravação da sessão em relatório |
| *"Encerrar registro da atividade"* | Finaliza e salva o relatório em JSON |

> **Nota:** O sistema tolera variações naturais da fala. O algoritmo de validação exige correspondência de **pelo menos 2 palavras-chave** do comando para aceitá-lo.

---

## 🖥️ Interface Web

A interface web (acessível em `http://localhost:7001`) apresenta:

- **Painel de Comando de Voz** — botão de microfone com animação de gravação, exibição da transcrição e feedback do comando executado.
- **Dashboard de Monitoramento** — cards com status em tempo real de todos os subsistemas (Bancada, Experimento, Energia, Temperatura e Registro).
- **Log de Eventos** — histórico das interações com timestamps.

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.10+
- Microfone funcional
- GPU com CUDA (opcional, mas recomendado para melhor desempenho de transcrição)

### 1. Criar e ativar o ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

> ⚠️ O download do modelo Wav2Vec2 (~1.2 GB) será feito automaticamente no primeiro uso via Hugging Face.

### 3. Inicializar os dados do NLTK

```bash
python inicializador_nltk.py
```

### 4. Iniciar o assistente

```bash
python assistente.py
```

### 5. Acessar a interface

Abra o navegador e acesse:

```
http://localhost:7001
```

---

## 📦 Dependências

| Pacote | Finalidade |
|---|---|
| `torch` | Framework de deep learning (inferência do modelo) |
| `torchaudio` | Carregamento e reamostragem de áudio |
| `transformers` | Carregamento do modelo Wav2Vec2 via Hugging Face |
| `flask` | Servidor web e API REST |
| `nltk` | Tokenização e stopwords em português |
| `sounddevice` | Captura de áudio pelo microfone |
| `soundfile` (PySoundFile) | Leitura e escrita de arquivos de áudio |

---

## 📁 Estrutura de Diretórios

```
assistente virtual web/
├── assistente.py
├── bancada.py
├── config.json
├── energia.py
├── experimento.py
├── inicializador_modelo.py
├── inicializador_nltk.py
├── registro.py
├── requirements.txt
├── temperatura.py
├── transcritor.py
├── testes.py
├── testar_gpu.py
├── audios/           ← Áudios de referência para testes
├── public/           ← Interface web (HTML, CSS, JS)
├── relatorios/       ← Relatórios JSON gerados automaticamente
├── temp/             ← Arquivos de áudio temporários (descartados após uso)
└── venv/             ← Ambiente virtual Python
```

---

## 🧪 Testes

O arquivo `testes.py` contém testes automatizados para validar:

- A transcrição dos áudios de referência pelo modelo Wav2Vec2.
- A acurácia da correspondência entre transcrição e comandos esperados.
- O comportamento de cada módulo atuador.

Para executar:

```bash
python testes.py
```

---

## 📊 Modos de Operação

O sistema suporta dois modos, configuráveis diretamente em `assistente.py`:

| Modo | Descrição |
|---|---|
| `MODO_WEB` (padrão) | Interface gráfica no navegador com API REST |
| `MODO_LINHA_DE_COMANDO` | Loop contínuo de captura e transcrição no terminal |

---

## 👨‍💻 Autores

Desenvolvido como trabalho avaliativo da disciplina de **Inteligência Artificial**.

---

## 📄 Licença

Projeto acadêmico — uso educacional.
