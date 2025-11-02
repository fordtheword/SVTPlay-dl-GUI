# SVTPlay-dl Web GUI

Ett webbaserat grafiskt gränssnitt för [svtplay-dl](https://svtplay-dl.se/), verktyget för att ladda ner videos från svenska streamingsajter.

## Funktioner

- 📺 Ladda ner enskilda TV-program
- 📦 Ladda ner hela säsonger automatiskt
- 🌐 Webbaserat gränssnitt tillgängligt från alla datorer i nätverket
- 📊 Realtidsuppdatering av nedladdningsstatus
- 🎬 Kvalitetsval (1080p, 720p, 480p eller bästa tillgängliga)
- 💬 Automatisk nedladdning av undertexter
- 📁 Filhantering med möjlighet att ladda ner färdiga filer

## Supporterade sajter

Primärt fokus på:
- SVT Play (svtplay.se)

Andra svenska streamingsajter som stöds av svtplay-dl:
- TV4 Play
- Viafree
- Dplay
- och många fler...

## Installation på Windows

### Förutsättningar

1. **Python 3.8 eller senare**
   - Ladda ner från [python.org](https://www.python.org/downloads/)
   - **VIKTIGT**: Bocka i "Add Python to PATH" under installationen

2. **ffmpeg** (krävs för svtplay-dl)
   - Ladda ner från [ffmpeg.org](https://ffmpeg.org/download.html#build-windows)
   - Eller använd [Chocolatey](https://chocolatey.org/): `choco install ffmpeg`
   - Eller använd [Scoop](https://scoop.sh/): `scoop install ffmpeg`

### Steg-för-steg installation

1. **Ladda ner projektet**
   ```bash
   git clone https://github.com/andersmolausson/SVTPlay-dl-GUI.git
   cd SVTPlay-dl-GUI
   ```

2. **Skapa en virtuell miljö** (rekommenderat)
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Installera beroenden**
   ```bash
   pip install -r requirements.txt
   ```

4. **Starta servern**
   ```bash
   python app.py
   ```

5. **Öppna webbläsaren**
   - På samma dator: `http://localhost:5000`
   - Från andra datorer i nätverket: `http://[DIN_SERVER_IP]:5000`

   För att hitta din server-IP:
   ```bash
   ipconfig
   ```
   Leta efter "IPv4 Address" under din nätverksadapter

## Användning

### Ladda ner ett enskilt program

1. Gå till SVT Play och hitta programmet du vill ladda ner
2. Kopiera URL:en från adressfältet
3. Klistra in URL:en i "Video-URL" fältet
4. Välj "Enskilt avsnitt"
5. Välj önskad kvalitet
6. Klicka på "Starta nedladdning"

### Ladda ner en hel säsong

1. Gå till SVT Play och hitta serien
2. Kopiera URL:en (kan vara från vilket avsnitt som helst i serien)
3. Klistra in URL:en i "Video-URL" fältet
4. Välj "Hela säsongen"
5. Välj önskad kvalitet
6. Klicka på "Starta nedladdning"

### Hämta information

Innan du laddar ner kan du klicka på "Hämta info" för att se:
- Om det är en serie eller ett enskilt program
- Antal tillgängliga avsnitt
- URL:er till alla avsnitt

### Nedladdade filer

- Alla nedladdade filer hamnar i mappen `downloads/`
- Du kan ladda ner filer direkt från webbgränssnittet
- Filer namnges automatiskt med programmets titel och avsnittsnummer

## Konfiguration

Redigera `config.py` för att anpassa:

```python
# Server-inställningar
HOST = '0.0.0.0'  # Lyssna på alla nätverksgränssnitt
PORT = 5000       # Port nummer

# Nedladdningsinställningar
DOWNLOAD_DIR = 'downloads'  # Mapp för nedladdningar
DEFAULT_QUALITY = 'best'    # Standardkvalitet
DEFAULT_SUBTITLE = True     # Ladda ner undertexter som standard
```

## Köra som Windows-tjänst (valfritt)

För att programmet ska starta automatiskt när Windows startar:

### Alternativ 1: Använd Task Scheduler

1. Öppna Task Scheduler
2. Skapa ny uppgift
3. Trigger: "At startup"
4. Action: Starta `python.exe` med argumentet `C:\sökväg\till\SVTPlay-dl-GUI\app.py`

### Alternativ 2: Använd NSSM (Non-Sucking Service Manager)

1. Ladda ner [NSSM](https://nssm.cc/download)
2. Installera tjänsten:
   ```bash
   nssm install SVTPlayGUI "C:\path\to\python.exe" "C:\path\to\SVTPlay-dl-GUI\app.py"
   nssm start SVTPlayGUI
   ```

## Brandväggsinställningar

För att andra datorer ska kunna komma åt servern:

1. Öppna Windows Defender Firewall
2. Klicka på "Avancerade inställningar"
3. Välj "Inbound Rules"
4. Klicka "New Rule"
5. Välj "Port" → "TCP" → Ange port `5000`
6. Tillåt anslutningen
7. Ge regeln ett namn, t.ex. "SVTPlay-dl GUI"

## Felsökning

### "Python hittades inte"
- Kontrollera att Python är installerat: `python --version`
- Se till att Python finns i PATH

### "ffmpeg hittades inte"
- Kontrollera att ffmpeg är installerat: `ffmpeg -version`
- Se till att ffmpeg finns i PATH

### "Kan inte nå servern från annan dator"
- Kontrollera brandväggsinställningar
- Kontrollera att servern körs på `0.0.0.0` (inte `127.0.0.1`)
- Verifiera IP-adressen med `ipconfig`

### "Nedladdningen misslyckas"
- Kontrollera att URL:en är korrekt
- Vissa program kan vara geo-blockerade eller kräva inloggning
- Kontrollera att svtplay-dl fungerar via kommandoraden: `svtplay-dl [URL]`

## Utveckling

Projektstruktur:
```
SVTPlay-dl-GUI/
├── app.py                 # Flask-applikation
├── config.py              # Konfiguration
├── svtplay_handler.py     # svtplay-dl integration
├── requirements.txt       # Python-beroenden
├── templates/
│   └── index.html        # HTML-gränssnitt
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── app.js        # JavaScript-logik
└── downloads/            # Nedladdningsmapp
```

## API Endpoints

Backend erbjuder följande REST API:

- `GET /` - Webbgränssnitt
- `POST /api/info` - Hämta videoinformation
- `POST /api/episodes` - Lista avsnitt i en serie
- `POST /api/download` - Starta nedladdning av enskilt program
- `POST /api/download/season` - Starta nedladdning av säsong
- `GET /api/downloads` - Hämta alla nedladdningar
- `GET /api/downloads/<id>` - Hämta status för specifik nedladdning
- `GET /api/downloads/files` - Lista nedladdade filer
- `GET /downloads/<filename>` - Ladda ner fil

## Licens

Detta projekt är open source och använder samma licens som svtplay-dl.

## Tack till

- [svtplay-dl](https://svtplay-dl.se/) - Det underliggande nedladdningsverktyget
- [Flask](https://flask.palletsprojects.com/) - Webbramverk
- [Bootstrap](https://getbootstrap.com/) - UI-ramverk

## Support

Om du stöter på problem:
1. Kontrollera felsökningssektionen ovan
2. Öppna en issue på GitHub
3. Kontrollera [svtplay-dl dokumentation](https://svtplay-dl.se/)

## Framtida förbättringar

- [ ] Schemaläggning av nedladdningar
- [ ] E-postnotifikationer när nedladdning är klar
- [ ] Support för fler streamingsajter
- [ ] Möjlighet att avbryta pågående nedladdningar
- [ ] Användarkonton och behörighetssystem
- [ ] Mörkt tema
