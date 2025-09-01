
"""
Modul för hantering av SQLite-databas för årsredovisningsdata.

Skapar en SQLite-databas med tabellen 'arsredovisning' och fördefinierade kolumner.
Tabellen innehåller kolumner enligt REQUIRED_FIELDS, men inga data läggs in vid skapandet.
"""
from sqlite3 import connect, Error
from datetime import datetime
from joblib import dump
import pandas as pd
from loggning import info, fel

DB_PATH = "databas.db"

REQUIRED_FIELDS = [
    "bolagsnamn", "år", "omsättning", "rorelseresultat", "resultat_efter_finansiella",
    "eget_kapital", "totala_tillgangar", "kortfristiga_skulder",
    "omsattningstillgangar", "antal_aktier", "utdelning_total"
]

def create_database() -> None:
    """
    Skapar en SQLite-databas med tabellen 'arsredovisning' och fördefinierade kolumner.
    Tabellen skapas endast om den inte redan finns. Inga data läggs in.
    """
    try:
        with connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS arsredovisning (
                    bolagsnamn TEXT,
                    år INTEGER,
                    omsättning REAL,
                    rorelseresultat REAL,
                    resultat_efter_finansiella REAL,
                    eget_kapital REAL,
                    totala_tillgangar REAL,
                    kortfristiga_skulder REAL,
                    omsattningstillgangar REAL,
                    antal_aktier INTEGER,
                    utdelning_total REAL
                )
            """)
            conn.commit()
            info("🗄️ Databasen och tabellen 'arsredovisning' har skapats.")
    except Error as e:
        fel(f"Fel vid skapande av databas: {e}")

def spara_felrapport(felposter: list[dict], prefix: str) -> str:
    """
    Sparar en lista med felposter till en joblib-fil med ett datumstämplat filnamn.

    Args:
        felposter (list[dict]): En lista med felposter som ska sparas.
        prefix (str): Filnamnsprefix som används före datumet.

    Returns:
        str: Det fullständiga filnamnet som rapporten sparades till.
    """
    datum_str = datetime.now().strftime("%y%m%d")
    filnamn = f"{prefix}_{datum_str}.joblib"
    dump(felposter, filnamn)
    info(f"📄 Rapport sparad: {filnamn}")
    return filnamn

def insert_data(data: dict) -> str:
    """
    Validerar och försöker infoga data i tabellen 'arsredovisning'.

    Args:
        data (dict): En dictionary med nycklar enligt REQUIRED_FIELDS.

    Returns:
        str: Filnamn på felrapporten (även om inga fel uppstod).
    """
    felposter = []

    if set(data.keys()) != set(REQUIRED_FIELDS):
        felmeddelande = "❌ Felaktiga fält – insättning avbruten"
        fel(felmeddelande)
        felposter.append({
            "nivå": "ERROR",
            "tid": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "feltyp": "Validering",
            "modul": "databas.py",
            "funktion": "insert_data",
            "meddelande": felmeddelande,
            "kontext": str(data)
        })
        return spara_felrapport(felposter, "felrapport_insert")

    try:
        with connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO arsredovisning VALUES (
                    :bolagsnamn, :år, :omsättning, :rorelseresultat, :resultat_efter_finansiella,
                    :eget_kapital, :totala_tillgangar, :kortfristiga_skulder,
                    :omsattningstillgangar, :antal_aktier, :utdelning_total
                )
            """, data)
            info(f"✅ Data insatt för {data.get('bolagsnamn')} år {data.get('år')}")
    except Error as e:
        felmeddelande = f"Fel vid insättning: {e}"
        fel(felmeddelande)
        felposter.append({
            "nivå": "ERROR",
            "tid": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "feltyp": "Insättning",
            "modul": "databas.py",
            "funktion": "insert_data",
            "meddelande": str(e),
            "kontext": str(data)
        })

    return spara_felrapport(felposter, "felrapport_insert")

def skapa_databasrapport(filnamn: str | None = None) -> str:
    """
    Hämtar data från tabellen 'arsredovisning' och sparar som joblib-fil.

    Args:
        filnamn (str | None): Valfritt filnamn. Om inget anges skapas ett med dagens datum.

    Returns:
        str: Filnamnet där rapporten sparades.
    """
    try:
        with connect(DB_PATH) as conn:
            df = pd.read_sql_query("SELECT * FROM arsredovisning", conn)
    except Error as e:
        fel(f"Fel vid hämtning av data: {e}")
        return ""

    if not filnamn:
        datum_str = datetime.now().strftime("%y%m%d")
        filnamn = f"databasrapport_{datum_str}.pkl"

    dump(df, filnamn)
    info(f"📦 Databasrapport skapad: {filnamn}")
    return filnamn

def initiera_databas() -> str:
    """
    Initierar databasen genom att skapa tabellen om den inte finns.

    Returns:
        str: Filnamn på eventuell felrapport.
    """
    felposter = []
    try:
        with connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS arsredovisning (
                    bolagsnamn TEXT,
                    år INTEGER,
                    omsättning REAL,
                    rorelseresultat REAL,
                    resultat_efter_finansiella REAL,
                    eget_kapital REAL,
                    totala_tillgangar REAL,
                    kortfristiga_skulder REAL,
                    omsattningstillgangar REAL,
                    antal_aktier INTEGER,
                    utdelning_total REAL
                )
            """)
            info("✅ Databasen initierad eller redan existerande")
    except Error as e:
        felmeddelande = f"Fel vid initiering av databas: {e}"
        fel(felmeddelande)
        felposter.append({
            "nivå": "ERROR",
            "tid": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "feltyp": "Initiering",
            "modul": "databas.py",
            "funktion": "initiera_databas",
            "meddelande": str(e),
            "kontext": DB_PATH
        })

    return spara_felrapport(felposter, "felrapport_databas")
