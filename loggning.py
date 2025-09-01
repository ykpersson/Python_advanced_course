# loggning.py
import logging
import os
from datetime import datetime
from joblib import dump,load

def logga_testresultat(testresultat: dict, loggfil="fel.log"):
    """
    Loggar testresultat från test_pipeline till loggfilen.
    """
    tid = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = testresultat.get("status", "UNKNOWN")
    exit_code = testresultat.get("exit_code", -1)

    with open(loggfil, "a") as f:
        f.write(f"{tid} INFO: 🧪 Teststatus: {status} (exit code: {exit_code})\n")



def initiera_logg(filnamn="fel.log"):
    logging.basicConfig(
        filename=filnamn,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def info(meddelande):
    logging.info(meddelande)

def fel(meddelande):
    logging.error(meddelande)

def varning(meddelande):
    logging.warning(meddelande)


def generera_felrapport(loggfil="fel.log"):
    if not os.path.exists(loggfil):
        print("❌ Ingen loggfil hittades.")
        return []

    felposter = []

    with open(loggfil, "r", encoding="utf-8") as f:
        for rad in f:
            delar = rad.strip().split(" - ")
            if len(delar) < 3:
                continue

            tidsstämpel, nivå, meddelande = delar[0], delar[1], delar[2]

            if nivå not in ["ERROR", "WARNING"]:
                continue

            post = {
                "nivå": nivå,
                "tid": tidsstämpel.split(",")[0],
                "feltyp": None,
                "modul": None,
                "funktion": None,
                "meddelande": meddelande,
                "kontext": None
            }

            # Försök extrahera feltyp
            if ":" in meddelande:
                post["feltyp"] = meddelande.split(":")[0].strip()

            # Försök hitta modul/funktion
            if "i" in meddelande and ".py" in meddelande:
                delar = meddelande.split("i")
                for d in delar:
                    if ".py" in d:
                        post["modul"] = d.strip().split()[0]
                        break

            if "()" in meddelande:
                post["funktion"] = meddelande.split("()")[0].split()[-1]

            # Kontext (om något extra finns)
            if "Data" in meddelande or "Fil" in meddelande:
                post["kontext"] = meddelande

            felposter.append(post)

    datum_str = datetime.now().strftime("%y%m%d")
    filnamn = f"felrapport_{datum_str}.joblib"
    dump(felposter, filnamn)
    print(f"📦 Felrapport sparad som '{filnamn}' ({len(felposter)} poster)")
    return felposter

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from joblib import dump
from datetime import datetime

def exportera_felrapport_pdf(pkl_fil):
    try:
        with open(pkl_fil, "rb") as f:
            felposter = load(f)
    except Exception as e:
        print(f"❌ Kunde inte läsa '{pkl_fil}': {e}")
        return

    datum_str = datetime.now().strftime("%y%m%d")
    pdf_fil = f"felrapport_{datum_str}.pdf"
    doc = SimpleDocTemplate(pdf_fil, pagesize=A4)
    styles = getSampleStyleSheet()
    innehåll = []

    # Rubrik
    innehåll.append(Paragraph(f"Felrapport – {datum_str}", styles["Title"]))
    innehåll.append(Spacer(1, 12))

    # Tabellrubriker
    tabell_data = [["Tid", "Nivå", "Feltyp", "Modul", "Funktion", "Meddelande"]]

    for post in felposter:
        rad = [
            post.get("tid", ""),
            post.get("nivå", ""),
            post.get("feltyp", ""),
            post.get("modul", ""),
            post.get("funktion", ""),
            post.get("meddelande", "")[:80] + "..." if len(post.get("meddelande", "")) > 80 else post.get("meddelande", "")
        ]
        tabell_data.append(rad)

    tabell = Table(tabell_data, repeatRows=1)
    tabell.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    innehåll.append(tabell)
    doc.build(innehåll)
    print(f"📄 PDF skapad: {pdf_fil}")

# Förhindra att modulen körs vid import
if __name__ == "__main__":
    
