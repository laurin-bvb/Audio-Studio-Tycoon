"""
Audio Studio Tycoon - Audio Edition
Hauptprogramm & Spielschleife

100% Screenreader-optimiert (NVDA).
Steuerung: Pfeiltasten + Enter + Buchstaben für Texteingabe.
"""

import pygame
import time
from audio import AudioManager
from logic import GameState
from menus import (
    MainMenu,
    CompanyNameMenu,
    GameMenu,
    TopicMenu,
    GenreMenu,
    PlatformMenu,
    AudienceMenu,
    EngineSelectMenu,
    GameNameMenu,
    DevelopmentSliderMenu,
    DevProgressMenu,
    ReviewResultMenu,
    HRMenu,
    HireMenu,
    FireMenu,
    ResearchMenu,
    FeatureResearchMenu,
    EngineCreateNameMenu,
    EngineFeatureSelectMenu,
    OfficeMenu,
    GameSizeMenu,
    MarketingMenu,
    TrainingEmployeeSelectMenu,
    TrainingOptionMenu,
    BankruptcyMenu,
    EmailInboxMenu,
    EmailDetailMenu,
    ServiceMenu,
    GameServiceOptionsMenu,
)


def main():
    # ---- Initialisierung ----
    pygame.init()
    screen = pygame.display.set_mode((500, 300))
    pygame.display.set_caption("Audio Studio Tycoon - Audio Edition")
    audio = AudioManager()
    audio.speak("Audio Studio Tycoon.")
    state = GameState()

    # ---- Menü-Instanzen ----
    menus = {
        # Haupt-Flow
        "main_menu": MainMenu(audio, state),
        "company_name_input": CompanyNameMenu(audio, state),
        "game_menu": GameMenu(audio, state),

        # Spielentwicklung
        "topic_menu": TopicMenu(audio, state),
        "genre_menu": GenreMenu(audio, state),
        "platform_menu": PlatformMenu(audio, state),
        "audience_menu": AudienceMenu(audio, state),
        "game_size_menu": GameSizeMenu(audio, state),
        "marketing_menu": MarketingMenu(audio, state),
        "engine_select_menu": EngineSelectMenu(audio, state),
        "game_name_input": GameNameMenu(audio, state),
        "slider_menu": DevelopmentSliderMenu(audio, state),
        "dev_progress_menu": DevProgressMenu(audio, state),
        "review_result": ReviewResultMenu(audio, state),

        # Personal
        "hr_menu": HRMenu(audio, state),
        "hire_menu": HireMenu(audio, state),
        "fire_menu": FireMenu(audio, state),
        "training_employee_select": TrainingEmployeeSelectMenu(audio, state),
        "training_option_select": TrainingOptionMenu(audio, state),

        # Forschung & Engines
        "research_menu": ResearchMenu(audio, state),
        "feature_research_menu": FeatureResearchMenu(audio, state),
        "engine_create_name": EngineCreateNameMenu(audio, state),
        "engine_feature_select": EngineFeatureSelectMenu(audio, state),

        # Büro
        "office_menu": OfficeMenu(audio, state),

        # Spezial
        "bankruptcy": BankruptcyMenu(audio, state),
        "email_inbox": EmailInboxMenu(audio, state),
        "email_detail": EmailDetailMenu(audio, state),
        "service_menu": ServiceMenu(audio, state),
        "game_service_options": GameServiceOptionsMenu(audio, state),
    }

    current_key = "main_menu"
    current_menu = menus[current_key]

    # ---- Willkommensnachricht ----
    audio.speak(
        "Willkommen bei Audio Studio Tycoon, Audio Edition! "
        "Gründe deine eigene Spielefirma, stelle Mitarbeiter ein, "
        "erforsche Technologien und entwickle Bestseller! "
        "Nutze die Pfeiltasten zum Navigieren und Enter zum Auswählen."
    )
    time.sleep(0.3)
    current_menu.announce_entry()

    # ---- Hauptschleife ----
    running = True
    clock = pygame.time.Clock()

    while running:
        # Update-Logik (Fortschrittsbalken etc.)
        if hasattr(current_menu, 'update'):
            current_menu.update()

        # Pleite-Check
        if state.is_bankrupt() and current_key != "bankruptcy":
            current_key = "bankruptcy"
            current_menu = menus[current_key]
            current_menu.announce_entry()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                result = current_menu.handle_input(event)

                if result == "quit":
                    running = False
                elif result and result in menus:
                    current_key = result
                    current_menu = menus[current_key]
                    current_menu.announce_entry()

        # Fenster aktualisieren
        screen.fill((10, 10, 20))

        try:
            font = pygame.font.SysFont("Arial", 13)

            # Header
            header = font.render(
                f"[{state.company_name or 'Audio Studio Tycoon'}] "
                f"Geld: {state.money:,} | Fans: {state.fans:,} | "
                f"Woche: {state.week} | Spiele: {state.games_made}",
                True, (80, 200, 80)
            )
            screen.blit(header, (10, 10))

            # Team-Info
            from game_data import OFFICE_LEVELS
            office = OFFICE_LEVELS[state.office_level]
            team_text = font.render(
                f"Büro: {office['name']} | "
                f"Mitarbeiter: {len(state.employees)}/{office['max_employees']} | "
                f"Engines: {len(state.engines)}",
                True, (100, 150, 200)
            )
            screen.blit(team_text, (10, 30))

            # Menü-Info
            menu_info = font.render(f"Aktuelles Menü: {current_key}", True, (150, 150, 150))
            screen.blit(menu_info, (10, 50))

            # Trend-Info
            if state.current_trend:
                txt = f"TREND: {state.current_trend['topic']} / {state.current_trend['genre']}"
                trend_v = font.render(txt, True, (255, 100, 100))
                screen.blit(trend_v, (10, 70))

            # Screenreader-Hinweis
            hint = font.render(
                "Dieses Spiel ist für Screenreader (NVDA) optimiert. "
                "Das Fenster dient nur der Tastatureingabe.",
                True, (60, 60, 60)
            )
            screen.blit(hint, (10, 275))
        except Exception:
            pass

        pygame.display.flip()
        clock.tick(30)

    # ---- Aufräumen ----
    audio.cleanup()
    pygame.quit()


if __name__ == "__main__":
    main()
