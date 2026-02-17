"""
Menüsystem für Audio Studio Tycoon - Audio Edition.

Alle Menüs sind vollständig über Tastatur bedienbar und
kommunizieren per NVDA mit dem Spieler.

Menü-Typen:
- Menu: Standard-Auswahl (Auf/Ab + Enter)
- TextInputMenu: Texteingabe (Buchstaben tippen, Backspace, Enter)
- SliderMenu: Slider-Verteilung (Auf/Ab = Slider, Links/Rechts = Wert)
"""

import pygame
import time
from models import GameProject, ReviewScore
from game_data import (
    TOPICS, GENRES, SLIDER_NAMES, PLATFORMS, AUDIENCES,
    OFFICE_LEVELS, ENGINE_FEATURES, GAME_SIZES, MARKETING_CAMPAIGNS,
    TRAINING_OPTIONS,
    get_compatibility, get_compatibility_text,
    get_available_platforms, get_available_features,
)
# logic.py: Spielzustand


# ============================================================
# BASIS-MENÜ
# ============================================================

class Menu:
    def __init__(self, title, options, audio, game_state):
        self.title = title
        self.options = options
        self.audio = audio
        self.game_state = game_state
        self.current_index = 0

    def speak_current(self, interrupt=True):
        if self.options:
            text = self.options[self.current_index]['text']
            pos = f"{self.current_index + 1} von {len(self.options)}"
            # TODO: Translate pos
            self.audio.speak(f"{text}. {pos}", interrupt=interrupt)

    def announce_entry(self):
        self.current_index = 0
        self.audio.speak(self.title)
        if self.options:
            self.speak_current(interrupt=False)

    def handle_input(self, event):
        if not self.options:
            return None
        if event.key == pygame.K_UP:
            self.current_index = (self.current_index - 1) % len(self.options)
            self.audio.play_sound("click")
            self.speak_current()
        elif event.key == pygame.K_DOWN:
            self.current_index = (self.current_index + 1) % len(self.options)
            self.audio.play_sound("click")
            self.speak_current()
        elif event.key == pygame.K_RETURN:
            self.audio.play_sound("confirm")
            action = self.options[self.current_index].get('action')
            if action:
                return action()
        return None

    def update(self):
        pass


# ============================================================
# TEXTEINGABE-MENÜ
# ============================================================

class TextInputMenu:
    def __init__(self, title, prompt, audio, game_state, on_confirm, on_cancel):
        self.title = title
        self.prompt = prompt
        self.audio = audio
        self.game_state = game_state
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.text = ""

    def announce_entry(self):
        self.text = ""
        self.audio.speak(f"{self.title}. {self.prompt} Tippe den Namen und drücke Enter.")

    def handle_input(self, event):
        if event.key == pygame.K_RETURN:
            if self.text.strip():
                self.audio.play_sound("confirm")
                self.audio.speak(f"Bestätigt: {self.text}")
                return self.on_confirm(self.text.strip())
            else:
                self.audio.speak("Bitte gib einen Namen ein.")
        elif event.key == pygame.K_BACKSPACE:
            if self.text:
                removed = self.text[-1]
                self.text = self.text[:-1]
                remaining = self.text if self.text else "leer"
                self.audio.speak(f"{removed} gelöscht. Aktuell: {remaining}")
            else:
                self.audio.speak("Eingabe ist leer.")
        elif event.key == pygame.K_ESCAPE:
            return self.on_cancel()
        elif event.unicode and event.unicode.isprintable() and len(event.unicode) == 1:
            self.text += event.unicode
            self.audio.speak(event.unicode)
        return None

    def update(self):
        pass


# ============================================================
# EINSTELLUNGEN-MENÜ
# ============================================================

class SettingsMenu:
    def __init__(self, audio, game_state, on_back):
        self.audio = audio
        self.game_state = game_state
        self.on_back = on_back
        self.current_index = 0
        self.options = []
        self._update_options()

    def _update_options(self):
        s = self.game_state.settings
        lang_name = "Deutsch" if s['language'] == 'de' else "English"
        music_status = self.game_state.get_text('on') if s['music_enabled'] else self.game_state.get_text('off')

        self.options = [
            {'text': f"{self.game_state.get_text('music')}: {music_status}", 'action': self._toggle_music},
            {'text': f"{self.game_state.get_text('language')}: {lang_name}", 'action': self._toggle_language},
            {'text': self.game_state.get_text('back'), 'action': self.on_back}
        ]

    def _toggle_music(self):
        self.game_state.settings['music_enabled'] = not self.game_state.settings['music_enabled']
        self.audio.set_music_enabled(self.game_state.settings['music_enabled'])
        if self.game_state.settings['music_enabled']:
            self.audio.play_music("music_back")
        self._update_options()
        self.speak_current()

    def _toggle_language(self):
        new_lang = 'en' if self.game_state.settings['language'] == 'de' else 'de'
        self.game_state.settings['language'] = new_lang
        self._update_options()
        self.audio.speak(self.game_state.get_text('language'))
        self.speak_current()

    def speak_current(self, interrupt=True):
        text = self.options[self.current_index]['text']
        self.audio.speak(text, interrupt=interrupt)

    def announce_entry(self):
        self.current_index = 0
        self.audio.speak(self.game_state.get_text('settings_menu'))
        self.speak_current(interrupt=False)

    def handle_input(self, event):
        if event.key == pygame.K_UP:
            self.current_index = (self.current_index - 1) % len(self.options)
            self.audio.play_sound("click")
            self.speak_current()
        elif event.key == pygame.K_DOWN:
            self.current_index = (self.current_index + 1) % len(self.options)
            self.audio.play_sound("click")
            self.speak_current()
        elif event.key == pygame.K_RETURN:
            self.audio.play_sound("confirm")
            return self.options[self.current_index]['action']()
        elif event.key == pygame.K_ESCAPE:
            return self.on_back()
        return None

    def update(self):
        pass


