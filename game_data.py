"""
Statische Spieldaten für Audio Studio Tycoon - Audio Edition.

Enthält Themen, Genres, Kompatibilitätstabelle, Slider-Gewichtungen,
Plattformen, Engine-Features, Mitarbeiter-Daten und Zufallsereignisse.
"""

# ============================================================
# THEMEN (Topics) - 20 verschiedene
# ============================================================
TOPICS = [
    "Fantasy",
    "Sci-Fi",
    "Mittelalter",
    "Spionage",
    "Piraten",
    "Zombies",
    "Sport",
    "Rennen",
    "Krankenhaus",
    "Schule",
    "Stadt",
    "Weltraum",
    "Krieg",
    "Musik",
    "Kochen",
    "Tiere",
    "Horror",
    "Superheld",
    "Cyberpunk",
    "Detektiv",
    "Dinosaurier",
    "Vampire",
    "Feuerwehr",
    "Polizei",
    "Wilder Westen",
]

# ============================================================
# GENRES - 8 verschiedene
# ============================================================
GENRES = [
    "Action",
    "RPG",
    "Simulation",
    "Strategie",
    "Abenteuer",
    "Puzzle",
    "Sport",
    "Casual",
    "Horror",
    "Kampfspiel",
    "Rennspiel",
]

# ============================================================
# SLIDER-NAMEN (6 Slider für die Entwicklungsphase)
# ============================================================
SLIDER_NAMES = [
    "Gameplay",
    "Grafik",
    "Sound",
    "Story",
    "KI",
    "Welt",
]

# ============================================================
# IDEALE SLIDER-VERTEILUNG pro Genre
# ============================================================
GENRE_IDEAL_SLIDERS = {
    "Action": {
        "Gameplay": 9, "Grafik": 7, "Sound": 5, "Story": 2, "KI": 3, "Welt": 4,
    },
    "RPG": {
        "Gameplay": 6, "Grafik": 5, "Sound": 4, "Story": 9, "KI": 4, "Welt": 8,
    },
    "Simulation": {
        "Gameplay": 8, "Grafik": 4, "Sound": 3, "Story": 2, "KI": 7, "Welt": 6,
    },
    "Strategie": {
        "Gameplay": 7, "Grafik": 3, "Sound": 3, "Story": 4, "KI": 9, "Welt": 6,
    },
    "Abenteuer": {
        "Gameplay": 5, "Grafik": 6, "Sound": 6, "Story": 9, "KI": 3, "Welt": 7,
    },
    "Puzzle": {
        "Gameplay": 9, "Grafik": 4, "Sound": 5, "Story": 1, "KI": 5, "Welt": 2,
    },
    "Sport": {
        "Gameplay": 8, "Grafik": 7, "Sound": 5, "Story": 1, "KI": 6, "Welt": 3,
    },
    "Casual": {
        "Gameplay": 8, "Grafik": 5, "Sound": 6, "Story": 1, "KI": 3, "Welt": 3,
    },
}

# ============================================================
# THEMA/GENRE KOMPATIBILITÄT
# 3 = Super, 2 = Gut, 1 = Okay, 0 = Schlecht
# ============================================================
TOPIC_GENRE_COMPAT = {
    #                    Action  RPG  Sim  Strat  Aben  Puzzle  Sport  Casual
    "Fantasy":          [  2,     3,   1,    2,     3,    1,     0,     1  ],
    "Sci-Fi":           [  3,     2,   2,    3,     2,    1,     0,     1  ],
    "Mittelalter":      [  2,     3,   2,    3,     2,    0,     0,     0  ],
    "Spionage":         [  3,     1,   1,    2,     3,    2,     0,     1  ],
    "Piraten":          [  3,     2,   1,    2,     3,    1,     0,     1  ],
    "Zombies":          [  3,     1,   0,    2,     2,    1,     0,     1  ],
    "Sport":            [  1,     0,   2,    1,     0,    0,     3,     2  ],
    "Rennen":           [  2,     0,   2,    0,     0,    0,     3,     2  ],
    "Krankenhaus":      [  0,     0,   3,    1,     1,    2,     0,     2  ],
    "Schule":           [  0,     1,   3,    1,     1,    2,     0,     2  ],
    "Stadt":            [  0,     1,   3,    2,     1,    1,     0,     1  ],
    "Weltraum":         [  3,     2,   2,    3,     2,    0,     0,     1  ],
    "Krieg":            [  3,     1,   1,    3,     1,    0,     0,     0  ],
    "Musik":            [  0,     0,   2,    0,     0,    3,     0,     3  ],
    "Kochen":           [  0,     0,   3,    0,     0,    2,     0,     3  ],
    "Tiere":            [  1,     1,   3,    1,     2,    2,     0,     3  ],
    "Horror":           [  2,     1,   0,    1,     3,    1,     0,     0  ],
    "Superheld":        [  3,     2,   0,    1,     3,    0,     0,     1  ],
    "Cyberpunk":        [  3,     3,   1,    2,     2,    0,     0,     0  ],
    "Detektiv":         [  1,     1,   1,    1,     3,    3,     0,     1  ],
}

