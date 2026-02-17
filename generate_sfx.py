import wave
import struct
import math
import os

def generate_beep(filename, frequency, duration, volume=0.5, sample_rate=44100):
    """Generiert einen einfachen Beep und speichert ihn als WAV."""
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    num_samples = int(duration * sample_rate)
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)  # Mono
        f.setsampwidth(2)   # 16-bit
        f.setframerate(sample_rate)
        
        for i in range(num_samples):
            # Sinus-Welle mit Envelope (Fading)
            envelope = 1.0
            if i < 441: # Attack
                envelope = i / 441
            elif i > num_samples - 441: # Release
                envelope = (num_samples - i) / 441
                
            value = int(math.sin(2 * math.pi * frequency * (i / sample_rate)) * 32767 * volume * envelope)
            f.writeframesraw(struct.pack('<h', value))

def main():
    print("Generiere Sound-Effekte...")
    # Navigations-Klick (kurz, mittlere Frequenz)
    generate_beep("assets/click.wav", 440, 0.05, volume=0.2)
    # Bestätigung (zwei Töne aufsteigend)
    generate_beep("assets/confirm.wav", 880, 0.1, volume=0.3)
    # Fehler (tief, kurz)
    generate_beep("assets/error.wav", 110, 0.15, volume=0.4)
    # Erfolg (fanfare-artig)
    generate_beep("assets/success.wav", 660, 0.2, volume=0.3)
    print("Fertig! Sounds in /assets gespeichert.")

if __name__ == "__main__":
    main()
