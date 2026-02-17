"""
Spielzustand für Audio Studio Tycoon - Audio Edition.

Verwaltet Firmendaten, Geld, Fans, Mitarbeiter, Engines,
Spielhistorie, Ereignisse und die Bewertungslogik.
"""

import random
import json
import os
from models import GameProject, ReviewScore, Employee, Engine, EngineFeature
from translations import TRANSLATIONS
from game_data import (
    get_compatibility, get_ideal_sliders, SLIDER_NAMES, GENRES,
    PLATFORMS, AUDIENCE_MULTI, AUDIENCE_PRICE,
    RANDOM_EVENTS, OFFICE_LEVELS, ENGINE_FEATURES,
    EMPLOYEE_ROLES, DEV_PHASES, GAME_SIZES, MARKETING_CAMPAIGNS,
    TREND_TOPICS, TREND_GENRES, TRAINING_OPTIONS,
    get_available_platforms, get_available_features,
)


class GameState:
    def __init__(self):
        self.company_name = ""
        self.money = 70000
        self.fans = 0
        self.week = 1
        self.game_history = []    # Liste aller GameProject
        self.high_score = 0.0
        self.games_made = 0
        self.total_revenue = 0

        # Trends
        self.current_trend = {}  # {'topic': '...', 'genre': '...', 'week_started': X}
        self.last_trend_week = 0

        # Mitarbeiter
        self.employees = []

        # Engines
        self.engines = []
        self.unlocked_features = []  # Liste von EngineFeature (freigeschaltet)
        self._init_starter_engine()

        # Büro
        self.office_level = 0  # Index in OFFICE_LEVELS

        # Ereignisse
        self.last_event_week = 0

        # Aktuelles Projekt
        self.current_draft = {
            "name": "",
            "topic": None,
            "genre": None,
            "platform": None,
            "audience": None,
            "engine": None,
            "sliders": {},
            "size": "Mittel",
            "marketing": "Kein Marketing",
        }
        
        # Posteingang
        self.emails = []

        # Einstellungen
        self.settings = {
            "language": "de",
            "music_enabled": True
        }

    def _init_starter_engine(self):
        """Erstellt die Starter-Engine mit Basis-Features."""
        starter_features = []
        for f_data in ENGINE_FEATURES:
            if f_data["cost"] == 0:
                feat = EngineFeature(f_data["category"], f_data["name"], f_data["tech_bonus"])
                starter_features.append(feat)
                self.unlocked_features.append(feat)

        starter = Engine("Basis-Engine", starter_features)
        self.engines.append(starter)

    def reset_draft(self):
        """Setzt den aktuellen Entwurf zurück."""
        self.current_draft = {
            "name": "",
            "topic": None,
            "genre": None,
            "platform": None,
            "audience": None,
            "engine": None,
            "sliders": {},
            "size": "Mittel",
            "marketing": "Kein Marketing",
        }

    def get_text(self, key, **kwargs):
        """Holt einen übersetzten Text basierend auf dem aktuellen Sprach-Setting."""
        lang = self.settings.get("language", "de")
        text = TRANSLATIONS.get(lang, TRANSLATIONS['de']).get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text
        return text

    # ==========================================================
    # MITARBEITER
    # ==========================================================

    def get_max_employees(self):
        """Maximale Mitarbeiter basierend auf Büro-Level."""
        return OFFICE_LEVELS[self.office_level]["max_employees"]

    def can_hire(self):
        return len(self.employees) < self.get_max_employees()

    def generate_candidate(self):
        """Generiert einen zufälligen Bewerber."""
        from game_data import EMPLOYEE_SPECIALIZATIONS
        role_data = random.choice(EMPLOYEE_ROLES)
        level = random.randint(1, min(3, 1 + self.games_made // 3))
        
        spec = None
        if random.random() < 0.3: # 30% Chance auf Spezialisierung
            spec = random.choice(EMPLOYEE_SPECIALIZATIONS)
            
        return Employee(role_data=role_data, skill_level=level, specialization=spec)

    def hire_employee(self, employee):
        """Stellt einen Mitarbeiter ein."""
        if not self.can_hire():
            return False
        # Einstellungsgebühr = 2 Wochen Gehalt
        hire_cost = employee.salary * 2
        if self.money < hire_cost:
            return False
        self.money -= hire_cost
        self.employees.append(employee)
        return True

    def fire_employee(self, index):
        """Entlässt einen Mitarbeiter."""
        if 0 <= index < len(self.employees):
            emp = self.employees.pop(index)
            # Abfindung = 4 Wochen Gehalt
            self.money -= emp.salary * 4
            return emp
        return None

    def pay_salaries(self):
        """Bezahlt alle Gehälter (wöchentlich)."""
        total = sum(e.salary for e in self.employees)
        self.money -= total
        return total

    def advance_week(self, weeks=1):
        """Rückt die Zeit vor und verarbeitet wöchentliche Ereignisse."""
        for _ in range(weeks):
            self.week += 1
            self.pay_salaries()
            
            # Trends und Zufallsereignisse
            self.check_random_event()
            
            # Verkäufe für aktive Spiele
            for g in self.game_history:
                if g.is_active:
                    g.weeks_on_market += 1
                    # Verkäufe sinken mit der Zeit
                    new_sales = int(self.calculate_sales(g) / (1 + g.weeks_on_market * 0.2))
                    if g.bugs > 0:
                        new_sales = int(new_sales * 0.5) # Bugs halbieren Verkäufe
                    
                    price = AUDIENCE_PRICE.get(g.audience, 30)
                    g.sales += new_sales
                    g.revenue += new_sales * price
                    self.money += new_sales * price
                    
                    # Nach 12-20 Wochen oder bei sehr niedrigen Verkäufen vom Markt nehmen
                    if g.weeks_on_market > 20 or new_sales < 100:
                        g.is_active = False

            # Fan-Mails & Bugs generieren
            self.process_emails()

    def process_emails(self):
        """Generiert zufällige E-Mails."""
        from models import Email
        from game_data import MAIL_TEMPLATES
        
        if not self.game_history:
            return
            
        # Chance auf Mail
        if random.random() < 0.2:
            game = random.choice(self.game_history)
            if random.random() < 0.5:
                # Bug Report
                game.bugs += random.randint(1, 5)
                mail = Email(
                    sender="Ein enttäuschter Spieler",
                    subject=MAIL_TEMPLATES["bug_report"]["subject"].format(game=game.name),
                    body=MAIL_TEMPLATES["bug_report"]["body"].format(game=game.name),
                    date_week=self.week,
                    game_name=game.name,
                    is_bug=True
                )
            else:
                # Fan Mail
                mail = Email(
                    sender="Fan",
                    subject=MAIL_TEMPLATES["fan_praise"]["subject"].format(game=game.name),
                    body=MAIL_TEMPLATES["fan_praise"]["body"].format(game=game.name, topic=game.topic),
                    date_week=self.week,
                    game_name=game.name
                )
            self.emails.insert(0, mail)
            
    def release_patch(self, game_index):
        """Veröffentlicht einen kostenlosen Patch."""
        game = self.game_history[game_index]
        if game.bugs > 0:
            game.bugs = 0
            self.fans += 100
            return True
        return False

    def release_dlc(self, game_index):
        """Veröffentlicht einen kostenpflichtigen DLC."""
        game = self.game_history[game_index]
        cost = 20000
        if self.money < cost:
            return False
        self.money -= cost
        game.dlc_count += 1
        game.is_active = True # Bringt Spiel zurück in die Charts
        game.weeks_on_market = max(0, game.weeks_on_market - 5)
        self.fans += 500
        return True

    def get_team_bonus(self):
        """Gesamtbonus des Teams auf Spielqualität."""
        if not self.employees:
            return 0.0
        return sum(e.quality_contribution for e in self.employees)

    def get_team_slider_bonus(self, slider_name):
        """Durchschnittlicher Skill-Bonus des Teams für einen Slider."""
        if not self.employees:
            return 0.0
        bonuses = [e.get_slider_bonus(slider_name) for e in self.employees]
        return sum(bonuses) / len(bonuses)

    # ==========================================================
    # ENGINES
    # ==========================================================

    def research_feature(self, feature_data):
        """Schaltet ein Engine-Feature frei."""
        if self.money < feature_data["cost"]:
            return False
        # Prüfen ob schon freigeschaltet
        for f in self.unlocked_features:
            if f.name == feature_data["name"]:
                return False
        self.money -= feature_data["cost"]
        feat = EngineFeature(feature_data["category"], feature_data["name"], feature_data["tech_bonus"])
        self.unlocked_features.append(feat)
        return True

    def create_engine(self, name, feature_list):
        """Erstellt eine neue Engine aus freigeschalteten Features."""
        engine = Engine(name, feature_list)
        self.engines.append(engine)
        return engine

    def get_researchable_features(self):
        """Features die erforschbar, aber noch nicht freigeschaltet sind."""
        available = get_available_features(self.week)
        unlocked_names = {f.name for f in self.unlocked_features}
        return [f for f in available if f["name"] not in unlocked_names]

    # ==========================================================
    # BÜRO
    # ==========================================================

    def can_upgrade_office(self):
        """Kann das Büro aufgerüstet werden?"""
        if self.office_level >= len(OFFICE_LEVELS) - 1:
            return False
        next_level = OFFICE_LEVELS[self.office_level + 1]
        return self.money >= next_level["cost"]

    def upgrade_office(self):
        """Rüstet das Büro auf."""
        if not self.can_upgrade_office():
            return False
        next_level = OFFICE_LEVELS[self.office_level + 1]
        self.money -= next_level["cost"]
        self.office_level += 1
        return True

    def get_office_info(self):
        """Info über aktuelles Büro."""
        office = OFFICE_LEVELS[self.office_level]
        return office

    # ==========================================================
    # TRENDS
    # ==========================================================

    def update_trends(self):
        """Aktualisiert Markttrends alle 12-20 Wochen."""
        if self.week - self.last_trend_week < random.randint(12, 20):
            return None
        
        # Trend auswählen
        topic_trend = random.choice(TREND_TOPICS)
        genre_trend = random.choice(TREND_GENRES)
        
        self.current_trend = {
            "topic": topic_trend["topic"],
            "genre": genre_trend["genre"],
            "text": f"{topic_trend['text']} Und: {genre_trend['text']}",
            "week_started": self.week
        }
        self.last_trend_week = self.week
        return self.current_trend

    # ==========================================================
    # ZUFALLSEREIGNISSE
    # ==========================================================

    def check_random_event(self):
        """Prüft ob ein Zufallsereignis oder Trendwechsel ausgelöst wird."""
        # Trend prüfen
        trend = self.update_trends()
        if trend:
            return {"title": "Markttrend-Wechsel", "text": trend["text"], "effect": "trend"}

        if self.week - self.last_event_week < 8:
            return None
        if random.random() < 0.25:
            event = random.choice(RANDOM_EVENTS)
            self.last_event_week = self.week
            self.apply_event(event)
            return event
        return None

    def apply_event(self, event):
        """Wendet ein Ereignis an."""
        if event["effect"] == "money":
            self.money += event["value"]
        elif event["effect"] == "fans":
            self.fans = max(0, self.fans + event["value"])

    # ==========================================================
    # BEWERTUNG
    # ==========================================================

    def calculate_review(self, project):
        """
        Berechnet die Bewertung eines Spiels.
        Inklusive Trend-Bonus.
        """
        topic = project.topic
        genre = project.genre
        sliders = project.sliders

        # 1. Synergiewert (0.0 - 1.0)
        compat_raw = get_compatibility(topic, genre)
        synergy = compat_raw / 3.0

        # 2. Slider-Match (0.0 - 1.0)
        ideal = get_ideal_sliders(genre)
        total_diff = 0
        max_diff = 0
        for sname in SLIDER_NAMES:
            player_val = sliders.get(sname, 5)
            ideal_val = ideal.get(sname, 5)
            team_bonus = self.get_team_slider_bonus(sname)
            effective_val = player_val + team_bonus
            total_diff += abs(effective_val - ideal_val)
            max_diff += 10
        slider_match = 1.0 - (total_diff / max_diff) if max_diff > 0 else 0.5

        # 3. Team-Bonus (0.0 - 1.0)
        team_quality = min(1.0, self.get_team_bonus() * 5)

        # 4. Engine-Bonus (0.0 - 1.0)
        engine_quality = 0.3
        if project.engine:
            engine_quality = min(1.0, 0.3 + project.engine.quality_bonus)

        # 5. Trend-Bonus
        trend_bonus = 1.0
        if self.current_trend:
            if topic == self.current_trend["topic"]:
                trend_bonus += 0.2
            if genre == self.current_trend["genre"]:
                trend_bonus += 0.2

        # 6. Zufallsfaktor
        random_factor = random.uniform(0.9, 1.1)

        # Basis-Score
        base_score = (
            (synergy * 0.30) +
            (slider_match * 0.30) +
            (team_quality * 0.15) +
            (engine_quality * 0.10) +
            (0.5 * 0.15)
        )
        base_score *= random_factor * trend_bonus

        # Sequel Bonus/Malus
        if len(self.game_history) > 0:
            last = self.game_history[-1]
            if last.topic == topic and last.genre == genre:
                base_score *= 0.8
            
            # Sequel Bonus: Wenn der Name eine Steigerung andeutet
            is_sequel = False
            if project.name.startswith(last.name) and project.name != last.name:
                is_sequel = True
            
            if is_sequel:
                if last.review and last.review.average >= 7.5:
                    base_score *= 1.15  # Hype Bonus
                elif last.review and last.review.average < 5.0:
                    base_score *= 0.85  # Enttäuschungs-Malus

        if self.high_score > 0:
            ratio = (base_score * 10) / self.high_score
            if ratio < 0.8:
                base_score *= 0.9

        prestige = OFFICE_LEVELS[self.office_level]["prestige"]
        base_score *= (1.0 + prestige * 0.03)

        base_review = max(1.0, min(10.0, float(base_score * 10)))

        scores = []
        for _ in range(4):
            variance = random.uniform(-1.2, 1.2)
            s = int(round(max(1.0, min(10.0, base_review + variance))))
            scores.append(s)

        # NEU: Review-Texte generieren
        from game_data import REVIEW_TEMPLATES
        comments = []
        
        # Intro
        intro = random.choice(REVIEW_TEMPLATES["intro"]).format(company=self.company_name, game=project.name)
        comments.append(intro)
        
        # Positiv/Negativ basierend auf Slidern/Synergie
        if synergy >= 0.8:
            comments.append(random.choice(REVIEW_TEMPLATES["positive"]).format(genre=project.genre, topic=project.topic))
        elif synergy < 0.5:
            comments.append(random.choice(REVIEW_TEMPLATES["negative"]).format(genre=project.genre, topic=project.topic))
            
        if slider_match < 0.6:
            comments.append("Das Gameplay fühlt sich hölzern an.")
        elif slider_match >= 0.9:
            comments.append("Die Spielmechaniken sind perfekt aufeinander abgestimmt.")

        # Fazit
        comments.append(random.choice(REVIEW_TEMPLATES["conclusion"]))

        review = ReviewScore(scores, comments=comments)
        if review.average > self.high_score:
            self.high_score = review.average

        return review

    def calculate_sales(self, project):
        """Berechnet Verkäufe inkl. Marketing und Größe."""
        if not project.review:
            return 0

        avg = project.review.average
        # Basis-Verkäufe skalieren mit Größe
        size_data = next((s for s in GAME_SIZES if s["name"] == project.size), GAME_SIZES[1])
        base_sales = 5000 * size_data["revenue_multi"]

        if avg >= 9: score_m = 10.0
        elif avg >= 8: score_m = 5.0
        elif avg >= 7: score_m = 3.0
        elif avg >= 6: score_m = 2.0
        elif avg >= 5: score_m = 1.0
        elif avg >= 4: score_m = 0.5
        else: score_m = 0.2

        fan_bonus = 1.0 + (self.fans / 100000)

        # Marketing Multiplikator
        mark_data = next((m for m in MARKETING_CAMPAIGNS if m["name"] == project.marketing), MARKETING_CAMPAIGNS[0])
        marketing_multi = mark_data["sales_multi"]

        plat_multi = 1.0
        for p in PLATFORMS:
            if p["name"] == project.platform:
                plat_multi = p["market_multi"]
                break

        audience_multi = AUDIENCE_MULTI.get(project.audience, 1.0)
        rand_m = random.uniform(0.8, 1.2)

        sales = int(base_sales * score_m * fan_bonus * plat_multi * audience_multi * marketing_multi * rand_m)
        return sales

    def calculate_dev_cost(self, project):
        """Berechnet Entwicklungskosten inkl. Größe und Marketing."""
        # Basis-Kosten basierend auf Größe
        size_data = next((s for s in GAME_SIZES if s["name"] == project.size), GAME_SIZES[1])
        base_cost = 10000 * size_data["cost_multi"]

        # Team-Kosten
        dev_weeks = sum(p["duration_weeks"] for p in DEV_PHASES) * size_data["time_multi"]
        salary_cost = sum(e.salary for e in self.employees) * dev_weeks

        # Lizenzgebühren
        license_fee = 0
        for p in PLATFORMS:
            if p["name"] == project.platform:
                license_fee = p["license_fee"]
                break

        # Marketing-Kosten
        mark_data = next((m for m in MARKETING_CAMPAIGNS if m["name"] == project.marketing), MARKETING_CAMPAIGNS[0])
        marketing_cost = mark_data["cost"]

        return int(base_cost + salary_cost + license_fee + marketing_cost)

    def finalize_game(self, project):
        """Schließt die Spielentwicklung ab."""
        project.week_developed = self.week

        # Kosten und Marketing abziehen
        project.dev_cost = self.calculate_dev_cost(project)
        self.money -= project.dev_cost

        project.review = self.calculate_review(project)
        project.sales = self.calculate_sales(project)

        price = AUDIENCE_PRICE.get(project.audience, 30)
        project.revenue = project.sales * price

        self.money += project.revenue
        self.fans += project.sales // 10
        self.games_made += 1
        self.total_revenue += project.revenue

        # Zeit vorrücken
        size_data = next((s for s in GAME_SIZES if s["name"] == project.size), GAME_SIZES[1])
        dev_weeks = int(sum(p["duration_weeks"] for p in DEV_PHASES) * size_data["time_multi"])
        self.week += dev_weeks

        for emp in self.employees:
            emp.weeks_employed += dev_weeks
            if project.review and project.review.average >= 7:
                emp.morale = min(100, emp.morale + 5)
            elif project.review and project.review.average < 4:
                emp.morale = max(0, emp.morale - 10)

        self.game_history.append(project)
        return project

    # ==========================================================
    # TRAINING
    # ==========================================================

    def train_employee(self, emp_index, train_data):
        """Verbessert Skills eines Mitarbeiters."""
        if self.money < train_data["cost"]:
            return False
        
        emp = self.employees[emp_index]
        self.money -= train_data["cost"]
        
        # Skill-Boost auf Primärskill
        sname = emp.primary_skill
        emp.skills[sname] = min(100, emp.skills.get(sname, 0) + train_data["skill_boost"])
        # Kleiner Boost auf Sekundärskill
        s2 = emp.secondary_skill
        emp.skills[s2] = min(100, emp.skills.get(s2, 0) + train_data["skill_boost"] // 2)
        
        # Gehalt steigt leicht
        emp.salary = emp._calculate_salary()
        return True

    # ==========================================================
    # PLEITE CHECK
    # ==========================================================

    def is_bankrupt(self):
        """Prüft ob die Firma pleite ist."""
        return self.money < -50000  # Kreditrahmen von 50k


    # ==========================================================
    # STATUS
    # ==========================================================

    def get_status_text(self):
        """Statusübersicht als Text."""
        office = OFFICE_LEVELS[self.office_level]
        return (
            f"Firma: {self.company_name}. "
            f"Geld: {self.money:,} Euro. "
            f"Fans: {self.fans:,}. "
            f"Woche: {self.week}. "
            f"Büro: {office['name']}. "
            f"Mitarbeiter: {len(self.employees)} von {office['max_employees']}. "
            f"Spiele entwickelt: {self.games_made}."
        )

    # ==========================================================
    # SPEICHERN / LADEN
    # ==========================================================

    def save_game(self, slot=1):
        """Speichert den Spielstand in einem Slot."""
        filepath = f"save_slot_{slot}.json"
        data = {
            "company_name": self.company_name,
            "money": self.money,
            "fans": self.fans,
            "week": self.week,
            "high_score": self.high_score,
            "games_made": self.games_made,
            "total_revenue": self.total_revenue,
            "office_level": self.office_level,
            "last_event_week": self.last_event_week,
            "last_trend_week": self.last_trend_week,
            "current_trend": self.current_trend,
            "settings": self.settings,
            "game_history": [g.to_dict() for g in self.game_history],
            "employees": [e.to_dict() for e in self.employees],
            "engines": [
                {"name": eng.name, "features": [
                    {"category": f.category, "name": f.name, "tech_bonus": f.tech_bonus}
                    for f in eng.features
                ]} for eng in self.engines
            ],
            "unlocked_features": [
                {"category": f.category, "name": f.name, "tech_bonus": f.tech_bonus}
                for f in self.unlocked_features
            ],
            "emails": [
                {
                    "sender": m.sender, "subject": m.subject, "body": m.body,
                    "date_week": m.date_week, "game_name": m.game_name,
                    "is_bug": m.is_bug, "is_read": m.is_read
                } for m in self.emails
            ]
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True

    def get_save_slots_info(self):
        """Gibt Infos über die 3 verfügbaren Slots zurück."""
        slots = {}
        for i in range(1, 4):
            path = f"save_slot_{i}.json"
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    slots[i] = f"Slot {i}: {data['company_name']} (Woche {data['week']}, {data['money']:,} Euro)"
                except:
                    slots[i] = f"Slot {i}: [FEHLERHAFT]"
            else:
                slots[i] = f"Slot {i}: [LEER]"
        return slots

    def load_game(self, slot=1):
        """Lädt einen Spielstand aus einem Slot."""
        filepath = f"save_slot_{slot}.json"
        if not os.path.exists(filepath):
            return False

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.company_name = data["company_name"]
        self.money = data["money"]
        self.fans = data["fans"]
        self.week = data["week"]
        self.high_score = data["high_score"]
        self.games_made = data["games_made"]
        self.total_revenue = data["total_revenue"]
        self.office_level = data["office_level"]
        self.last_event_week = data.get("last_event_week", 0)
        self.last_trend_week = data.get("last_trend_week", 0)
        self.current_trend = data.get("current_trend")

        # Engines laden
        self.unlocked_features = []
        for fd in data.get("unlocked_features", []):
            self.unlocked_features.append(
                EngineFeature(fd["category"], fd["name"], fd["tech_bonus"])
            )

        self.engines = []
        for ed in data.get("engines", []):
            features = [
                EngineFeature(fd["category"], fd["name"], fd["tech_bonus"])
                for fd in ed["features"]
            ]
            self.engines.append(Engine(ed["name"], features))

        # Spielhistorie laden
        self.game_history = []
        for gd in data.get("game_history", []):
            proj = GameProject(
                gd["name"], gd["topic"], gd["genre"],
                gd.get("sliders"), gd.get("platform"), gd.get("audience"),
                size=gd.get("size", "Mittel"), marketing=gd.get("marketing", "Kein Marketing")
            )
            if gd.get("review_scores"):
                proj.review = ReviewScore(gd["review_scores"])
            proj.sales = gd.get("sales", 0)
            proj.revenue = gd.get("revenue", 0)
            proj.dev_cost = gd.get("dev_cost", 0)
            proj.week_developed = gd.get("week_developed", 0)
            self.game_history.append(proj)

        # Mitarbeiter laden
        self.employees = []
        for ed in data.get("employees", []):
            emp = Employee.__new__(Employee)
            emp.name = ed["name"]
            emp.role = ed["role"]
            emp.primary_skill = ed["primary_skill"]
            emp.secondary_skill = ed["secondary_skill"]
            emp.skill_level = ed["skill_level"]
            emp.skills = ed["skills"]
            emp.salary = ed["salary"]
            emp.morale = ed["morale"]
            emp.weeks_employed = ed["weeks_employed"]
            emp.specialization = ed.get("specialization")
            self.employees.append(emp)

        # E-Mails laden
        self.emails = []
        from models import Email
        for md in data.get("emails", []):
            mail = Email(md["sender"], md["subject"], md["body"], md["date_week"], md.get("game_name"), md.get("is_bug", False))
            mail.is_read = md.get("is_read", False)
            self.emails.append(mail)

        self.settings = data.get("settings", {"language": "de", "music_enabled": True})

        self.reset_draft()
        return True
