/* ============================================================
   RoboLab — script.js
   Voice recording, command processing, status polling
   ============================================================ */

const recordButton      = document.getElementById('recordButton');
const micHint           = document.getElementById('micHint');
const transcriptionText = document.getElementById('transcriptionText');
const feedbackBox       = document.getElementById('feedbackBox');
const feedbackText      = document.getElementById('feedbackText');
const logContainer      = document.getElementById('logContainer');
const clearLogBtn       = document.getElementById('clearLogBtn');
const systemStatusDot   = document.getElementById('systemStatusDot');
const systemStatusLabel = document.getElementById('systemStatusLabel');

// Monitoring elements
const badgeBancada      = document.getElementById('badgeBancada');
const badgeExperimento  = document.getElementById('badgeExperimento');
const badgeEnergia      = document.getElementById('badgeEnergia');
const badgeTemperatura  = document.getElementById('badgeTemperatura');
const badgeRegistro     = document.getElementById('badgeRegistro');

const cardBancada       = document.getElementById('cardBancada');
const cardEnergia       = document.getElementById('cardEnergia');
const cardTemperatura   = document.getElementById('cardTemperatura');

const potenciaAtual     = document.getElementById('potenciaAtual');
const consumoTotal      = document.getElementById('consumoTotal');
const tempAtual         = document.getElementById('tempAtual');
const alertasCount      = document.getElementById('alertasCount');

const detailBancada     = document.getElementById('detailBancada');
const detailExperimento = document.getElementById('detailExperimento');
const detailEnergia     = document.getElementById('detailEnergia');
const detailTemperatura = document.getElementById('detailTemperatura');
const detailRegistro    = document.getElementById('detailRegistro');

// Set init time
document.getElementById('initTime').textContent = now();

let recorder, audioContext, stream, isRecording = false;
let statusInterval = null;

// ---- Recording ----

recordButton.addEventListener('click', async () => {
    if (!isRecording) {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const source = audioContext.createMediaStreamSource(stream);
            recorder = new Recorder(source, { numChannels: 1 });
            recorder.record();

            setMicState('recording');
            addLog('Gravação iniciada...', 'info');
        } catch (err) {
            console.error('Erro ao acessar microfone:', err);
            addLog('Erro ao acessar microfone: ' + err.message, 'error');
        }
    } else {
        recorder.stop();
        stream.getTracks().forEach(track => track.stop());
        setMicState('processing');
        addLog('Processando fala...', 'info');

        recorder.exportWAV(async (audioBlob) => {
            const formData = new FormData();
            formData.append('fala', audioBlob, 'fala.wav');

            try {
                const response = await fetch('/reconhecer_comando', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                const result = await response.json();

                // Show transcription
                transcriptionText.textContent = result.transcricao || '(sem transcrição)';

                // Show feedback
                const ok = result.acao !== null;
                showFeedback(result.feedback || 'Sem resposta', ok ? 'success' : 'error');

                addLog(
                    ok
                        ? `✅ Comando executado: "${result.acao} ${result.objeto}" — "${result.transcricao}"`
                        : `⚠ Comando não reconhecido — "${result.transcricao}"`,
                    ok ? 'success' : 'warn'
                );
            } catch (error) {
                showFeedback('Erro na comunicação com o servidor.', 'error');
                addLog('Erro de comunicação: ' + error.message, 'error');
                console.error('Erro:', error);
            }

            setMicState('idle');
        });
    }
});

clearLogBtn.addEventListener('click', () => {
    logContainer.innerHTML = '';
    addLog('Log limpo.', 'info');
});

// ---- UI helpers ----

function setMicState(state) {
    recordButton.classList.remove('recording', 'processing');
    isRecording = false;

    if (state === 'recording') {
        recordButton.classList.add('recording');
        micHint.textContent = 'Gravando... pressione para parar';
        isRecording = true;
    } else if (state === 'processing') {
        recordButton.classList.add('processing');
        micHint.textContent = 'Processando...';
    } else {
        micHint.textContent = 'Pressione para falar';
    }
}

function showFeedback(msg, type) {
    feedbackBox.className = 'feedback-box ' + (type || '');
    feedbackText.textContent = msg;
}

