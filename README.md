# Python_advanced_course

## 🧾 Årsredovisningspipeline

Ett automatiserat system för att hämta, extrahera och lagra finansiell information från Bolagsverkets årsredovisningar, och är byggt med modulär kod, testdriven utveckling och fullständig loggning, som senare ska användas till att beräkna diverse ekonomiska nyckeltal.

## 📁 Mappstruktur

årsredovisningspipeline/

├── main.py                     # Kör pipelinen  
├── README.md                   # Dokumentation  
├── requirements.txt            # Paketlista  
├── databas.py                  # Initierar SQLite och tabeller  
├── nedladdning.py              # Hämtar årsredovisningar  
├── parser.py                   # Extraherar strukturerad data  
├── loggning.py                 # Loggar händelser och testresultat  
├── test_pipeline.py            # Automatiserade tester  
├── fel.log                     # Loggfil med fel och teststatus  
├── felrapport_YYMMDD.pdf       # PDF med felposter  
└── felrapport_YYMMDD.joblib    # Serialiserad felrapport  
### 🧪 Testmotor

Alla moduler testas automatiskt via `test_pipeline.py`.  
Testresultat sparas som `.joblib`-filer och loggas med status per modul.  
Pipelinen körs endast om testerna godkänns.

## Rapportfiler

- `testrapport_YYMMDD.joblib` – Testresultat från senaste körning
- `databasrapport_YYMMDD.pkl` – Snapshot av hela databasinnehållet
- `felrapport_*.joblib` – Loggade fel från körningen

## Körning

python main.py

Den här pipelinen är resultatet av många timmar, många misstag – och mycket lärande från andra. Tack till alla som delar sin kunskap, även när den kommer med vassa kanter.
