/**
 * The Song Studio - Audio Engine
 * Powered by Tone.js
 */

export class AudioEngine {
    constructor() {
        this.tracks = {};
        this.effects = {};
        this.master = null;
        this.isInitialized = false;
    }

    async init() {
        if (this.isInitialized) return;

        await Tone.start();
        console.log("Audio Engine Started");

        // --- Master Effects Chain ---
        this.effects.reverb = new Tone.Reverb({ decay: 2.5, wet: 0.1 }).toDestination();
        this.effects.delay = new Tone.PingPongDelay({ delayTime: "8n", feedback: 0.2, wet: 0.1 }).connect(this.effects.reverb);
        this.effects.limiter = new Tone.Limiter(-1).connect(this.effects.delay);

        // --- Instruments ---

        // 1. Kick (Membrane)
        this.tracks.kick = new Tone.MembraneSynth({
            pitchDecay: 0.05,
            octaves: 10,
            oscillator: { type: "sine" },
            envelope: { attack: 0.001, decay: 0.4, sustain: 0.01, release: 1.4, attackCurve: "exponential" }
        }).connect(this.effects.limiter);

        // 2. Snare (Noise + Membrane layer sim)
        this.tracks.snare = new Tone.NoiseSynth({
            noise: { type: "white" },
            envelope: { attack: 0.005, decay: 0.1, sustain: 0 }
        }).connect(this.effects.limiter);
        this.tracks.snare.volume.value = -3;

        // 3. HiHat Closed (Metal)
        this.tracks.hat_c = new Tone.MetalSynth({
            frequency: 250, envelope: { attack: 0.001, decay: 0.05, release: 0.01 },
            harmonicity: 5.1, modulationIndex: 32, resonance: 4000, octaves: 1.5
        }).connect(this.effects.limiter);
        this.tracks.hat_c.volume.value = -15;

        // 4. HiHat Open (Metal w/ longer decay)
        this.tracks.hat_o = new Tone.MetalSynth({
            frequency: 200, envelope: { attack: 0.001, decay: 0.3, release: 0.01 },
            harmonicity: 5.1, modulationIndex: 32, resonance: 4000, octaves: 1.5
        }).connect(this.effects.limiter);
        this.tracks.hat_o.volume.value = -15;

        // 5. Bass (MonoSynth)
        this.tracks.bass = new Tone.MonoSynth({
            oscillator: { type: "sawtooth" },
            filter: { Q: 2, type: "lowpass", rollover: -12 },
            envelope: { attack: 0.005, decay: 0.1, sustain: 0.9, release: 0.1 },
            filterEnvelope: { attack: 0.001, decay: 0.1, sustain: 0.5, baseFrequency: 200, octaves: 2.6 }
        }).connect(this.effects.limiter);
        this.tracks.bass.volume.value = -6;

        // 6. Lead (PolySynth - Saw)
        this.tracks.lead = new Tone.PolySynth(Tone.Synth, {
            oscillator: { type: "fatsawtooth", count: 3, spread: 30 },
            envelope: { attack: 0.01, decay: 0.1, sustain: 0.5, release: 0.4, }
        }).connect(this.effects.delay);
        this.tracks.lead.volume.value = -8;

        // 7. Pad (PolySynth - Triangle)
        this.tracks.pad = new Tone.PolySynth(Tone.Synth, {
            oscillator: { type: "triangle" },
            envelope: { attack: 0.5, decay: 0.5, sustain: 0.8, release: 1 }
        }).connect(this.effects.reverb);
        this.tracks.pad.volume.value = -12;

        // 8. FX (Pluck)
        this.tracks.fx = new Tone.PluckSynth({
            attackNoise: 1, dampening: 4000, resonance: 0.7
        }).connect(this.effects.delay);

        this.isInitialized = true;
    }

    trigger(trackName, time, note = null) {
        if (!this.isInitialized || !this.tracks[trackName]) return;
        const inst = this.tracks[trackName];

        if (trackName === 'kick') inst.triggerAttackRelease("C1", "8n", time);
        else if (trackName === 'snare') inst.triggerAttackRelease("8n", time);
        else if (trackName === 'hat_c') inst.triggerAttackRelease("32n", time);
        else if (trackName === 'hat_o') inst.triggerAttackRelease("16n", time);
        else if (trackName === 'bass') inst.triggerAttackRelease(note || "C2", "16n", time);
        else if (trackName === 'lead') inst.triggerAttackRelease(note || "C4", "16n", time);
        else if (trackName === 'pad') inst.triggerAttackRelease(note || "G3", "8n", time);
        else if (trackName === 'fx') inst.triggerAttackRelease(note || "C5", time);
    }

    setParam(target, param, value) {
        // e.g. target='reverb', param='wet', value=0.5
        if (this.effects[target]) {
            if (param in this.effects[target]) {
                this.effects[target][param].value = value;
            } else if (param === 'wet') {
                this.effects[target].wet.value = value;
            }
        }
    }
}