# ============================================================
# SLIDER-MENÜ
# ============================================================

class SliderMenu:
    def __init__(self, title, audio, game_state, slider_names, budget, on_confirm, on_cancel):
        self.title = title
        self.audio = audio
        self.game_state = game_state
        self.slider_names = slider_names
        self.budget = budget
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.values = {name: 0 for name in slider_names}
        self.current_index = 0
        self._enter_warned = False

    @property
    def remaining(self):
        return self.budget - sum(self.values.values())

    def announce_entry(self):
        self.values = {name: 0 for name in self.slider_names}
        self.current_index = 0
        self._enter_warned = False
        self.audio.speak(
            f"{self.title}. "
            f"Verteile {self.budget} Punkte auf {len(self.slider_names)} Bereiche. "
            f"Auf und Ab zum Wechseln. Links und Rechts zum Ändern. "
            f"Enter zum Bestätigen."
        )
        self._speak_current()

    def _speak_current(self):
        name = self.slider_names[self.current_index]
        val = self.values[name]
        self.audio.speak(
            f"{name}: {val} von 10. "
            f"Verbleibend: {self.remaining} Punkte. "
            f"Slider {self.current_index + 1} von {len(self.slider_names)}.",
            interrupt=True
        )

    def handle_input(self, event):
        if event.key == pygame.K_UP:
            self.current_index = (self.current_index - 1) % len(self.slider_names)
            self._speak_current()
        elif event.key == pygame.K_DOWN:
            self.current_index = (self.current_index + 1) % len(self.slider_names)
            self._speak_current()
        elif event.key == pygame.K_RIGHT:
            name = self.slider_names[self.current_index]
            if self.values[name] < 10 and self.remaining > 0:
                self.values[name] += 1
                self.audio.play_sound("click")
                self._speak_current()
            elif self.remaining <= 0:
                self.audio.play_sound("error")
                self.audio.speak("Keine Punkte mehr übrig.")
            else:
                self.audio.play_sound("error")
                self.audio.speak("Maximum erreicht.")
        elif event.key == pygame.K_LEFT:
            name = self.slider_names[self.current_index]
            if self.values[name] > 0:
                self.values[name] -= 1
                self.audio.play_sound("click")
                self._speak_current()
            else:
                self.audio.play_sound("error")
                self.audio.speak("Bereits auf Null.")
        elif event.key == pygame.K_RETURN:
            if self.remaining > 0:
                if hasattr(self, '_enter_warned') and self._enter_warned:
                    self.audio.play_sound("confirm")
                    return self.on_confirm(dict(self.values))
                self.audio.play_sound("error")
                self.audio.speak(f"Noch {self.remaining} Punkte übrig. Nochmal Enter zum Bestätigen.")
                self._enter_warned = True
            else:
                self.audio.play_sound("confirm")
                return self.on_confirm(dict(self.values))
        elif event.key == pygame.K_ESCAPE:
            return self.on_cancel()

        if event.key != pygame.K_RETURN:
            self._enter_warned = False
        return None

    def update(self):
        pass


# ============================================================
# HAUPTMENÜ
# ============================================================

class MainMenu(Menu):
    def __init__(self, audio, game_state):
        self.game_state = game_state
        options = [
            {'text': game_state.get_text('start_new_game'), 'action': self.new_game},
            {'text': game_state.get_text('load_game'), 'action': self.load_game},
            {'text': game_state.get_text('settings'), 'action': self.goto_settings},
            {'text': game_state.get_text('quit'), 'action': self.quit_game},
        ]
        super().__init__(game_state.get_text('main_menu'), options, audio, game_state)

    def goto_settings(self):
        return "settings_menu"

    def new_game(self):
        self.audio.speak("Neues Spiel wird gestartet...")
        return "company_name_input"

    def load_game(self):
        return "load_menu"

    def quit_game(self):
        self.audio.speak(self.game_state.get_text('goodbye'))
        return "quit"


# ============================================================
# FIRMENGRÜNDUNG
# ============================================================

class CompanyNameMenu(TextInputMenu):
    def __init__(self, audio, game_state):
        super().__init__(
            title="Firmengründung", # TODO: Translate
            prompt=game_state.get_text('company_name_prompt'),
            audio=audio,
            game_state=game_state,
            on_confirm=self._confirm,
            on_cancel=self._cancel,
        )

    def _confirm(self, name):
        self.game_state.company_name = name
        self.audio.speak(
            f"Willkommen bei {name}! "
            f"Du hast {self.game_state.money:,} Euro Startkapital. "
            f"Du startest in einer Garage. "
            f"Zeit, dein erstes Spiel zu entwickeln!"
        )
        return "game_menu"

    def _cancel(self):
        return "main_menu"


# ============================================================
# MANAGEMENT-ZENTRALE (Hauptspiel-Menü)
# ============================================================