# ============================================================
# PLATTFORMEN
# name, Lizenzgebühr, Markt-Multiplikator, verfügbar ab Woche, Ende Woche (None = nie), Typ
# ============================================================
PLATFORMS = [
    {"name": "PC (MS-DOS)",     "license_fee": 0,      "market_multi": 1.0,  "available_week": 1,  "end_week": 40,   "type": "PC"},
    {"name": "PC (Windows)",    "license_fee": 0,      "market_multi": 1.2,  "available_week": 30, "end_week": None, "type": "PC"},
    {"name": "PC (Linux)",      "license_fee": 0,      "market_multi": 0.5,  "available_week": 50, "end_week": None, "type": "PC"},
    
    {"name": "Playsystem 1",    "license_fee": 20000,  "market_multi": 1.5,  "available_week": 1,  "end_week": 100,  "type": "Konsole"},
    {"name": "Playsystem 2",    "license_fee": 40000,  "market_multi": 2.2,  "available_week": 80, "end_week": 250,  "type": "Konsole"},
    
    {"name": "Ninvento GS",     "license_fee": 15000,  "market_multi": 1.3,  "available_week": 1,  "end_week": 60,   "type": "Handheld"},
    {"name": "Ninvento Duo",    "license_fee": 30000,  "market_multi": 1.8,  "available_week": 70, "end_week": 200,  "type": "Konsole"},
    
    {"name": "mBox",            "license_fee": 25000,  "market_multi": 1.4,  "available_week": 20, "end_week": 150,  "type": "Konsole"},
    {"name": "mBox 360",        "license_fee": 45000,  "market_multi": 2.0,  "available_week": 140,"end_week": 350,  "type": "Konsole"},
    
    {"name": "Handheld X",      "license_fee": 10000,  "market_multi": 0.8,  "available_week": 1,  "end_week": 80,   "type": "Handheld"},
    {"name": "Smartphone",      "license_fee": 5000,   "market_multi": 2.5,  "available_week": 160,"end_week": None, "type": "Mobile"},
    {"name": "Tablet OS",       "license_fee": 7000,   "market_multi": 1.8,  "available_week": 200,"end_week": None, "type": "Mobile"},
]

AUDIENCE_MULTI = {
    "Jeder":           1.5,
    "Jugendliche":     1.0,
    "Hardcore-Gamer":  0.7,
}

AUDIENCE_PRICE = {
    "Jeder":           20,
    "Jugendliche":     30,
    "Hardcore-Gamer":  50,
}

AUDIENCES = list(AUDIENCE_PRICE.keys())

# ============================================================
# REVIEW-TEXTE
# ============================================================
REVIEW_TEMPLATES = {
    "intro": [
        "Das neue Spiel von {company} ist da!",
        "Wir haben uns '{game}' genau angesehen.",
        "Endlich ist '{game}' auf dem Markt!"
    ],
    "positive": [
        "Die Story und das Gameplay waren erstklassig!",
        "Die technische Umsetzung ist absolut brillant.",
        "Ein Meilenstein für das Genre {genre}.",
        "Selten hat uns ein Spiel so gefesselt."
    ],
    "negative": [
        "Die Grafik ist leider total veraltet.",
        "Das Gameplay fühlt sich hölzern an.",
        "Es gibt viel zu viele Bugs zum Release.",
        "Das Thema {topic} wurde schwach umgesetzt."
    ],
    "conclusion": [
        "Ein absolutes Muss für jeden Fan!",
        "Kann man spielen, muss man aber nicht.",
        "Leider eine Enttäuschung auf ganzer Linie.",
        "Wir sind gespannt auf das nächste Projekt."
    ]
}

