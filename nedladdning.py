import requests
from bs4 import BeautifulSoup
import os
import zipfile
from datetime import datetime
from joblib import dump
from loggning import initiera_logg, info, fel

BASE_PAGE_URL = "https://vardefulla-datamangder.bolagsverket.se/arsredovisningar/"
BASE_FILE_URL = BASE_PAGE_URL + "2025/"
DOWNLOAD_DIR = "arsredovisningar_2025"
TRACK_FILE = "nedladdade_filer.txt"

def download_files():
    initiera_logg()
    info("Startar nedladdning av årsredovisningar")

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Läs redan nedladdade filer
    downloaded = set()
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "r") as f:
            downloaded = set(line.strip() for line in f)

    # Hämta zip-länkar
    try:
        response = requests.get(BASE_PAGE_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        zip_links = [
            link.get("href") for link in soup.find_all("a")
            if link.get("href", "").startswith("2025/") and link.get("href").endswith(".zip")
        ]
        info(f"Hittade {len(zip_links)} zip-filer")
    except Exception as e:
        fel(f"Fel vid hämtning av länkar: {e}")
        felposter = [{
            "nivå": "ERROR",
            "tid": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "feltyp": "Länkhämtning",
            "modul": "nedladdning.py",
            "funktion": "download_files",
            "meddelande": str(e),
            "kontext": BASE_PAGE_URL
        }]
        dump(felposter, f"felrapport_{datetime.now().strftime('%y%m%d')}_nedladdning.joblib")
        return None

    # Samla felposter
    felposter = []
    antal_lyckade = 0
    antal_hoppade = 0

    for relative_path in zip_links:
        filename = relative_path.split("/")[-1]
        if filename in downloaded:
            info(f"Hoppar över redan nedladdad fil: {filename}")
            antal_hoppade += 1
            continue

        full_url = BASE_FILE_URL + filename
        zip_path = os.path.join(DOWNLOAD_DIR, filename)
        extract_path = os.path.join(DOWNLOAD_DIR, filename.replace(".zip", ""))

        try:
            info(f"Nedladdning startar: {filename}")
            response = requests.get(full_url)
            response.raise_for_status()
            with open(zip_path, "wb") as f:
                f.write(response.content)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            with open(TRACK_FILE, "a") as f:
                f.write(filename + "\n")

            info(f"Extraktion lyckades: {filename}")
            antal_lyckade += 1

        except Exception as e:
            fel(f"{filename}: {e}")
            felposter.append({
                "nivå": "ERROR",
                "tid": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "feltyp": "Nedladdning/Extraktion",
                "modul": "nedladdning.py",
                "funktion": "download_files",
                "meddelande": f"{filename}: {e}",
                "kontext": full_url
            })

    # Summering
    info(f"Körning klar: {antal_lyckade} lyckade, {len(felposter)} fel, {antal_hoppade} hoppade över")
    sammanfattning = {
        "nivå": "INFO",
        "tid": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "feltyp": "Summering",
        "modul": "nedladdning.py",
        "funktion": "download_files",
        "meddelande": f"Körning klar: {antal_lyckade} lyckade, {len(felposter)} fel, {antal_hoppade} hoppade över",
        "kontext": None
    }
    felposter.append(sammanfattning)

    # Spara rapport
    datum_str = datetime.now().strftime("%y%m%d")
    rapport_fil = f"felrapport_{datum_str}_nedladdning.joblib"
    dump(felposter, rapport_fil)
    info(f"📦 Nedladdningsrapport sparad: {rapport_fil}")
    return rapport_fil

# Förhindra att modulen körs vid import
if __name__ == "__main__":
    download_files()



    