class GameMenu(Menu):
    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        options = [
            {'text': game_state.get_text('company_overview'), 'action': self.show_status},
            {'text': game_state.get_text('develop_new_game'), 'action': self.new_game},
            {'text': game_state.get_text('hr_department'), 'action': self.goto_hr},
            {'text': game_state.get_text('research_engines'), 'action': self.goto_research},
            {'text': game_state.get_text('service_support'), 'action': self.goto_service},
            {'text': game_state.get_text('inbox'), 'action': self.goto_inbox},
            {'text': game_state.get_text('upgrade_office'), 'action': self.goto_office},
            {'text': game_state.get_text('history'), 'action': self.show_history},
            {'text': game_state.get_text('save_game'), 'action': self.goto_save},
            {'text': game_state.get_text('wiki'), 'action': self.goto_help},
            {'text': game_state.get_text('settings'), 'action': self.goto_settings},
            {'text': game_state.get_text('quit'), 'action': self.quit_game_to_main},
        ]
        super().__init__(game_state.get_text('management_center'), options, audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        # Zufallsereignis prüfen
        event = self.game_state.check_random_event()
        if event:
            self.audio.speak(
                f"Ereignis: {event['title']}! {event['text']}"
            )
        self.audio.speak(
            f"{self.game_state.get_text('management_center')} - {self.game_state.company_name}. "
            f"{self.game_state.get_text('week')} {self.game_state.week}.",
            interrupt=False
        )
        self.speak_current(interrupt=False)

    def goto_service(self):
        return "service_menu"

    def goto_inbox(self):
        return "email_inbox"

    def show_status(self):
        self.audio.speak(self.game_state.get_status_text())
        return None

    def new_game(self):
        self.game_state.reset_draft()
        return "topic_menu"

    def goto_hr(self):
        return "hr_menu"

    def goto_research(self):
        return "research_menu"

    def goto_office(self):
        return "office_menu"

    def goto_settings(self):
        return "settings_menu_ingame"

    def show_history(self):
        if not self.game_state.game_history:
            self.audio.speak(self.game_state.get_text('history') + ": Leer.")
            return None
        self.audio.speak(f"{self.game_state.get_text('history')}: {len(self.game_state.game_history)}.")
        for i, game in enumerate(self.game_state.game_history[-5:], 1):
            self.audio.speak(f"{i}. {game.summary()}", interrupt=False)
        return None

    def goto_save(self):
        return "save_menu"

    def goto_help(self):
        return "help_menu"

    def quit_game_to_main(self):
        self.audio.speak(self.game_state.get_text('goodbye'))
        return "main_menu"


# ============================================================
# SPIELENTWICKLUNG: THEMA → GENRE → PLATTFORM → ZIELGRUPPE → ENGINE → NAME → SLIDER → REVIEW
# ============================================================

class TopicMenu(Menu):
    def __init__(self, audio, game_state):
        options = []
        for topic in TOPICS:
            options.append({'text': topic, 'action': lambda t=topic: self._select(t)})
        options.append({'text': game_state.get_text('back'), 'action': self._cancel})
        super().__init__(game_state.get_text('select_topic'), options, audio, game_state)

    def _select(self, topic):
        self.game_state.current_draft['topic'] = topic
        self.audio.speak(f"Thema: {topic}")
        return "genre_menu"

    def _cancel(self):
        return "game_menu"


class GenreMenu(Menu):
    def __init__(self, audio, game_state):
        options = []
        for genre in GENRES:
            options.append({'text': genre, 'action': lambda g=genre: self._select(g)})
        options.append({'text': game_state.get_text('back'), 'action': self._cancel})
        super().__init__(game_state.get_text('select_genre'), options, audio, game_state)

    def announce_entry(self):
        topic = self.game_state.current_draft.get('topic', '?')
        self.current_index = 0
        self.audio.speak(f"Wähle ein Genre für dein {topic}-Spiel.")
        self.speak_current(interrupt=False)

    def _select(self, genre):
        topic = self.game_state.current_draft.get('topic', '?')
        self.game_state.current_draft['genre'] = genre
        compat = get_compatibility(topic, genre)
        compat_text = get_compatibility_text(compat)
        self.audio.speak(f"{topic} plus {genre}: {compat_text}.")
        return "platform_menu"

    def _cancel(self):
        return "topic_menu"


class PlatformMenu(Menu):
    """Plattform-Auswahl basierend auf verfügbaren Plattformen."""

    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        # Wird in announce_entry dynamisch befüllt
        super().__init__("Wähle eine Plattform", [], audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        available = get_available_platforms(self.game_state.week)
        self.options = []
        for p in available:
            fee = p['license_fee']
            fee_text = f" (Lizenz: {fee:,} {self.game_state.get_text('money_unit')})" if fee > 0 else ""
            
            def select_action(pn=p['name'], cost=fee):
                if self.game_state.money < cost:
                    # TODO: Translate
                    self.audio.speak(f"Nicht genug Geld für die {pn} Lizenz. Du brauchst {cost:,} {self.game_state.get_text('money_unit')}.")
                    return None
                return self._select(pn)

            self.options.append({
                'text': f"{p['name']}{fee_text}",
                'action': select_action,
            })
        self.options.append({'text': self.game_state.get_text('back'), 'action': self._cancel})
        self.audio.speak(self.game_state.get_text('select_platform'))
        self.speak_current(interrupt=False)

    def _select(self, platform_name):
        self.game_state.current_draft['platform'] = platform_name
        self.audio.speak(f"Plattform: {platform_name}.")
        return "audience_menu"

    def _cancel(self):
        return "genre_menu"


class AudienceMenu(Menu):
    """Zielgruppen-Auswahl."""

    def __init__(self, audio, game_state):
        options = []
        for a in AUDIENCES:
            options.append({'text': a, 'action': lambda au=a: self._select(au)})
        options.append({'text': game_state.get_text('back'), 'action': self._cancel})
        super().__init__(game_state.get_text('select_audience'), options, audio, game_state)

    def _select(self, audience):
        self.game_state.current_draft['audience'] = audience
        self.audio.speak(f"Zielgruppe: {audience}.")
        return "game_size_menu"

    def _cancel(self):
        return "platform_menu"


class GameSizeMenu(Menu):
    """Auswahl der Spielgröße (Klein, Mittel, Groß, AAA)."""

    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        options = []
        for size in GAME_SIZES:
            options.append({
                'text': f"{size['name']} - {size['description']}",
                'action': lambda s=size: self._select(s)
            })
        options.append({'text': game_state.get_text('back'), 'action': self._cancel})
        super().__init__(game_state.get_text('select_size'), options, audio, game_state)

    def _select(self, size_data):
        # Check min employees
        if len(self.game_state.employees) < size_data['min_employees']:
            self.audio.speak(
                f"Für ein {size_data['name']} Spiel brauchst du mindestens "
                f"{size_data['min_employees']} Mitarbeiter. Du hast nur {len(self.game_state.employees)}."
            )
            return None
        
        self.game_state.current_draft['size'] = size_data['name']
        self.audio.speak(f"Größe: {size_data['name']}.")
        return "marketing_menu"

    def _cancel(self):
        return "audience_menu"


class MarketingMenu(Menu):
    """Auswahl der Marketing-Kampagne."""

    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        options = []
        for mark in MARKETING_CAMPAIGNS:
            options.append({
                'text': f"{mark['name']} - {mark['description']}",
                'action': lambda m=mark: self._select(m)
            })
        options.append({'text': game_state.get_text('back'), 'action': self._cancel})
        super().__init__(game_state.get_text('marketing'), options, audio, game_state)

    def _select(self, mark_data):
        if self.game_state.money < mark_data['cost']:
            self.audio.speak(f"Nicht genug Geld für {mark_data['name']}. Du brauchst {mark_data['cost']:,} Euro.")
            return None
            
        self.game_state.current_draft['marketing'] = mark_data['name']
        self.audio.speak(f"Marketing: {mark_data['name']}.")
        return "engine_select_menu"

    def _cancel(self):
        return "game_size_menu"


class EngineSelectMenu(Menu):
    """Engine-Auswahl aus vorhandenen Engines."""

    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        super().__init__(game_state.get_text('select_engine'), [], audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        self.options = []
        for eng in self.game_state.engines:
            self.options.append({
                'text': f"{eng.name}, Tech-Level {eng.tech_level}",
                'action': lambda e=eng: self._select(e),
            })
        self.options.append({'text': self.game_state.get_text('back'), 'action': self._cancel})
        self.audio.speak(self.game_state.get_text('select_engine'))
        self.speak_current(interrupt=False)

    def _select(self, engine):
        self.game_state.current_draft['engine'] = engine
        self.audio.speak(f"Engine: {engine.name}, Tech-Level {engine.tech_level}.")
        return "game_name_input"

    def _cancel(self):
        return "marketing_menu"


class GameNameMenu(TextInputMenu):
    def __init__(self, audio, game_state):
        super().__init__(
            title=game_state.get_text('game_name'),
            prompt=game_state.get_text('game_name_prompt_short'), # I'll add this to translations
            audio=audio,
            game_state=game_state,
            on_confirm=self._confirm,
            on_cancel=self._cancel,
        )

    def announce_entry(self):
        self.text = ""
        d = self.game_state.current_draft
        self.audio.speak(
            f"Spielname eingeben. Dein {d.get('topic','?')} {d.get('genre','?')}-Spiel "
            f"auf {d.get('platform','?')}. Tippe den Namen und drücke Enter."
        )

    def _confirm(self, name):
        self.game_state.current_draft['name'] = name
        self.audio.speak(f"Spielname: {name}. Weiter zur Entwicklung!")
        return "slider_menu"

    def _cancel(self):
        return "engine_select_menu"


class DevelopmentSliderMenu(SliderMenu):
    def __init__(self, audio, game_state):
        super().__init__(
            title=game_state.get_text('dev_progress'),
            audio=audio,
            game_state=game_state,
            slider_names=SLIDER_NAMES,
            budget=30,
            on_confirm=self._confirm,
            on_cancel=self._cancel,
        )

    def announce_entry(self):
        self.values = {name: 0 for name in self.slider_names}
        self.current_index = 0
        self._enter_warned = False

        d = self.game_state.current_draft
        dummy = type('Dummy', (), {
            'platform': d.get('platform', 'PC'),
            'audience': d.get('audience', 'Jugendliche'),
            'size': d.get('size', 'Mittel'),
            'marketing': d.get('marketing', 'Kein Marketing')
        })()
        cost = self.game_state.calculate_dev_cost(dummy)

        self.audio.speak(
            f"Entwicklung von '{d.get('name','?')}', "
            f"ein {d.get('topic','?')} {d.get('genre','?')}-Spiel "
            f"auf {d.get('platform','?')}. "
            f"Geschätzte Kosten: {cost:,} Euro. "
            f"Verteile {self.budget} Punkte auf 6 Bereiche."
        )
        self._speak_current()

    def _confirm(self, values):
        self.game_state.current_draft['sliders'] = values

        # Entwicklungsfortschritt anzeigen
        self.audio.speak(
            "Entwicklung läuft... Dein Team arbeitet hart!"
        )
        return "dev_progress_menu"

    def _cancel(self):
        return "game_name_input"


class DevProgressMenu:
    """Zeigt Entwicklungsfortschritt in Phasen."""

    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        self.phase_index = 0
        self.start_time = 0.0
        self.completed = False
        self.phases = []

    def announce_entry(self):
        from game_data import DEV_PHASES
        self.phases = DEV_PHASES
        self.phase_index = 0
        self.start_time = time.time()
        self.completed = False
        self.audio.speak(
            f"Phase 1 von {len(self.phases)}: {self.phases[0]['name']}..."
        )

    def update(self):
        if self.completed:
            return
        from game_data import DEV_PHASES
        elapsed = time.time() - self.start_time
        phase_duration = 1.5  # Sekunden pro Phase

        if elapsed >= phase_duration:
            self.phase_index += 1
            self.start_time = time.time()

            if self.phase_index >= len(DEV_PHASES):
                self.completed = True
                self.audio.speak(
                    self.game_state.get_text('dev_completed')
                )
            else:
                phase = DEV_PHASES[self.phase_index]
                # Phase name might be in game_data, still hardcoded there?
                self.audio.speak(
                    f"Phase {self.phase_index+1} von {len(DEV_PHASES)}: {phase['name']}..."
                )

    def handle_input(self, event):
        if self.completed and event.key == pygame.K_RETURN:
            return "review_result"
        return None


# ============================================================
# REVIEW-ERGEBNIS
# ============================================================

class ReviewResultMenu(Menu):
    def __init__(self, audio, game_state):
        options = [
            {'text': game_state.get_text('back'), 'action': self._continue},
            {'text': game_state.get_text('quit'), 'action': self._quit},
        ]
        super().__init__(game_state.get_text('review_result'), options, audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        from models import GameProject

        d = self.game_state.current_draft
        project = GameProject(
            name=d['name'], topic=d['topic'], genre=d['genre'],
            sliders=d['sliders'], platform=d.get('platform', 'PC'),
            audience=d.get('audience', 'Jugendliche'),
            engine=d.get('engine'),
            size=d.get('size', 'Mittel'),
            marketing=d.get('marketing', 'Kein Marketing')
        )

        project = self.game_state.finalize_game(project)

        self.audio.speak(f"Die Reviews für '{project.name}' sind da!")

        for i, score in enumerate(project.review.scores):
            self.audio.speak(f"Reviewer {i+1}: {score} von 10.", interrupt=False)

        self.audio.speak(
            f"Durchschnittsbewertung: {project.review.average:.1f} von 10.",
            interrupt=False,
        )
        # NEU: Detaillierte Berichte sprechen
        for comment in project.review.comments:
            self.audio.speak(comment, interrupt=False)
        self.audio.play_sound("cash")
        self.audio.speak(
            f"Verkäufe: {project.sales:,} Einheiten. "
            f"Einnahmen: {project.revenue:,} Euro. "
            f"Kosten: {project.dev_cost:,} Euro. "
            f"Gewinn: {project.profit:,} Euro.",
            interrupt=False,
        )
        self.audio.speak(
            f"Neuer Kontostand: {self.game_state.money:,} Euro. "
            f"Fans: {self.game_state.fans:,}.",
            interrupt=False,
        )
        self.speak_current(interrupt=False)

    def _continue(self):
        self.game_state.reset_draft()
        return "game_menu"

    def _quit(self):
        self.game_state.save_game()
        self.audio.speak("Spielstand gespeichert. Auf Wiedersehen!")
        return "quit"


# ============================================================
# PERSONAL-ABTEILUNG
# ============================================================

class HRMenu(Menu):
    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        options = [
            {'text': game_state.get_text('hire_employee'), 'action': self.hire},
            {'text': game_state.get_text('show_employees'), 'action': self.show_employees},
            {'text': game_state.get_text('train_employee'), 'action': self.train},
            {'text': game_state.get_text('fire_employee'), 'action': self.fire},
            {'text': game_state.get_text('back'), 'action': self.back},
        ]
        super().__init__(game_state.get_text('hr_department'), options, audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        gs = self.game_state
        max_emp = gs.get_max_employees()
        self.audio.speak(
            f"Personal-Abteilung. "
            f"{len(gs.employees)} von {max_emp} Mitarbeiter."
        )
        self.speak_current(interrupt=False)

    def hire(self):
        if not self.game_state.can_hire():
            office = OFFICE_LEVELS[self.game_state.office_level]
            self.audio.speak(
                f"Dein {office['name']} hat nur Platz für {office['max_employees']} Mitarbeiter. "
                f"Upgrade dein Büro für mehr Plätze."
            )
            return None
        return "hire_menu"

    def show_employees(self):
        if not self.game_state.employees:
            self.audio.speak("Du hast noch keine Mitarbeiter.")
            return None
        for i, emp in enumerate(self.game_state.employees, 1):
            self.audio.speak(f"{i}. {emp.detail()}", interrupt=False)
        return None

    def train(self):
        if not self.game_state.employees:
            self.audio.speak("Du hast keine Mitarbeiter zum Trainieren.")
            return None
        return "training_employee_select"

    def fire(self):
        if not self.game_state.employees:
            self.audio.speak("Du hast keine Mitarbeiter zum Entlassen.")
            return None
        return "fire_menu"

    def back(self):
        return "game_menu"


class HireMenu(Menu):
    """Zeigt 3 zufällige Bewerber."""

    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        self.candidates = []
        super().__init__(game_state.get_text('candidates'), [], audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        self.candidates = [self.game_state.generate_candidate() for _ in range(3)]
        self.options = []
        for c in self.candidates:
            hire_cost = c.salary * 2
            spec_text = f" Spezialisierung: {c.specialization['name']}." if c.specialization else ""
            self.options.append({
                'text': f"{c.name}, {c.role}, Level {c.skill_level}. "
                        f"Gehalt: {c.salary} pro Woche. {spec_text} Einstellung: {hire_cost:,} Euro",
                'action': lambda emp=c: self._hire(emp),
            })
        self.options.append({'text': self.game_state.get_text('refresh_candidates'), 'action': self._refresh})
        self.options.append({'text': self.game_state.get_text('back'), 'action': self._cancel})

        self.audio.speak("3 Bewerber verfügbar.")
        self.speak_current(interrupt=False)

    def _hire(self, emp):
        hire_cost = emp.salary * 2
        if self.game_state.money < hire_cost:
            self.audio.speak(f"Nicht genug Geld. Du brauchst {hire_cost:,} Euro.")
            return None
        if self.game_state.hire_employee(emp):
            self.audio.speak(
                f"{emp.name} eingestellt! "
                f"Kosten: {hire_cost:,} Euro. "
                f"Restgeld: {self.game_state.money:,} Euro."
            )
            return "hr_menu"
        self.audio.speak("Einstellung fehlgeschlagen.")
        return None

    def _refresh(self):
        return "hire_menu"

    def _cancel(self):
        return "hr_menu"


class FireMenu(Menu):
    """Zeigt aktuelle Mitarbeiter zum Entlassen."""

    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        super().__init__(game_state.get_text('fire_employee'), [], audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        self.options = []
        for i, emp in enumerate(self.game_state.employees):
            abfindung = emp.salary * 4
            self.options.append({
                'text': f"{emp.name}, {emp.role}. Abfindung: {abfindung:,} Euro",
                'action': lambda idx=i: self._fire(idx),
            })
        self.options.append({'text': self.game_state.get_text('back'), 'action': self._cancel})
        self.audio.speak("Wen möchtest du entlassen?")
        self.speak_current(interrupt=False)

    def _fire(self, index):
        emp = self.game_state.fire_employee(index)
        if emp:
            self.audio.speak(
                f"{emp.name} entlassen. "
                f"Restgeld: {self.game_state.money:,} Euro."
            )
        return "hr_menu"

    def _cancel(self):
        return "hr_menu"


# ============================================================
# FORSCHUNG & ENGINE
# ============================================================

class ResearchMenu(Menu):
    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        options = [
            {'text': game_state.get_text('research_feature'), 'action': self.research},
            {'text': game_state.get_text('create_engine_option'), 'action': self.create_engine},
            {'text': game_state.get_text('show_engines_option'), 'action': self.show_engines},
            {'text': game_state.get_text('back'), 'action': self.back},
        ]
        super().__init__(game_state.get_text('research_engines'), options, audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        researchable = self.game_state.get_researchable_features()
        self.audio.speak(
            f"Forschung und Engines. "
            f"{len(self.game_state.unlocked_features)} Features freigeschaltet. "
            f"{len(researchable)} neue Features verfügbar. "
            f"{len(self.game_state.engines)} Engines erstellt."
        )
        self.speak_current(interrupt=False)

    def research(self):
        return "feature_research_menu"

    def create_engine(self):
        return "engine_create_name"

    def show_engines(self):
        for eng in self.game_state.engines:
            self.audio.speak(eng.summary(), interrupt=False)
        return None

    def back(self):
        return "game_menu"


class FeatureResearchMenu(Menu):
    """Zeigt erforschbare Features."""

    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        super().__init__(game_state.get_text('research_feature'), [], audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        researchable = self.game_state.get_researchable_features()
        self.options = []
        for f in researchable:
            self.options.append({
                'text': f"{f['name']} ({f['category']}). Kosten: {f['cost']:,} Euro. Tech-Bonus: +{f['tech_bonus']}",
                'action': lambda fd=f: self._research(fd),
            })
        if not self.options:
            self.options.append({'text': self.game_state.get_text('no_features_available'), 'action': lambda: None})
        self.options.append({'text': self.game_state.get_text('back'), 'action': self._cancel})

        self.audio.speak(f"{len(researchable)} Features zum Erforschen.")
        self.speak_current(interrupt=False)

    def _research(self, feature_data):
        if self.game_state.research_feature(feature_data):
            self.audio.speak(
                f"{feature_data['name']} erforscht! "
                f"Restgeld: {self.game_state.money:,} Euro."
            )
            return "research_menu"
        else:
            self.audio.speak("Nicht genug Geld oder bereits erforscht.")
            return None

    def _cancel(self):
        return "research_menu"


class EngineCreateNameMenu(TextInputMenu):
    """Name für neue Engine eingeben."""

    def __init__(self, audio, game_state):
        super().__init__(
            title=game_state.get_text('create_engine_option'),
            prompt=game_state.get_text('engine_name_prompt'),
            audio=audio,
            game_state=game_state,
            on_confirm=self._confirm,
            on_cancel=self._cancel,
        )
        self._engine_name = ""

    def _confirm(self, name):
        self._engine_name = name
        self.game_state._pending_engine_name = name
        return "engine_feature_select"

    def _cancel(self):
        return "research_menu"


class EngineFeatureSelectMenu(Menu):
    """Features für die neue Engine auswählen (Toggle-basiert)."""

    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        self.selected_features = []
        super().__init__(game_state.get_text('select_engine_features'), [], audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        self.selected_features = []
        self.options = []

        # Gruppieren nach Kategorie, nur freigeschaltete
        categories = {}
        for f in self.game_state.unlocked_features:
            categories.setdefault(f.category, []).append(f)

        # Bestes Feature pro Kategorie anzeigen
        for cat, features in sorted(categories.items()):
            best = max(features, key=lambda x: x.tech_bonus)
            self.options.append({
                'text': f"[  ] {best.name} ({cat}, Tech: +{best.tech_bonus})",
                'action': lambda feat=best: self._toggle(feat),
                '_feature': best,
                '_selected': False,
            })

        self.options.append({'text': self.game_state.get_text('create_engine_option'), 'action': self._create})
        self.options.append({'text': self.game_state.get_text('back'), 'action': self._cancel})

        name = getattr(self.game_state, '_pending_engine_name', 'Neue Engine')
        self.audio.speak(
            f"Wähle Features für '{name}'. "
            f"Enter zum An/Abwählen. Letzte Option zum Erstellen."
        )
        self.speak_current(interrupt=False)

    def _toggle(self, feature):
        if feature in self.selected_features:
            self.selected_features.remove(feature)
            status = "abgewählt"
        else:
            self.selected_features.append(feature)
            status = "ausgewählt"

        # Update option text
        for opt in self.options:
            if opt.get('_feature') == feature:
                mark = "[X]" if feature in self.selected_features else "[  ]"
                opt['text'] = f"{mark} {feature.name} ({feature.category}, Tech: +{feature.tech_bonus})"
                break

        self.audio.speak(
            f"{feature.name} {status}. {len(self.selected_features)} Features gewählt."
        )
        return None

    def _create(self):
        if not self.selected_features:
            self.audio.speak("Wähle mindestens ein Feature!")
            return None

        name = getattr(self.game_state, '_pending_engine_name', 'Neue Engine')
        engine = self.game_state.create_engine(name, list(self.selected_features))
        self.audio.speak(
            f"Engine '{engine.name}' erstellt! Tech-Level: {engine.tech_level}."
        )
        return "research_menu"

    def _cancel(self):
        return "research_menu"


# ============================================================
# BÜRO
# ============================================================

class OfficeMenu(Menu):
    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        options = [
            {'text': game_state.get_text('upgrade_office'), 'action': self.upgrade},
            {'text': game_state.get_text('back'), 'action': self.back},
        ]
        super().__init__(game_state.get_text('office_management'), options, audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        office = self.game_state.get_office_info()
        self.audio.speak(
            f"Aktuelles Büro: {office['name']}. "
            f"Platz für {office['max_employees']} Mitarbeiter."
        )
        if self.game_state.office_level < len(OFFICE_LEVELS) - 1:
            next_office = OFFICE_LEVELS[self.game_state.office_level + 1]
            self.audio.speak(
                f"Nächstes Upgrade: {next_office['name']} für {next_office['cost']:,} Euro. "
                f"Platz für {next_office['max_employees']} Mitarbeiter.",
                interrupt=False
            )
        else:
            self.audio.speak("Maximale Bürogröße erreicht!", interrupt=False)
        self.speak_current(interrupt=False)

    def upgrade(self):
        if self.game_state.upgrade_office():
            office = self.game_state.get_office_info()
            self.audio.speak(
                f"Upgrade auf {office['name']}! "
                f"Platz für {office['max_employees']} Mitarbeiter. "
                f"Restgeld: {self.game_state.money:,} Euro."
            )
        elif self.game_state.office_level >= len(OFFICE_LEVELS) - 1:
            self.audio.speak("Maximale Bürogröße erreicht!")
        else:
            next_cost = OFFICE_LEVELS[self.game_state.office_level + 1]['cost']
            self.audio.speak(f"Nicht genug Geld. Du brauchst {next_cost:,} Euro.")
        return None

    def back(self):
        return "game_menu"


# ============================================================
# TRAINING-MENÜS
# ============================================================

class TrainingEmployeeSelectMenu(Menu):
    """Wähle einen Mitarbeiter für das Training."""

    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        super().__init__(game_state.get_text('select_employee_training'), [], audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        self.options = []
        for i, emp in enumerate(self.game_state.employees):
            self.options.append({
                'text': f"{emp.name} ({emp.role})",
                'action': lambda idx=i: self._select(idx)
            })
        self.options.append({'text': "Abbrechen", 'action': lambda: "hr_menu"})
        self.audio.speak("Wähle einen Mitarbeiter zum Trainieren.")
        self.speak_current(interrupt=False)

    def _select(self, index):
        self.game_state._pending_train_emp_index = index
        return "training_option_select"


class TrainingOptionMenu(Menu):
    """Wähle eine Trainings-Option."""

    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        super().__init__(game_state.get_text('select_training'), [], audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        emp_idx = getattr(self.game_state, '_pending_train_emp_index', 0)
        emp = self.game_state.employees[emp_idx]
        
        self.options = []
        for train in TRAINING_OPTIONS:
            self.options.append({
                'text': f"{train['name']} - {train['description']} (Kosten: {train['cost']:,} Euro)",
                'action': lambda t=train: self._train(emp_idx, t)
            })
        self.options.append({'text': "Abbrechen", 'action': lambda: "hr_menu"})
        self.audio.speak(f"Training für {emp.name} wählen.")
        self.speak_current(interrupt=False)

    def _train(self, emp_idx, train_data):
        if self.game_state.train_employee(emp_idx, train_data):
            emp = self.game_state.employees[emp_idx]
            self.audio.speak(
                f"Training erfolgreich! {emp.name} hat sich verbessert. "
                f"Neues Gehalt: {emp.salary} Euro. Restgeld: {self.game_state.money:,} Euro."
            )
            return "hr_menu"
        else:
            self.audio.speak(f"Nicht genug Geld. Du brauchst {train_data['cost']:,} Euro.")
            return None


# ============================================================
# PLEITE-MENÜ
# ============================================================

class BankruptcyMenu(Menu):
    def __init__(self, audio, game_state):
        options = [
            {'text': "Zurück zum Hauptmenü", 'action': lambda: "main_menu"},
            {'text': "Spiel beenden", 'action': lambda: "quit"},
        ]
        super().__init__(game_state.get_text('bankruptcy'), options, audio, game_state)

    def announce_entry(self):
        self.audio.speak(
            "Deine Firma ist pleite! Du hast zu viele Schulden und die Bank hat dein Studio geschlossen. "
            "Das Spiel ist vorbei."
        )


# ============================================================
# NEU: E-MAIL & SERVICE
# ============================================================

class EmailInboxMenu(Menu):
    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        super().__init__("Posteingang", [], audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        self.options = []
        for i, mail in enumerate(self.game_state.emails):
            status = "" if mail.is_read else "[NEU] "
            self.options.append({
                'text': f"{status}{mail.subject} (Woche {mail.date_week})",
                'action': lambda idx=i: self._read_mail(idx)
            })
        self.options.append({'text': "Zurück", 'action': lambda: "game_menu"})
        
        unread = len([m for m in self.game_state.emails if not m.is_read])
        self.audio.speak(f"Posteingang. {len(self.game_state.emails)} E-Mails, {unread} ungelesen.")
        self.speak_current(interrupt=False)

    def _read_mail(self, index):
        self.game_state._pending_email_index = index
        return "email_detail"


class EmailDetailMenu(Menu):
    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        super().__init__(game_state.get_text('email_details'), [], audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        idx = getattr(self.game_state, '_pending_email_index', 0)
        mail = self.game_state.emails[idx]
        mail.is_read = True
        
        self.options = [
            {'text': self.game_state.get_text('reply_ok'), 'action': lambda: "email_inbox"},
            {'text': self.game_state.get_text('delete'), 'action': lambda: self._delete(idx)}
        ]
        
        self.audio.speak(f"Von: {mail.sender}. Betreff: {mail.subject}.")
        self.audio.speak(mail.body, interrupt=False)
        self.speak_current(interrupt=False)

    def _delete(self, index):
        self.game_state.emails.pop(index)
        return "email_inbox"


class ServiceMenu(Menu):
    """Management von Patches und DLCs."""
    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        super().__init__(game_state.get_text('service_support'), [], audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        self.options = []
        # Nur aktive oder verbuggte Spiele
        for i, game in enumerate(self.game_state.game_history):
            if game.is_active or game.bugs > 0:
                self.options.append({
                    'text': f"{game.name} ({game.bugs} Bugs, {game.dlc_count} DLCs)",
                    'action': lambda idx=i: self._manage_game(idx)
                })
        
        self.options.append({'text': "Zurück", 'action': lambda: "game_menu"})
        self.audio.speak("Service und Support. Wähle ein Spiel zum Bearbeiten.")
        self.speak_current(interrupt=False)

    def _manage_game(self, index):
        self.game_state._pending_service_game_index = index
        return "game_service_options"


class GameServiceOptionsMenu(Menu):
    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        super().__init__(game_state.get_text('update_options'), [], audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        idx = getattr(self.game_state, '_pending_service_game_index', 0)
        game = self.game_state.game_history[idx]
        
        self.options = [
            {'text': self.game_state.get_text('free_patch', bugs=game.bugs), 'action': lambda: self._patch(idx)},
            {'text': self.game_state.get_text('release_dlc_option'), 'action': lambda: self._dlc(idx)},
            {'text': self.game_state.get_text('back'), 'action': lambda: "service_menu"}
        ]
        self.audio.speak(f"Optionen für {game.name}.")
        self.speak_current(interrupt=False)

    def _patch(self, idx):
        if self.game_state.release_patch(idx):
            self.audio.speak("Patch veröffentlicht! Bugs wurden behoben und Fans sind glücklich.")
        else:
            self.audio.speak("Keine Bugs zum Beheben gefunden.")
        return "service_menu"

    def _dlc(self, idx):
        if self.game_state.release_dlc(idx):
            self.audio.speak("DLC veröffentlicht! Das Spiel ist wieder in den Charts.")
        else:
            self.audio.speak("Nicht genug Geld für die DLC-Entwicklung.")
        return "service_menu"


# ============================================================
# SPEICHER- SLOTS & HILFE
# ============================================================

class LoadMenu(Menu):
    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        super().__init__(game_state.get_text('select_slot'), [], audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        slots = self.game_state.get_save_slots_info()
        self.options = []
        for i in range(1, 4):
            self.options.append({
                'text': slots[i],
                'action': lambda s=i: self._load(s)
            })
        self.options.append({'text': self.game_state.get_text('back'), 'action': lambda: "main_menu"})
        self.audio.speak(self.game_state.get_text('select_slot'))
        self.speak_current(interrupt=False)

    def _load(self, slot):
        if self.game_state.load_game(slot):
            self.audio.speak(self.game_state.get_text('game_loaded'))
            return "game_menu"
        self.audio.speak(self.game_state.get_text('no_savegame'))
        return None


class SaveMenu(Menu):
    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        super().__init__(game_state.get_text('select_slot'), [], audio, game_state)

    def announce_entry(self):
        self.current_index = 0
        slots = self.game_state.get_save_slots_info()
        self.options = []
        for i in range(1, 4):
            self.options.append({
                'text': slots[i],
                'action': lambda s=i: self._save(s)
            })
        self.options.append({'text': self.game_state.get_text('back'), 'action': lambda: "game_menu"})
        self.audio.speak(self.game_state.get_text('select_slot'))
        self.speak_current(interrupt=False)

    def _save(self, slot):
        if self.game_state.save_game(slot):
            self.audio.speak(self.game_state.get_text('game_saved', slot=slot))
            return "game_menu"
        return None


class HelpMenu(Menu):
    def __init__(self, audio, game_state):
        self.audio = audio
        self.game_state = game_state
        options = [
            {'text': game_state.get_text('wiki_concept'), 'action': lambda: self._speak_key('wiki_concept')},
            {'text': game_state.get_text('wiki_dev'), 'action': lambda: self._speak_key('wiki_dev')},
            {'text': game_state.get_text('wiki_hr'), 'action': lambda: self._speak_key('wiki_hr')},
            {'text': game_state.get_text('back'), 'action': lambda: "game_menu"}
        ]
        super().__init__(game_state.get_text('wiki'), options, audio, game_state)

    def _speak_key(self, key):
        self.audio.speak(self.game_state.get_text(key))
        return None

    def announce_entry(self):
        self.current_index = 0
        self.audio.speak(self.game_state.get_text('wiki_welcome'))
        self.speak_current(interrupt=False)
