import sqlite3
import os
from datetime import datetime
from joblib import dump
from loggning import info, fel

DB_PATH = "arsredovisning.db"

def connect():
    return sqlite3.connect(DB_PATH)

def initiera_databas():
    felposter = []

    try:
        conn = connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='arsredovisning'
        """)
        finns = cursor.fetchone()

        if not finns:
            cursor.execute("""
                CREATE TABLE arsredovisning (
                    bolagsnamn TEXT,
                    år TEXT,
                    omsättning TEXT,
                    rorelseresultat TEXT,
                    resultat_efter_finansiella TEXT,
                    eget_kapital TEXT,
                    totala_tillgangar TEXT,
                    kortfristiga_skulder TEXT,
                    omsattningstillgangar TEXT,
                    antal_aktier TEXT,
                    utdelning_total TEXT
                )
            """)
            conn.commit()
            info("📦 Databasen skapades")
        else:
            info("✅ Databasen finns redan")

        info("Databasstatus: skapad eller redan existerande – redo för insättning")
        conn.close()

    except Exception as e:
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

    # Summering
    sammanfattning = {
        "nivå": "INFO",
        "tid": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "feltyp": "Summering",
        "modul": "databas.py",
        "funktion": "initiera_databas",
        "meddelande": f"Initiering klar med {len(felposter)} fel",
        "kontext": DB_PATH
    }
    felposter.append(sammanfattning)

    # Spara rapport
    datum_str = datetime.now().strftime("%y%m%d")
    rapport_fil = f"felrapport_{datum_str}_databas.joblib"
    dump(felposter, rapport_fil)
    info(f"📦 Databasrapport sparad: {rapport_fil}")
    return rapport_fil

def insert_data(data: dict):
    felposter = []

    if not isinstance(data, dict) or len(data) != 11:
        felmeddelande = "❌ Felaktig datainmatning – insättning avbruten"
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
    else:
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO arsredovisning VALUES (
                    :bolagsnamn, :år, :omsättning, :rorelseresultat, :resultat_efter_finansiella,
                    :eget_kapital, :totala_tillgangar, :kortfristiga_skulder,
                    :omsattningstillgangar, :antal_aktier, :utdelning_total
                )
            """, data)
            conn.commit()
            conn.close()
            info(f"✅ Data insatt för {data.get('bolagsnamn', 'okänt bolag')} år {data.get('år', 'okänt år')}")
        except Exception as e:
            felmeddelande = f"❌ Fel vid insättning i databasen: {e}"
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

    # Summering
    sammanfattning = {
        "nivå": "INFO",
        "tid": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "feltyp": "Summering",
        "modul": "databas.py",
        "funktion": "insert_data",
        "meddelande": f"Insättning klar med {len(felposter)} fel",
        "kontext": None
    }
    felposter.append(sammanfattning)

    # Spara rapport
    datum_str = datetime.now().strftime("%y%m%d")
    rapport_fil = f"felrapport_{datum_str}_insert.joblib"
    dump(felposter, rapport_fil)
    info(f"📦 Insättningsrapport sparad: {rapport_fil}")
    return rapport_fil

# Förhindra att modulen körs vid import
if __name__ == "__main__":
    initiera_databas()
import sqlite3
import pandas as pd
from joblib import dump
from datetime import datetime

#skapa databasrapport av data från inlästa årsedovisningar
def skapa_databasrapport(filnamn=None):
    """
    Skapar en .pkl-dump av hela databasinnehållet.

    Parametrar:
        filnamn (str): Valfritt filnamn. Om None används datumbaserat namn.

    Returnerar:
        str: Sökvägen till sparad rapportfil
    """
    conn = sqlite3.connect("arsredovisning.db")
    df = pd.read_sql_query("SELECT * FROM arsredovisning", conn)
    conn.close()
  
    if not filnamn:
        datum_str = datetime.now().strftime("%y%m%d")
        filnamn = f"databasrapport_{datum_str}.pkl"

    dump(df, filnamn)
    return filnamn


