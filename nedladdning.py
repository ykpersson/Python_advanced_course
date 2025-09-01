
"""Modul för nedladdning och extraktion av årsredovisningar från Bolagsverket."""

import os
import zipfile
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from joblib import dump

from loggning import initiera_logg, info, fel

TRACK_FILE = "nedladdade_filer.txt"


def extract_zip(zip_path: str, extract_path: str) -> None:
    """Extraherar en ZIP-fil till angiven sökväg."""
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"Ogiltig ZIP-fil: {zip_path}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)


def read_downloaded_files() -> set:
    """Läser in tidigare nedladdade filnamn från spårfilen."""
    if not os.path.exists(TRACK_FILE):
        return set()
    with open(TRACK_FILE, "r", encoding="utf-8") as file:
        return set(line.strip() for line in file)


def zip_links(base_url: str, year: int) -> list:
    """Hämtar alla zip-länkar för ett givet år från Bolagsverkets sida."""
    try:
        response = requests.get(base_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return [
            link.get("href") for link in soup.find_all("a")
            if link.get("href", "").startswith(f"{year}/")
            and link.get("href").endswith(".zip")
        ]
    except requests.exceptions.RequestException as error:
        fel(f"Fel vid hämtning av länkar: {error}")
        raise


def handle_download(
    filename: str,
    full_url: str,
    download_dir: str,
    downloaded: set,
    errors: list
) -> bool:
    """Hanterar nedladdning och extraktion av en enskild zip-fil."""
    if filename in downloaded:
        info(f"↪ Hoppar över redan nedladdad fil: {filename}")
        return False

    zip_path = os.path.join(download_dir, filename)
    extract_path = os.path.join(download_dir, filename.replace(".zip", ""))

    try:
        info(f"⬇ Hämtar: {filename}")
        response = requests.get(full_url, timeout=30)
        response.raise_for_status()
        with open(zip_path, "wb") as file:
            file.write(response.content)

        extract_zip(zip_path, extract_path)

        with open(TRACK_FILE, "a", encoding="utf-8") as file:
            file.write(filename + "\n")

        info(f"✅ Extraktion lyckades: {filename}")
        return True

    except (requests.exceptions.RequestException, zipfile.BadZipFile) as error:
        fel(f"Fel för {filename}: {error}")
        errors.append({
            "nivå": "ERROR",
            "tid": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "feltyp": "Nedladdning/Extraktion",
            "modul": "nedladdning.py",
            "funktion": "handle_download",
            "meddelande": f"{filename}: {error}",
            "kontext": full_url
        })
        return False


def save_report(errors: list, prefix: str) -> str:
    """Sparar felrapporten som en joblib-fil."""
    date_str = datetime.now().strftime("%y%m%d")
    report_file = f"{prefix}_{date_str}_nedladdning.joblib"
    dump(errors, report_file)
    info(f"📄 Nedladdningsrapport sparad: {report_file}")
    return report_file


def download_files(year: int = 2025) -> str:
    """Hämtar och extraherar årsredovisningar för ett givet år."""
    if not isinstance(year, int):
        raise TypeError("Årtalet måste vara ett heltal")

    initiera_logg()
    info(f"Startar nedladdning av årsredovisningar för år {year}")

    base_page_url = (
        "https://vardefulla-datamangder.bolagsverket.se/arsredovisningar/"
    )
    base_file_url = f"{base_page_url}{year}/"
    download_dir = f"arsredovisningar_{year}"
    os.makedirs(download_dir, exist_ok=True)

    downloaded = read_downloaded_files()

    try:
        links = zip_links(base_page_url, year)
        info(f"Hittade {len(links)} zip-filer")
    except requests.exceptions.RequestException as error:
        return save_report([{
            "nivå": "ERROR",
            "tid": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "feltyp": "Länkhämtning",
            "modul": "nedladdning.py",
            "funktion": "download_files",
            "meddelande": str(error),
            "kontext": base_page_url
        }], "felrapport")

    errors = []
    success_count = 0
    skipped_count = 0

    for relative_path in links:
        filename = relative_path.split("/")[-1]
        full_url = base_file_url + filename
        success = handle_download(
            filename,
            full_url,
            download_dir,
            downloaded,
            errors
        )
        if success:
            success_count += 1
        else:
            skipped_count += 1

    info(
        f"Körning klar: {success_count} lyckade, "
        f"{len(errors)} fel, {skipped_count} hoppade över"
    )
    errors.append({
        "nivå": "INFO",
        "tid": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "feltyp": "Summering",
        "modul": "nedladdning.py",
        "funktion": "download_files",
        "meddelande": (
            f"Körning klar: {success_count} lyckade, "
            f"{len(errors)} fel, {skipped_count} hoppade över"
        ),
        "kontext": None
    })

    return save_report(errors, "felrapport")
