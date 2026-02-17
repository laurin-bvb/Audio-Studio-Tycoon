"""
Audio-Manager für Audio Studio Tycoon - Audio Edition.
Kommuniziert direkt mit NVDA über accessible_output2.
Nutzt pygame.mixer für Sound-Effekte.
"""

import pygame


class AudioManager:
    def __init__(self):
        # NVDA-Ausgabe initialisieren
        self.speaker = None
        try:
            from accessible_output2.outputs import nvda
            self.speaker = nvda.NVDA()
        except Exception as e:
            print(f"[NVDA Init Fehler]: {e}")
            print("[INFO] Fallback auf Konsolen-Ausgabe aktiv.")

        # Pygame Mixer für SFX
        try:
            pygame.mixer.init()
        except Exception:
            pass

    def speak(self, text, interrupt=True):
        """
        Text an NVDA senden. Fallback: Konsolen-Ausgabe.
        """
        print(f"[SPRACHE]: {text}")
        if self.speaker:
            try:
                self.speaker.speak(text, interrupt=interrupt)
            except Exception as e:
                print(f"[NVDA Fehler]: {e}")

    def play_sound(self, sound_name):
        """Spielt einen Sound-Effekt ab."""
        try:
            sound_path = f"assets/{sound_name}.wav"
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(0.3)
            sound.play()
        except Exception:
            pass

    def play_loop(self, sound_name):
        """Startet einen Sound in Endlosschleife."""
        try:
            sound_path = f"assets/{sound_name}.wav"
            self.current_loop = pygame.mixer.Sound(sound_path)
            self.current_loop.set_volume(0.2)
            self.current_loop.play(loops=-1)
        except Exception:
            self.current_loop = None

    def stop_loop(self):
        """Stoppt die aktuelle Schleife."""
        if hasattr(self, 'current_loop') and self.current_loop:
            self.current_loop.stop()
            self.current_loop = None

    def cleanup(self):
        """Ressourcen freigeben."""
        self.stop_loop()
        try:
            pygame.mixer.quit()
        except Exception:
            pass
