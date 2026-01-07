# Sprint 9: Sonic Identity - Implementation Plan

## Goal

Allow users to record and display a "Voice Intro" on their profile with a rich waveform visualization.

## 1. Database & Backend

- [x] **Verify Schema**: Confirm `voice_intro_path` and `voice_waveform_json` columns exist in `profiles` table. (Confirmed in `db.py`)
- [ ] **Mutation Handler**: Create `mutations/voice.py` to handle:
  - File upload (audio/webm or audio/mp3)
  - Saving file to `static/uploads/voice/`
  - Updating profile record
- [ ] **API Endpoint**: Register `/api/profile/voice` in `app.py`.

## 2. Frontend: Recording (The "Sonicizer")

- [ ] **Visualizer Component**: Create `ui/js/voice.js` containing:
  - classes for `VoiceRecorder` and `WaveformPlayer`.
  - Real-time frequency visualization using `AudioContext` and `AnalyserNode`.
- [ ] **UI Integration**:
  - Add "Record Intro" button to Profile Edit Modal in `wall.html`.
  - Show recording interface (canvas + controls).

## 3. Frontend: Playback

- [ ] **Profile Card Update**:
  - Display the Voice Intro player on the user's profile card in `wall.html`.
  - Use the stored waveform JSON to render a static (playable) visualization.

## 4. Verification

- [ ] Create `tests/verify_voice.py` to test the upload endpoint and database updates.
