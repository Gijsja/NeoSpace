/**
 * The Song Studio - Main Controller
 */
import { AudioEngine } from './AudioEngine.js';

export class SongStudio {
    constructor() {
        this.engine = new AudioEngine();
        this.isPlaying = false;
        this.bpm = 120;
        this.currentStep = 0;
        this.steps = 16;

        // Track Config
        this.trackList = ['kick', 'snare', 'hat_c', 'hat_o', 'bass', 'lead', 'pad', 'fx'];

        // Data State
        this.pattern = {};
        this.trackList.forEach(t => this.pattern[t] = new Array(this.steps).fill(0));

        // Note State (for melodic tracks) - Default basic notes
        this.notes = {};
        this.trackList.forEach(t => this.notes[t] = new Array(this.steps).fill(null));

        // Defaults
        this.notes.bass.fill("C2");
        this.notes.lead.fill("C4");
        this.notes.pad.fill("G3");
        this.notes.fx.fill("C5");

        this.init();
    }

    async init() {
        // Bind UI Controls
        this.bindControls();
        this.renderGrid();
    }

    bindControls() {
        document.getElementById('btn-play').onclick = () => this.togglePlay();
        document.getElementById('btn-clear').onclick = () => this.clearPattern();

        const bpmInput = document.getElementById('bpm-input');
        bpmInput.onchange = (e) => {
            this.bpm = parseInt(e.target.value);
            Tone.Transport.bpm.value = this.bpm;
        };

        // Save
        document.getElementById('btn-save').onclick = () => this.saveSong();
    }

    async togglePlay() {
        await this.engine.init();

        if (this.isPlaying) {
            Tone.Transport.stop();
            document.getElementById('btn-play').innerHTML = '<span>► PLAY</span>';
            document.getElementById('btn-play').classList.remove('bg-red-500', 'text-white');
            document.getElementById('btn-play').classList.add('bg-cyber-neon', 'text-cyber-black');
            this.currentStep = 0;
            this.updateVisuals(-1); // Reset
        } else {
            Tone.Transport.bpm.value = this.bpm;
            Tone.Transport.scheduleRepeat((time) => this.stepLoop(time), "16n");
            Tone.Transport.start();
            document.getElementById('btn-play').innerHTML = '<span>■ STOP</span>';
            document.getElementById('btn-play').classList.remove('bg-cyber-neon', 'text-cyber-black');
            document.getElementById('btn-play').classList.add('bg-red-500', 'text-white');
        }
        this.isPlaying = !this.isPlaying;
    }

    stepLoop(time) {
        const step = this.currentStep % this.steps;

        Tone.Draw.schedule(() => {
            this.updateVisuals(step);
        }, time);

        this.trackList.forEach(track => {
            if (this.pattern[track][step]) {
                const note = this.notes[track][step];
                this.engine.trigger(track, time, note);
            }
        });

        this.currentStep++;
    }

    updateVisuals(step) {
        // Clear old highlights
        document.querySelectorAll('.step-col-active').forEach(el => el.classList.remove('step-col-active', 'brightness-150', 'bg-white/10'));

        if (step === -1) return;

        // Highlight new
        const cells = document.querySelectorAll(`.step-col-${step}`);
        cells.forEach(cell => {
            cell.classList.add('step-col-active', 'brightness-150', 'bg-white/10');
        });

        // Update Time Display
        const transport = Tone.Transport.position.toString().split(':');
        document.getElementById('transport-time').innerText = `${transport[0]}:${transport[1]}`;
    }

    renderGrid() {
        const container = document.getElementById('sequencer-grid');
        container.innerHTML = '';

        // Header Row (Visual aid)
        // Render 8 rows
        this.trackList.forEach(track => {
            // Track Label
            // We handle labels via CSS grid in the main HTML now for alignment

            // Steps
            for (let i = 0; i < this.steps; i++) {
                const btn = document.createElement('div');
                btn.className = `h-10 border border-cyber-grid bg-black/50 cursor-pointer relative step-btn step-col-${i} hover:bg-white/5 transition-colors duration-75`;

                // Beat markers
                if (i % 4 === 0) btn.classList.add('border-l-gray-600');

                // Active State
                if (this.pattern[track][i]) {
                    btn.classList.add('active', `bg-${this.getTrackColor(track)}`);
                    btn.style.backgroundColor = this.getTrackColorHex(track);
                    btn.style.boxShadow = `0 0 10px ${this.getTrackColorHex(track)}`;
                }

                btn.onclick = () => {
                    this.pattern[track][i] = !this.pattern[track][i];
                    this.renderGrid(); // Brute force re-render for simplicity or toggle class
                };

                container.appendChild(btn);
            }
        });
    }

    getTrackColor(track) {
        // Tailwind classes map
        const map = {
            'kick': 'cyber-hot', 'snare': 'cyber-blue', 'hat_c': 'cyber-neon', 'hat_o': 'cyber-neon',
            'bass': '[#9d00ff]', 'lead': 'orange-500', 'pad': 'pink-500', 'fx': 'white'
        };
        return map[track];
    }

    getTrackColorHex(track) {
        const map = {
            'kick': '#ff0055', 'snare': '#00ccff', 'hat_c': '#ccff00', 'hat_o': '#ccff00',
            'bass': '#9d00ff', 'lead': '#f97316', 'pad': '#ec4899', 'fx': '#ffffff'
        };
        return map[track];
    }

    clearPattern() {
        this.trackList.forEach(t => this.pattern[t].fill(0));
        this.renderGrid();
    }

    async saveSong() {
        const title = prompt("Name your track:", "Untitled Track");
        if (!title) return;

        const data = {
            pattern: this.pattern,
            notes: this.notes,
            bpm: this.bpm
        };

        try {
            const res = await fetch('/song/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: title,
                    data: data,
                    is_public: 1
                })
            });
            const json = await res.json();
            if (json.ok) {
                alert("Track Saved! ID: " + json.id);
            } else {
                alert("Error: " + json.error);
            }
        } catch (e) {
            console.error(e);
            alert("Save failed");
        }
    }
}
