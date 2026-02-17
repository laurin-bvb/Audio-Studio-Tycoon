"""
Audio-Manager für Audio Studio Tycoon - Audio Edition.
Kommuniziert direkt mit NVDA über accessible_output2.
Nutzt pygame.mixer für Sound-Effekte.
"""

import pygame
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


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

        self.music_enabled = True
        self.current_loop = None

    def set_music_enabled(self, enabled):
        """Aktiviert oder deaktiviert Musik."""
        self.music_enabled = enabled
        if not enabled:
            self.stop_music()

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
        """Spielt einen Sound-Effekt ab (wav, ogg oder mp3)."""
        formats = ["wav", "ogg", "mp3"]
        for fmt in formats:
            try:
                sound_path = resource_path(f"assets/{sound_name}.{fmt}")
                if os.path.exists(sound_path):
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(0.15)
                    sound.play()
                    return
            except Exception:
                continue

    def play_loop(self, sound_name):
        """Startet einen Sound in Endlosschleife."""
        formats = ["wav", "ogg", "mp3"]
        for fmt in formats:
            try:
                sound_path = resource_path(f"assets/{sound_name}.{fmt}")
                if os.path.exists(sound_path):
                    self.current_loop = pygame.mixer.Sound(sound_path)
                    self.current_loop.set_volume(0.1)
                    self.current_loop.play(loops=-1)
                    return
            except Exception:
                continue
        self.current_loop = None

    def play_music(self, music_name):
        """Startet Hintergrundmusik über pygame.mixer.music."""
        if not self.music_enabled:
            return
        formats = ["mp3", "ogg", "wav"]
        for fmt in formats:
            try:
                music_path = resource_path(f"assets/{music_name}.{fmt}")
                if os.path.exists(music_path):
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.set_volume(0.05)
                    pygame.mixer.music.play(loops=-1)
                    return
            except Exception:
                continue

    def stop_music(self):
        """Stoppt die Hintergrundmusik."""
        pygame.mixer.music.stop()

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
