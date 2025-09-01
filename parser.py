import os
from bs4 import BeautifulSoup
from joblib import dump
from loggning import info, fel
from datetime import datetime

EXTRACTED_DIR = "arsredovisningar_2025"
OUTPUT_DIR = "data_2025"

nycklar = {
    "CompanyName": "Bolagsnamn",
    "ReportingPeriodEndDate": "År",
    "RevenueNet": "Omsättning",
    "OperatingProfitLoss": "Rörelseresultat",
    "ProfitLossBeforeTax": "Resultat efter finansiella",
    "Equity": "Eget kapital",
    "Assets": "Totala tillgångar",
    "CurrentLiabilities": "Kortfristiga skulder",
    "CurrentAssets": "Omsättningstillgångar",
    "NumberOfShares": "Antal aktier",
    "ProposedDividendTotal": "Utdelning totalt"
}

obligatoriska = list(nycklar.values())

def extrahera_data():
    info("🔍 Startar parsing av XHTML-filer")
    resultat = []
    felposter = []

    for root, dirs, files in os.walk(EXTRACTED_DIR):
        for file in files:
            if file.endswith(".xhtml"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        soup = BeautifulSoup(f, "lxml")
                        data = {v: None for v in nycklar.values()}

                        for tag in soup.find_all(["ix:nonNumeric", "ix:nonFraction"]):
                            name = tag.get("name")
                            if name in nycklar:
                                value = tag.text.strip()
                                if name == "ReportingPeriodEndDate" and len(value) >= 4:
                                    value = value[:4]
                                data[nycklar[name]] = value

                        saknade = [f for f in obligatoriska if data[f] in [None, "", "null"]]
                        if saknade:
                            felposter.append({
                                "nivå": "WARNING",
                                "tid": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "feltyp": "Saknade fält",
                                "modul": "parser.py",
                                "funktion": "extrahera_data",
                                "meddelande": f"{filepath} saknar: {', '.join(saknade)}",
                                "kontext": filepath
                            })
                            continue

                        resultat.append(data)

                except Exception as e:
                    felposter.append({
                        "nivå": "ERROR",
                        "tid": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "feltyp": "Parsing",
                        "modul": "parser.py",
                        "funktion": "extrahera_data",
                        "meddelande": f"{filepath}: {type(e).__name__}: {e}",
                        "kontext": filepath
                    })

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for rad in resultat:
        try:
            år = rad["År"]
            namn = rad["Bolagsnamn"].replace(" ", "_").replace("/", "_")
            filnamn = f"{år}_{namn}.joblib"
            dump(rad, os.path.join(OUTPUT_DIR, filnamn))
            info(f"✅ Sparade: {filnamn}")
        except Exception as e:
            felposter.append({
                "nivå": "ERROR",
                "tid": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "feltyp": "Sparning",
                "modul": "parser.py",
                "funktion": "extrahera_data",
                "meddelande": f"{rad.get('Bolagsnamn')}: {e}",
                "kontext": str(rad)
            })

    info(f"📦 Parsing klar – {len(resultat)} filer sparade")

    # Summering
    sammanfattning = {
        "nivå": "INFO",
        "tid": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "feltyp": "Summering",
        "modul": "parser.py",
        "funktion": "extrahera_data",
        "meddelande": f"Parsing klar: {len(resultat)} sparade, {len(felposter)} fel",
        "kontext": None
    }
    felposter.append(sammanfattning)

    # Spara rapport
    datum_str = datetime.now().strftime("%y%m%d")
    rapport_fil = f"felrapport_{datum_str}_parser.joblib"
    dump(felposter, rapport_fil)
    info(f"📦 Parserrapport sparad: {rapport_fil}")
    return rapport_fil

# Förhindra att modulen körs vid import
if __name__ == "__main__":
    extrahera_data()