# ============================================================
# FAN-MAILS & BUG-REPORTS
# ============================================================
MAIL_TEMPLATES = {
    "fan_praise": {
        "subject": "Ich liebe {game}!",
        "body": "Hey! Ich spiele gerade '{game}' und es ist fantastisch. Besonders das Thema {topic} gefällt mir!"
    },
    "fan_critique": {
        "subject": "Enttäuscht von {game}",
        "body": "Eigentlich mag ich eure Spiele, aber '{game}' ist nicht so gut. Das Genre {genre} passt irgendwie nicht."
    },
    "bug_report": {
        "subject": "BUG gefunden in {game}!",
        "body": "Hilfe! Ich hänge im Level fest. Es scheint ein technisches Problem zu geben. Bitte fixen!"
    }
}

# ============================================================
# ENGINE-FEATURES (zum Freischalten / Erforschen)
# category, name, tech_bonus, research_cost, available_week
# ============================================================
ENGINE_FEATURES = [
    # Grafik
    {"category": "Grafik",    "name": "2D Grafik V1",        "tech_bonus": 1,  "cost": 0,      "week": 1},
    {"category": "Grafik",    "name": "2D Grafik V2",        "tech_bonus": 2,  "cost": 15000,  "week": 10},
    {"category": "Grafik",    "name": "3D Grafik V1",        "tech_bonus": 3,  "cost": 40000,  "week": 30},
    {"category": "Grafik",    "name": "3D Grafik V2",        "tech_bonus": 5,  "cost": 80000,  "week": 60},
    # Sound
    {"category": "Sound",     "name": "Mono Sound",          "tech_bonus": 1,  "cost": 0,      "week": 1},
    {"category": "Sound",     "name": "Stereo Sound",        "tech_bonus": 2,  "cost": 10000,  "week": 10},
    {"category": "Sound",     "name": "Surround Sound",      "tech_bonus": 3,  "cost": 30000,  "week": 40},
    # KI
    {"category": "KI",        "name": "Einfache KI",         "tech_bonus": 1,  "cost": 0,      "week": 1},
    {"category": "KI",        "name": "Fortgeschrittene KI", "tech_bonus": 2,  "cost": 20000,  "week": 20},
    {"category": "KI",        "name": "Lernende KI",         "tech_bonus": 4,  "cost": 60000,  "week": 50},
    # Gameplay
    {"category": "Gameplay",  "name": "Basis Steuerung",     "tech_bonus": 1,  "cost": 0,      "week": 1},
    {"category": "Gameplay",  "name": "Physik-Engine",       "tech_bonus": 2,  "cost": 25000,  "week": 15},
    {"category": "Gameplay",  "name": "Online-Multiplayer",  "tech_bonus": 4,  "cost": 70000,  "week": 45},
    # Level-Design
    {"category": "Level",     "name": "Lineares Design",     "tech_bonus": 1,  "cost": 0,      "week": 1},
    {"category": "Level",     "name": "Open World",          "tech_bonus": 3,  "cost": 50000,  "week": 35},
]

# ============================================================
# MITARBEITER-NAMEN (zufällig)
# ============================================================
EMPLOYEE_FIRST_NAMES = [
    "Max", "Anna", "Felix", "Sarah", "Tim", "Julia", "Leon", "Laura",
    "Lukas", "Marie", "Jonas", "Lena", "Niklas", "Emma", "David",
    "Sophie", "Jan", "Mia", "Tom", "Lisa", "Kai", "Nina", "Ben",
    "Hanna", "Erik", "Lea", "Paul", "Clara", "Finn", "Ella",
]

EMPLOYEE_LAST_NAMES = [
    "Müller", "Schmidt", "Weber", "Fischer", "Wagner", "Bauer",
    "Koch", "Richter", "Klein", "Wolf", "Schwarz", "Braun",
    "Zimmermann", "Hartmann", "Krüger", "Hofmann", "Lange",
    "Jung", "Peters", "König", "Lang", "Berg", "Stein",
]