function addLog(msg, type = 'info') {
    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;
    entry.innerHTML = `<span class="log-time">${now()}</span><span class="log-msg">${msg}</span>`;
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

function now() {
    return new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

// ---- Status polling ----

function setBadge(el, text, cls) {
    el.textContent = text;
    el.className = 'monitor-badge ' + cls;
}

function updateStatus(data) {
    // System online indicator
    systemStatusDot.className = 'status-dot online';
    systemStatusLabel.textContent = 'Sistema Online';

    // Bancada
    const b = data.bancada;
    if (b.ligada) {
        setBadge(badgeBancada, 'ONLINE', 'badge-online');
        cardBancada.classList.add('active-card');
        detailBancada.textContent = 'Ambiente de monitoramento ativo';
    } else {
        setBadge(badgeBancada, 'OFFLINE', 'badge-offline');
        cardBancada.classList.remove('active-card');
        detailBancada.textContent = '—';
    }

    // Experimento
    const ex = data.experimento;
    if (ex.monitorando) {
        setBadge(badgeExperimento, 'ATIVO', 'badge-active');
        detailExperimento.textContent = `${ex.eventos ? ex.eventos.length + ' evento(s) registrado(s)' : 'Em andamento...'}`;
    } else {
        setBadge(badgeExperimento, 'PARADO', 'badge-offline');
        detailExperimento.textContent = '—';
    }

    // Energia
    const en = data.energia;
    if (en.monitorando) {
        setBadge(badgeEnergia, 'ATIVO', 'badge-active');
        cardEnergia.classList.add('active-card');
        potenciaAtual.textContent = en.potencia_atual_w ? en.potencia_atual_w.toFixed(1) : '—';
        consumoTotal.textContent = en.consumo_total_wh ? en.consumo_total_wh.toFixed(4) : '—';
        detailEnergia.textContent = 'Última leitura: ' + now();
    } else {
        setBadge(badgeEnergia, 'PARADO', 'badge-offline');
        cardEnergia.classList.remove('active-card');
        potenciaAtual.textContent = '—';
        consumoTotal.textContent = '—';
        detailEnergia.textContent = '—';
    }

    // Temperatura
    const temp = data.temperatura;
    if (temp.monitorando) {
        const hasAlert = temp.alertas && temp.alertas.length > 0;
        setBadge(badgeTemperatura, hasAlert ? 'ALERTA' : 'ATIVO', hasAlert ? 'badge-warning' : 'badge-active');
        cardTemperatura.classList.toggle('active-card', !hasAlert);
        cardTemperatura.classList.toggle('warn-card', hasAlert);
        tempAtual.textContent = temp.temperatura_atual_c ? temp.temperatura_atual_c.toFixed(1) + '°' : '—';
        alertasCount.textContent = temp.alertas ? temp.alertas.length : '0';
        if (hasAlert) {
            const lastAlert = temp.alertas[temp.alertas.length - 1];
            detailTemperatura.textContent = lastAlert.mensagem;
            detailTemperatura.classList.add('has-alert');
            // log the alert (avoid spam: track with data attr)
            const alertMsg = lastAlert.timestamp + ' ' + lastAlert.mensagem;
            if (detailTemperatura.dataset.lastAlert !== alertMsg) {
                detailTemperatura.dataset.lastAlert = alertMsg;
                addLog('🌡 ' + lastAlert.mensagem, 'warn');
            }
        } else {
            detailTemperatura.textContent = 'Dentro dos limites normais';
            detailTemperatura.classList.remove('has-alert');
        }
    } else {
        setBadge(badgeTemperatura, 'PARADO', 'badge-offline');
        cardTemperatura.classList.remove('active-card', 'warn-card');
        tempAtual.textContent = '—';
        alertasCount.textContent = '—';
        detailTemperatura.textContent = '—';
        detailTemperatura.classList.remove('has-alert');
    }

    // Registro
    const reg = data.registro;
    if (reg.registrando) {
        setBadge(badgeRegistro, 'EM ANDAMENTO', 'badge-active');
        detailRegistro.textContent = reg.data_inicio ? `Iniciado em: ${reg.data_inicio}` : 'Em andamento...';
    } else {
        setBadge(badgeRegistro, 'PARADO', 'badge-offline');
        detailRegistro.textContent = reg.data_inicio ? `Último início: ${reg.data_inicio}` : '—';
    }
}

async function pollStatus() {
    try {
        const res = await fetch('/status');
        if (res.ok) {
            const data = await res.json();
            updateStatus(data);
        }
    } catch (e) {
        // server may not be reachable, silently skip
    }
}

// Start polling every 2 seconds
statusInterval = setInterval(pollStatus, 2000);
pollStatus(); // immediate first call
