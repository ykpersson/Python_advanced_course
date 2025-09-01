from datetime import datetime
from databas import initiera_databas, skapa_databasrapport
from nedladdning import download_files
from parser import extrahera_data
from loggning import logga_händelse, generera_felrapport, exportera_felrapport_pdf
import subprocess
import sys
from datetime import datetime

from test_pipeline import kör_tester
from loggning import logga_testresultat

# Automatiska programtestning, innan pipelinen startar
testresultat = kör_tester()
logga_testresultat(testresultat)

if testresultat["status"] != "PASS":
    print("❌ Tester misslyckades – pipelinen avbryts")
    sys.exit(1)

# Steg 1: Initiera databas
try:
    initiera_databas()
    logga_händelse("INFO", f"Databasen initierad – {datetime.now().strftime('%H:%M:%S')}")
except Exception as e:
    logga_händelse("ERROR", f"Fel vid databasinitiering: {e}")

# Steg 2: Hämta årsredovisningar
try:
    filer = download_files()
    logga_händelse("INFO", f"Hämtade {len(filer)} årsredovisningar – {datetime.now().strftime('%H:%M:%S')}")
except Exception as e:
    logga_händelse("ERROR", f"Fel vid hämtning: {e}")

# Steg 3: Extrahera data
try:
    data = extrahera_data(filer)
    logga_händelse("INFO", f"Extraherade data från {len(data)} dokument – {datetime.now().strftime('%H:%M:%S')}")
except Exception as e:
    logga_händelse("ERROR", f"Fel vid parsing: {e}")

# Steg 6: Skapa sammanställning
try:
    skapa_sammanställning(resultat)
    logga_händelse("INFO", f"Sammanställning skapad – {datetime.now().strftime('%H:%M:%S')}")
except Exception as e:
    logga_händelse("ERROR", f"Fel vid sammanställning: {e}")

# Steg 7: Generera felrapport
felposter = generera_felrapport()
datum_str = datetime.now().strftime("%y%m%d")
rapportfil = f"felrapport_{datum_str}.joblib"

# Steg 8: Exportera PDF
exportera_felrapport_pdf(rapportfil)
logga_händelse("INFO", f"PDF-export klar – {datetime.now().strftime('%H:%M:%S')}")

print(f"✅ Pipeline färdig – {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Rapport från databasmodulen,  data från nya årsredovisningar
try:
    rapportfil = skapa_databasrapport()
    logga_händelse("INFO", f"📦 Databasrapport skapad: {rapportfil}")
except Exception as e:
    logga_händelse("ERROR", f"❌ Fel vid skapande av databasrapport: {e}")