EMPLOYEE_ROLES = [
    {"role": "Programmierer",  "primary": "KI",       "secondary": "Gameplay"},
    {"role": "Designer",       "primary": "Grafik",   "secondary": "Welt"},
    {"role": "Sound-Engineer", "primary": "Sound",    "secondary": "Gameplay"},
    {"role": "Autor",          "primary": "Story",    "secondary": "Welt"},
    {"role": "Allrounder",     "primary": "Gameplay", "secondary": "Grafik"},
]

# ============================================================
# MITARBEITER-SPEZIALISIERUNGEN (Boni)
# ============================================================
EMPLOYEE_SPECIALIZATIONS = [
    {"name": "Sound-Genie",      "bonus_type": "Sound",    "bonus_value": 0.2, "description": "Verbessert die Audio-Qualität massiv."},
    {"name": "Code-Maschine",    "bonus_type": "KI",       "bonus_value": 0.2, "description": "Optimiert Programmierung und KI."},
    {"name": "Design-Gott",      "bonus_type": "Grafik",   "bonus_value": 0.2, "description": "Ein Auge für erstklassige Grafik."},
    {"name": "Story-Master",     "bonus_type": "Story",    "bonus_value": 0.2, "description": "Schreibt packende Dialoge und Plots."},
    {"name": "Motivationstrainer", "bonus_type": "Moral",   "bonus_value": 10,  "description": "Hält die Moral im Team hoch."},
    {"name": "Bug-Jäger",        "bonus_type": "Bugs",     "bonus_value": 0.5, "description": "Findet und behebt Bugs doppelt so schnell."},
    {"name": "Marketing-Experte", "bonus_type": "Marketing", "bonus_value": 0.3, "description": "Erhöht die Effektivität von Marketing."},
]

# ============================================================
# ENTWICKLUNGSPHASEN
# ============================================================
DEV_PHASES = [
    {"name": "Konzept",    "duration_weeks": 1, "primary_sliders": ["Story", "Gameplay"]},
    {"name": "Engine",     "duration_weeks": 1, "primary_sliders": ["KI", "Gameplay"]},
    {"name": "Design",     "duration_weeks": 1, "primary_sliders": ["Grafik", "Welt"]},
    {"name": "Produktion", "duration_weeks": 2, "primary_sliders": ["Gameplay", "Grafik", "Sound"]},
    {"name": "Testing",    "duration_weeks": 1, "primary_sliders": ["KI", "Gameplay"]},
]

# ============================================================
# ZUFALLSEREIGNISSE
# ============================================================
RANDOM_EVENTS = [
    {
        "title": "Spielemesse",
        "text": "Auf der großen Spielemesse präsentierst du dein Studio! Fans steigen.",
        "effect": "fans",
        "value": 500,
    },
    {
        "title": "Wirtschaftsboom",
        "text": "Die Wirtschaft boomt! Spieler kaufen mehr.",
        "effect": "money",
        "value": 15000,
    },
    {
        "title": "Rezession",
        "text": "Eine Wirtschaftskrise trifft die Branche. Umsätze sinken.",
        "effect": "money",
        "value": -10000,
    },
    {
        "title": "Retro-Trend",
        "text": "Retro-Spiele sind plötzlich wieder total angesagt!",
        "effect": "fans",
        "value": 300,
    },
    {
        "title": "Hacker-Angriff",
        "text": "Hacker haben deine Server angegriffen! Reparaturkosten fallen an.",
        "effect": "money",
        "value": -8000,
    },
    {
        "title": "Award-Nominierung",
        "text": "Dein letztes Spiel wurde für einen Award nominiert!",
        "effect": "fans",
        "value": 1000,
    },
    {
        "title": "Steuernachzahlung",
        "text": "Das Finanzamt fordert eine Nachzahlung.",
        "effect": "money",
        "value": -12000,
    },
    {
        "title": "Spende eines Investors",
        "text": "Ein geheimnisvoller Investor glaubt an dein Studio!",
        "effect": "money",
        "value": 25000,
    },
    {
        "title": "Viral-Hit",
        "text": "Ein Video über dein Studio geht viral!",
        "effect": "fans",
        "value": 2000,
    },
    {
        "title": "Server-Ausfall",
        "text": "Dein Online-Service ist ausgefallen. Fans sind verärgert.",
        "effect": "fans",
        "value": -500,
    },
]

