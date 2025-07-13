import numpy as np
import random
import time
from scipy.io.wavfile import write

# --- Note & Chord Definitions ---
NOTES = {
    # Lower Octave
    "C3": 130.81, "D3": 146.83, "E3": 164.81, "F3": 174.61, "G3": 196.00, "A3": 220.00, "B3": 246.94,
    # Main Octave
    "C4": 261.63, "D4": 293.66, "Eb4": 311.13, "E4": 329.63, "F4": 349.23, "G4": 392.00, "Ab4": 415.30, "A4": 440.00, "B4": 493.88,
    # Higher Octave
    "C5": 523.25, "D5": 587.33, "E5": 659.25, "G5": 783.99
}
REST = "REST"

# --- Mood Definitions ---
MOODS = {
    "happy": {
        "scale": ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"],
        "chords": [("C4", "E4", "G4"), ("G4", "B4", "D5"), ("A4", "C5", "E5"), ("F4", "A4", "C5")],
        "bpm": 120
    },
    "sad": {
        "scale": ["C4", "Eb4", "F4", "G4", "Ab4", "C5"],
        "chords": [("C4", "Eb4", "G4"), ("Ab4", "C5", "Eb4"), ("F3", "Ab3", "C4"), ("G3", "A3", "D4")],
        "bpm": 75
    },
    "dreamy": {
        "scale": ["C4", "E4", "G4", "A4", "C5", "E5", "G5"],
        "chords": [("C4", "E4", "G4", "B4"), ("A3", "C4", "E4", "G4")],
        "bpm": 60
    }
}

def create_waveform(frequency, duration, sample_rate, instrument):
    """Generates audio data for a note with a distinct, clear instrument sound."""
    t = np.linspace(0., duration, int(sample_rate * duration), endpoint=False)
    
    # --- Instrument Recipes ---
    if instrument == 'piano':
        # Rich sound with several harmonics
        data = (0.6 * np.sin(2. * np.pi * frequency * t) + 
                0.2 * np.sin(2. * np.pi * (frequency * 2) * t) + 
                0.1 * np.sin(2. * np.pi * (frequency * 3) * t))
    elif instrument == 'organ':
        # Full sound mixing octaves
        data = (0.5 * np.sin(2. * np.pi * (frequency * 0.5) * t) + # Sub-octave
                0.5 * np.sin(2. * np.pi * frequency * t) +
                0.3 * np.sin(2. * np.pi * (frequency * 2) * t)) # Octave
    elif instrument == 'retro_synth':
        # A classic square wave for an 8-bit sound
        data = np.sign(np.sin(2. * np.pi * frequency * t))
    else: # Default to piano
        data = (0.6 * np.sin(2. * np.pi * frequency * t) + 0.2 * np.sin(2. * np.pi * (frequency * 2) * t))

    # --- Apply a standard decay envelope ---
    envelope = np.exp(np.linspace(0., -5., len(data)))
    return data * envelope

def generate_music(mood_key, instrument, total_duration_seconds):
    """Generates a musical piece by synthesizing and mixing NumPy arrays."""
    mood = MOODS[mood_key]
    scale = mood["scale"] + [REST]
    chords = mood["chords"]
    bpm = mood["bpm"]

    quarter_note_duration = 60 / bpm
    rhythms = [quarter_note_duration, quarter_note_duration / 2, quarter_note_duration * 1.5]

    melody_sequence = []
    current_time = 0
    while current_time < total_duration_seconds:
        duration = random.choice(rhythms)
        if current_time + duration > total_duration_seconds:
            duration = total_duration_seconds - current_time
        melody_note = random.choice(scale)
        melody_sequence.append({"note": melody_note, "duration": duration})
        current_time += duration

    print(f"\nSynthesizing a '{mood_key}' tune with a '{instrument}' sound...")
    sample_rate = 44100
    final_track_data = np.zeros(int(sample_rate * total_duration_seconds))
    
    current_pos_samples = 0
    chord_index = 0
    for item in melody_sequence:
        duration_samples = int(item["duration"] * sample_rate)
        
        # Add Melody
        if item["note"] != REST:
            freq = NOTES[item["note"]]
            mel_wave = create_waveform(freq, item["duration"], sample_rate, instrument)
            final_track_data[current_pos_samples:current_pos_samples + duration_samples] += mel_wave * 0.45 # Melody volume

        # Add Harmony (Chords)
        current_chord_notes = chords[chord_index]
        for note_name in current_chord_notes:
            if note_name in NOTES:
                freq = NOTES[note_name]
                # Chords now use a softer 'organ' sound so they don't overpower the melody
                chord_wave = create_waveform(freq, item["duration"], sample_rate, 'organ')
                final_track_data[current_pos_samples:current_pos_samples + duration_samples] += chord_wave * 0.20 # Chords volume

        current_pos_samples += duration_samples
        if current_pos_samples % int((quarter_note_duration * 4) * sample_rate) < duration_samples:
            chord_index = (chord_index + 1) % len(chords)

    print("Normalizing and saving file...")
    max_amp = np.max(np.abs(final_track_data))
    if max_amp > 0:
        final_track_data = final_track_data / max_amp
    
    scaled_data = (final_track_data * 32767).astype(np.int16)
    
    timestamp = int(time.time())
    filename = f"track_{mood_key}_{instrument}_{timestamp}.wav"
    
    write(filename, sample_rate, scaled_data)
    print(f"Done! 🎉 Your masterpiece is saved as '{filename}'")

if __name__ == "__main__":
    print("--- 🎵 Final AI Music Generator 🎵 ---")
    
    try:
        instrument_options = ['piano', 'organ', 'retro_synth']
        print("\nChoose an instrument sound:")
        for i, option in enumerate(instrument_options, 1): print(f"{i}. {option.replace('_', ' ').title()}")
        inst_choice_num = int(input("> "))
        chosen_instrument = instrument_options[inst_choice_num - 1]
        
        mood_options = list(MOODS.keys())
        print("\nChoose a mood:")
        for i, option in enumerate(mood_options, 1): print(f"{i}. {option.capitalize()}")
        mood_choice_num = int(input("> "))
        chosen_mood = mood_options[mood_choice_num - 1]
        
        duration = int(input("\nEnter desired duration in seconds (e.g., 60): "))

        generate_music(chosen_mood, chosen_instrument, duration)

    except (ValueError, IndexError):
        print("\nInvalid choice. Please run the script again and enter a valid number.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")