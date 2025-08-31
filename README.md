# Python_advanced_course

## 🧾 Årsredovisningspipeline – Översikt

En Python-pipeline som hämtar årsredovisningar från Bolagsverket, extraherar viss ekonomisk metadata, sparar dem som `.joblib`-filer och laddar in dem i en SQLite-databas. Databasen används av användare för att beräkna ekonomiska nyckeltal – utanför pipelinen.

## 📁 Mappstruktur

årsredovisningspipeline/

├── main.py                     # Kör pipelinen  
├── README.md                   # Dokumentation  
├── requirements.txt            # Paketlista  
│  
├── databas.py                  # Initierar SQLite och tabeller  
├── datainsamling.py            # Hämtar årsredovisningar  
├── parser.py                   # Extraherar strukturerad data  
├── loggning.py                 # Loggar händelser och testresultat  
├── test_pipeline.py            # Automatiserade tester  
│  
├── fel.log                     # Loggfil med fel och teststatus  
├── felrapport_YYMMDD.pdf       # PDF med felposter  
└── felrapport_YYMMDD.joblib    # Serialiserad felrapport  


Den här pipelinen är resultatet av många timmar, många misstag – och mycket lärande från andra. Tack till alla som delar sin kunskap, även när den kommer med vassa kanter.
