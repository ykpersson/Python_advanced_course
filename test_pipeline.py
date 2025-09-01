def kör_tester():
    from datetime import datetime
    from joblib import dump
    from loggning import initiera_logg, logga_händelse
    from databas import initiera_databas, insert_data
    from nedladdning import download_files
    from parser import extrahera_data

    testresultat = {
        "status": "PASS",
        "tid": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "moduler": {},
        "kommentar": ""
    }

    initiera_logg()
    logga_händelse("INFO", "🚀 Startar modultestning")

    # Testa databasmodul
    try:
        initiera_databas()
        testresultat["moduler"]["databas"] = "OK"
        logga_händelse("INFO", "✅ Databasmodul testad")
    except Exception as e:
        testresultat["moduler"]["databas"] = f"FAIL: {e}"
        testresultat["status"] = "FAIL"
        logga_händelse("ERROR", f"❌ Databasmodul fel: {e}")

    # Testa nedladdningsmodul
    try:
        filer = download_files()
        testresultat["moduler"]["nedladdning"] = f"OK ({len(filer)} filer)"
        logga_händelse("INFO", f"✅ Nedladdningsmodul testad – {len(filer)} filer")
    except Exception as e:
        testresultat["moduler"]["nedladdning"] = f"FAIL: {e}"
        testresultat["status"] = "FAIL"
        logga_händelse("ERROR", f"❌ Nedladdningsmodul fel: {e}")

    # Testa parsermodul
    try:
        data = extrahera_data()
        testresultat["moduler"]["parser"] = f"OK ({len(data)} poster)"
        logga_händelse("INFO", f"✅ Parsermodul testad – {len(data)} poster")
    except Exception as e:
        testresultat["moduler"]["parser"] = f"FAIL: {e}"
        testresultat["status"] = "FAIL"
        logga_händelse("ERROR", f"❌ Parsermodul fel: {e}")

    # Summering
    if testresultat["status"] == "PASS":
        testresultat["kommentar"] = "Alla moduler testade utan fel"
        logga_händelse("INFO", "✅ Alla tester godkända")
    else:
        testresultat["kommentar"] = "En eller flera moduler misslyckades"
        logga_händelse("ERROR", "❌ Tester misslyckades")

    # Spara testresultat
    datum_str = datetime.now().strftime("%y%m%d")
    dump(testresultat, f"testrapport_{datum_str}.joblib")
    logga_händelse("INFO", f"📦 Testrapport sparad: testrapport_{datum_str}.joblib")
    print(f"🧪 Teststatus: {testresultat['status']}")
    return testresultat  