# ============================================================
# BÜRO-STUFEN
# ============================================================
OFFICE_LEVELS = [
    {"name": "Garage",          "max_employees": 1,  "cost": 0,       "prestige": 0},
    {"name": "Kleines Büro",    "max_employees": 3,  "cost": 50000,   "prestige": 1},
    {"name": "Mittleres Büro",  "max_employees": 6,  "cost": 200000,  "prestige": 2},
    {"name": "Großes Studio",   "max_employees": 12, "cost": 500000,  "prestige": 3},
    {"name": "Hauptquartier",   "max_employees": 20, "cost": 1500000, "prestige": 5},
]

# ============================================================
# SPIELGRÖSSE
# ============================================================
GAME_SIZES = [
    {
        "name": "Klein",
        "cost_multi": 0.5,
        "time_multi": 0.5,
        "revenue_multi": 0.4,
        "slider_budget": 20,
        "min_employees": 0,
        "description": "Ein kleines Indie-Spiel. Günstig, schnell, aber weniger Umsatzpotenzial.",
    },
    {
        "name": "Mittel",
        "cost_multi": 1.0,
        "time_multi": 1.0,
        "revenue_multi": 1.0,
        "slider_budget": 30,
        "min_employees": 0,
        "description": "Ein normales Spiel. Standardkosten und Umsatz.",
    },
    {
        "name": "Groß",
        "cost_multi": 2.0,
        "time_multi": 1.5,
        "revenue_multi": 2.5,
        "slider_budget": 40,
        "min_employees": 3,
        "description": "Ein großes Spiel. Höhere Kosten, aber deutlich mehr Umsatz. Mindestens 3 Mitarbeiter.",
    },
    {
        "name": "AAA",
        "cost_multi": 4.0,
        "time_multi": 2.0,
        "revenue_multi": 5.0,
        "slider_budget": 50,
        "min_employees": 6,
        "description": "Ein Blockbuster. Enorme Kosten, aber riesiges Umsatzpotenzial. Mindestens 6 Mitarbeiter.",
    },
]

# ============================================================
# MARKETING-KAMPAGNEN
# ============================================================
MARKETING_CAMPAIGNS = [
    {
        "name": "Kein Marketing",
        "cost": 0,
        "sales_multi": 1.0,
        "fan_multi": 1.0,
        "description": "Ohne Marketing-Kampagne.",
    },
    {
        "name": "Kleine Kampagne",
        "cost": 10000,
        "sales_multi": 1.3,
        "fan_multi": 1.2,
        "description": "Online-Werbung und Social Media. Kosten: 10.000 Euro.",
    },
    {
        "name": "Mittlere Kampagne",
        "cost": 40000,
        "sales_multi": 1.8,
        "fan_multi": 1.5,
        "description": "Werbung plus Messe-Auftritt. Kosten: 40.000 Euro.",
    },
    {
        "name": "Große Kampagne",
        "cost": 100000,
        "sales_multi": 2.5,
        "fan_multi": 2.0,
        "description": "TV-Werbung, große Messe, Influencer. Kosten: 100.000 Euro.",
    },
]

# ============================================================
# TRAINING
# ============================================================
TRAINING_OPTIONS = [
    {
        "name": "Workshop",
        "skill_boost": 5,
        "cost": 5000,
        "description": "Ein Workshop. +5 Skill-Punkte auf den Hauptbereich.",
    },
    {
        "name": "Fortbildung",
        "skill_boost": 10,
        "cost": 15000,
        "description": "Eine umfangreiche Fortbildung. +10 Skill-Punkte auf den Hauptbereich.",
    },
    {
        "name": "Experten-Seminar",
        "skill_boost": 20,
        "cost": 40000,
        "description": "Ein Experten-Seminar. +20 Skill-Punkte auf den Hauptbereich.",
    },
]

