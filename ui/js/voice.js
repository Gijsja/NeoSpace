
window.VoiceRecorder = window.VoiceRecorder || class VoiceRecorder {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.audioContext = null;
        this.analyser = null;
        this.source = null;
        this.isRecording = false;
        this.animationId = null;
        this.stream = null;
        this.waveform = []; // Store simplified peaks for saving
    }

    async start() {
        if (this.isRecording) return;

        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // Setup Audio Context for visualization
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            this.source = this.audioContext.createMediaStreamSource(this.stream);
            this.source.connect(this.analyser);

            // Setup Recorder
            this.mediaRecorder = new MediaRecorder(this.stream, { mimeType: 'audio/webm' });
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.start(100); // Slice chunks for safety
            this.isRecording = true;
            this.waveform = [];

            this.visualize();

        } catch (err) {
            console.error("Error accessing microphone:", err);
            throw err;
        }
    }

    stop() {
        return new Promise((resolve) => {
            if (!this.isRecording) return resolve(null);

            this.isRecording = false;
            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                this.cleanup();
                resolve({
                    blob: audioBlob,
                    waveform: this.normalizeWaveform(this.waveform)
                });
            };
            this.mediaRecorder.stop();
        });
    }

    cleanup() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
        if (this.audioContext) {
            this.audioContext.close();
        }
        cancelAnimationFrame(this.animationId);
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    visualize() {
        if (!this.isRecording) return;

        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const draw = () => {
            if (!this.isRecording) return;
            this.animationId = requestAnimationFrame(draw);

            this.analyser.getByteFrequencyData(dataArray);

            // Draw
            this.ctx.fillStyle = 'rgba(15, 23, 42, 0.5)'; // clear with fade
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

            const barWidth = (this.canvas.width / bufferLength) * 2.5;
            let barHeight;
            let x = 0;

            // Calculate a peak for this frame to store
            let frameSum = 0;

            for (let i = 0; i < bufferLength; i++) {
                barHeight = dataArray[i] / 2;
                frameSum += barHeight;

                this.ctx.fillStyle = `rgb(${barHeight + 100}, 50, 150)`; // Dynamic purple
                this.ctx.fillRect(x, this.canvas.height - barHeight, barWidth, barHeight);

                x += barWidth + 1;
            }

            // Sample waveform occasionally
            this.waveform.push(frameSum / bufferLength);
        };

        draw();
    }

    // Normalize waveform to [0, 1] range for portable storage
    normalizeWaveform(data) {
        // Downsample to ~50 points
        const targetLength = 50;
        const blockSize = Math.floor(data.length / targetLength) || 1;
        const sampled = [];

        for (let i = 0; i < targetLength; i++) {
            let sum = 0;
            let count = 0;
            for (let j = 0; j < blockSize; j++) {
                const idx = i * blockSize + j;
                if (idx < data.length) {
                    sum += data[idx];
                    count++;
                }
            }
            sampled.push(count > 0 ? (sum / count) / 255.0 : 0); // approx normalize based on byte frequency max
        }
        return sampled;
    }
};

window.VoicePlayer = window.VoicePlayer || class VoicePlayer {
    constructor(containerId, audioUrl, waveformData) {
        this.container = document.getElementById(containerId);
        this.audioUrl = audioUrl;
        this.waveformData = waveformData || []; // Array of 0.0-1.0
        this.audio = new Audio(audioUrl);
        this.isPlaying = false;

        this.render();
    }

    render() {
        this.container.innerHTML = '';
        this.container.className = "flex items-center gap-3 bg-slate-800/50 p-2 rounded-xl border border-white/10 w-full hover:bg-slate-800/80 transition group cursor-pointer";

        // Play Button
        const btn = document.createElement('button');
        btn.className = "w-8 h-8 rounded-full bg-bbs-accent flex items-center justify-center text-white shrink-0 shadow-glow transition hover:scale-105";
        btn.innerHTML = '<i class="ph-bold ph-play"></i>';

        // Canvas
        const canvas = document.createElement('canvas');
        canvas.height = 32;
        canvas.width = 200;
        canvas.className = "w-full h-8 opacity-70 group-hover:opacity-100 transition";

        this.ctx = canvas.getContext('2d');
        this.canvas = canvas;

        this.container.appendChild(btn);
        this.container.appendChild(canvas);

        this.drawWaveform(0);

        // Events
        btn.onclick = (e) => {
            e.stopPropagation();
            this.togglePlay(btn);
        };
        this.container.onclick = () => this.togglePlay(btn);

        this.audio.onended = () => {
            this.isPlaying = false;
            btn.innerHTML = '<i class="ph-bold ph-play"></i>';
            this.drawWaveform(0);
            cancelAnimationFrame(this.animId);
        };

        this.audio.ontimeupdate = () => {
            // Redraw with progress?
            //  this.drawWaveform(this.audio.currentTime / this.audio.duration);
        };

        this.audio.addEventListener('play', () => {
            const loop = () => {
                if (!this.isPlaying) return;
                this.drawWaveform(this.audio.currentTime / this.audio.duration);
                this.animId = requestAnimationFrame(loop);
            }
            loop();
        });
    }

    togglePlay(btn) {
        if (this.isPlaying) {
            this.audio.pause();
            this.isPlaying = false;
            btn.innerHTML = '<i class="ph-bold ph-play"></i>';
            cancelAnimationFrame(this.animId);
        } else {
            this.audio.play();
            this.isPlaying = true;
            btn.innerHTML = '<i class="ph-bold ph-pause"></i>';
        }
    }

    drawWaveform(progress) {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;
        const data = this.waveformData;
        const barW = w / data.length;
        const gap = 1;

        ctx.clearRect(0, 0, w, h);

        data.forEach((val, i) => {
            const barH = Math.max(2, val * h);
            const x = i * (barW);
            const y = (h - barH) / 2;

            // Color based on progress
            const isPlayed = (i / data.length) < progress;
            ctx.fillStyle = isPlayed ? '#60a5fa' : '#475569';

            // Round caps?
            Utils.roundRect(ctx, x, y, barW - gap, barH, 2);
            ctx.fill();
        });
    }
};

// Helper for round rect if not supported
window.Utils = window.Utils || {
    roundRect: function (ctx, x, y, w, h, r) {
        if (w < 2 * r) r = w / 2;
        if (h < 2 * r) r = h / 2;
        ctx.beginPath();
        ctx.moveTo(x + r, y);
        ctx.arcTo(x + w, y, x + w, y + h, r);
        ctx.arcTo(x + w, y + h, x, y + h, r);
        ctx.arcTo(x, y + h, x, y, r);
        ctx.arcTo(x, y, x + w, y, r);
        ctx.closePath();
    }
};