# ============================================================
# MARKTTRENDS (dynamisch wechselnd)
# ============================================================
TREND_TOPICS = [
    {"topic": "Zombies",     "text": "Zombies sind gerade im Trend!"},
    {"topic": "Weltraum",    "text": "Weltraum-Spiele sind total beliebt!"},
    {"topic": "Fantasy",     "text": "Fantasy erlebt ein Revival!"},
    {"topic": "Cyberpunk",   "text": "Cyberpunk ist der heißeste Trend!"},
    {"topic": "Horror",      "text": "Horror-Spiele boomen gerade!"},
    {"topic": "Sport",       "text": "Sport-Spiele verkaufen sich wie verrückt!"},
    {"topic": "Superheld",   "text": "Superhelden-Spiele sind mega populär!"},
    {"topic": "Piraten",     "text": "Piraten-Spiele sind wieder auf Kurs!"},
]

TREND_GENRES = [
    {"genre": "Action",      "text": "Action-Spiele dominieren die Charts!"},
    {"genre": "RPG",         "text": "RPGs sind extrem beliebt!"},
    {"genre": "Simulation",  "text": "Simulationsspiele sind der neue Hit!"},
    {"genre": "Casual",      "text": "Casual-Games erreichen die breite Masse!"},
    {"genre": "Strategie",   "text": "Strategiespiele erleben einen Boom!"},
]


# ============================================================
# TEMPLATES (E-Mails & Reviews)
# ============================================================
MAIL_TEMPLATES = {
    "bug_report": {
        "subject": "Beschwerde zu {game}",
        "body": "Hallo! Ich habe '{game}' gespielt, aber es stürzt ständig ab. Bitte behebt die Fehler!",
    },
    "fan_praise": {
        "subject": "Ich liebe {game}!",
        "body": "Hey! '{game}' ist fantastisch. Besonders das Thema {topic} gefällt mir sehr gut. Weiter so!",
    }
}

REVIEW_TEMPLATES = {
    "intro": [
        "Wir haben uns '{game}' von {company} genau angesehen.",
        "Endlich ist '{game}' da. Hat sich das Warten gelohnt?",
        "Heute im Test: Das neue Werk von {company} namens '{game}'.",
    ],
    "positive": [
        "Die Kombination aus {topic} und {genre} ist ein genialer Schachzug.",
        "Ein echtes Meisterwerk für alle Fans von {genre}-Spielen.",
        "Selten hat uns ein Spiel mit dem Thema {topic} so gefesselt.",
    ],
    "negative": [
        "Leider wirkt die Verknüpfung von {topic} und {genre} sehr weit hergeholt.",
        "Hier hat man sich bei der Themenwahl deutlich vergriffen.",
        "Thematisch und spielerisch leider eine Enttäuschung.",
    ],
    "conclusion": [
        "Ein Muss für jede Spielesammlung.",
        "Gute Unterhaltung für zwischendurch.",
        "Leider nur Durchschnitt.",
        "Ein Titel, den man getrost ignorieren kann.",
    ]
}


# ============================================================
# HILFSFUNKTIONEN
# ============================================================

def get_compatibility(topic, genre):
    """Gibt Kompatibilitätswert (0-3) zurück."""
    if topic not in TOPIC_GENRE_COMPAT:
        return 1
    genre_index = GENRES.index(genre) if genre in GENRES else 0
    return TOPIC_GENRE_COMPAT[topic][genre_index]


def get_compatibility_text(value):
    """Beschreibender Text für Kompatibilitätswert."""
    texts = {
        0: "Schlechte Kombination",
        1: "Okay Kombination",
        2: "Gute Kombination",
        3: "Super Kombination",
    }
    return texts.get(value, "Unbekannt")


def get_ideal_sliders(genre):
    """Ideale Slider-Verteilung für ein Genre."""
    return GENRE_IDEAL_SLIDERS.get(genre, {s: 5 for s in SLIDER_NAMES})


def get_available_platforms(week):
    """Gibt Plattformen zurück, die in der aktuellen Woche verfügbar sind."""
    current_week = float(week)
    available = []
    for p in PLATFORMS:
        start = float(p["available_week"]) if p["available_week"] is not None else 0.0
        end = float(p["end_week"]) if p["end_week"] is not None else 99999.0
        if start <= current_week <= end:
            available.append(p)
    return available


def get_available_features(week):
    """Gibt Engine-Features zurück, die in der aktuellen Woche erforschbar sind."""
    current_week = int(week)
    return [f for f in ENGINE_FEATURES if int(f["week"]) <= current_week]
