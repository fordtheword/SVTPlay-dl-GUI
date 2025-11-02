# SVTPlay-dl Web GUI

Ett webbaserat grafiskt gränssnitt för [svtplay-dl](https://svtplay-dl.se/), verktyget för att ladda ner videos från svenska streamingsajter.

## Funktioner

- 📺 Ladda ner enskilda TV-program
- 📦 Ladda ner hela säsonger automatiskt
- 💾 **Anpassade nedladdningsmappar** - Välj var dina filer ska sparas
- 📑 **Sparade profiler** - Spara inställningar för återkommande nedladdningar (perfekt för veckovisa program)
- 🌐 Webbaserat gränssnitt tillgängligt från alla datorer i nätverket
- 📊 Realtidsuppdatering av nedladdningsstatus
- 🎬 Kvalitetsval (1080p, 720p, 480p eller bästa tillgängliga)
- 💬 Automatisk nedladdning av undertexter
- 📁 Automatisk organisering i undermappar per serie
- 🔄 Filhantering med möjlighet att ladda ner färdiga filer

## Supporterade sajter

Primärt fokus på:
- SVT Play (svtplay.se)

Andra svenska streamingsajter som stöds av svtplay-dl:
- TV4 Play
- Viafree
- Dplay
- och många fler...

## Installation

### Förutsättningar

1. **Python 3.8 eller senare**
   - Ladda ner från [python.org](https://www.python.org/downloads/)
   - **VIKTIGT (Windows)**: Bocka i "Add Python to PATH" under installationen

2. **ffmpeg** (krävs för svtplay-dl)
   - **Windows**:
     - Ladda ner från [ffmpeg.org](https://ffmpeg.org/download.html#build-windows)
     - Eller använd [Chocolatey](https://chocolatey.org/): `choco install ffmpeg`
     - Eller använd [Scoop](https://scoop.sh/): `scoop install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` (Debian/Ubuntu) eller `sudo dnf install ffmpeg` (Fedora)

3. **Windows Terminal (rekommenderat för Windows-användare)**
   - Moderna kommandotolk med bättre support för Python
   - Installera från [Microsoft Store](https://aka.ms/terminal) eller `winget install Microsoft.WindowsTerminal`
   - Alternativt kan du använda PowerShell eller CMD (äldre)

### Lägg till Python och FFmpeg i PATH

För att kunna köra `python` och `ffmpeg` från kommandoraden måste de finnas i din systems PATH.

#### Windows

**För Python:**
1. Om du glömde bocka i "Add Python to PATH" under installationen:
   - Öppna "Redigera systemets miljövariabler" (sök i Start-menyn)
   - Klicka på "Miljövariabler..." längst ner
   - Under "Systemvariabler", hitta "Path" och klicka "Redigera"
   - Klicka "Ny" och lägg till (ersätt med din Python-sökväg):
     - `C:\Users\[DITT ANVÄNDARNAMN]\AppData\Local\Programs\Python\Python311`
     - `C:\Users\[DITT ANVÄNDARNAMN]\AppData\Local\Programs\Python\Python311\Scripts`
   - Klicka "OK" på alla fönster
   - **Starta om terminalen** för att ändringarna ska träda i kraft

2. Testa att det fungerar:
   ```cmd
   python --version
   ```

**För FFmpeg:**
1. Om du installerade manuellt (inte via Chocolatey/Scoop):
   - Packa upp FFmpeg till en mapp, t.ex. `C:\ffmpeg`
   - Öppna "Redigera systemets miljövariabler"
   - Klicka på "Miljövariabler..."
   - Under "Systemvariabler", hitta "Path" och klicka "Redigera"
   - Klicka "Ny" och lägg till: `C:\ffmpeg\bin`
   - Klicka "OK" på alla fönster
   - **Starta om terminalen**

2. Testa att det fungerar:
   ```cmd
   ffmpeg -version
   ```

**Om du använder Chocolatey eller Scoop** läggs allt automatiskt till i PATH!

#### macOS

PATH hanteras vanligtvis automatiskt på macOS när du använder Homebrew. Om något inte fungerar:

1. Öppna Terminal
2. Redigera din shell-konfiguration:
   ```bash
   nano ~/.zshrc   # För nyare macOS (Catalina+)
   # eller
   nano ~/.bash_profile   # För äldre macOS
   ```

3. Lägg till (om Python/FFmpeg installerades på annan plats):
   ```bash
   export PATH="/usr/local/bin:$PATH"
   ```

4. Spara och ladda om:
   ```bash
   source ~/.zshrc
   ```

#### Linux

PATH hanteras vanligtvis automatiskt när du använder `apt`, `dnf` eller andra pakethanterare. Om något inte fungerar:

1. Öppna Terminal
2. Redigera `.bashrc`:
   ```bash
   nano ~/.bashrc
   ```

3. Lägg till i slutet:
   ```bash
   export PATH="/usr/local/bin:$PATH"
   ```

4. Spara och ladda om:
   ```bash
   source ~/.bashrc
   ```

### Steg-för-steg installation

1. **Ladda ner projektet**
   ```bash
   git clone https://github.com/andersmolausson/SVTPlay-dl-GUI.git
   cd SVTPlay-dl-GUI
   ```

2. **Skapa en virtuell miljö** (rekommenderat)
   ```bash
   python -m venv venv
   ```

3. **Aktivera den virtuella miljön**

   **Windows (PowerShell / Windows Terminal):**
   ```powershell
   venv\Scripts\Activate.ps1
   ```

   **Windows (CMD):**
   ```cmd
   venv\Scripts\activate.bat
   ```

   **macOS / Linux:**
   ```bash
   source venv/bin/activate
   ```

   **Obs!** Om du får felmeddelande om körning av skript i PowerShell, kör:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Installera beroenden**

   Detta installerar Flask, svtplay-dl och alla andra nödvändiga paket:
   ```bash
   pip install -r requirements.txt
   ```

5. **Starta servern**
   ```bash
   python app.py
   ```

6. **Öppna webbläsaren**
   - På samma dator: `http://localhost:5000`
   - Från andra datorer i nätverket: `http://[DIN_SERVER_IP]:5000`

   **Hitta din server-IP:**
   - **Windows**: `ipconfig` (leta efter "IPv4 Address")
   - **macOS**: `ifconfig` (leta efter "inet" under din nätverksadapter)
   - **Linux**: `ip addr` eller `hostname -I`

## Användning

### Snabbstart: Ladda ner ett enskilt program

1. Gå till SVT Play och hitta programmet du vill ladda ner
2. Kopiera URL:en från adressfältet
3. Klistra in URL:en i "Video-URL" fältet
4. (Valfritt) Ange en anpassad nedladdningsmapp, t.ex. `D:\TV-Serier`
5. Välj "Enskilt avsnitt"
6. Välj önskad kvalitet
7. Klicka på "Starta nedladdning"

### Ladda ner en hel säsong

1. Gå till SVT Play och hitta serien
2. Kopiera URL:en (kan vara från vilket avsnitt som helst i serien)
3. Klistra in URL:en i "Video-URL" fältet
4. (Valfritt) Ange nedladdningsmapp
5. Välj "Hela säsongen"
6. Välj önskad kvalitet
7. Klicka på "Starta nedladdning"

### Använda sparade profiler (för återkommande nedladdningar)

**För att spara en profil:**
1. Ange ett **Serie-namn** (t.ex. "På Spåret")
2. Ange **Video-URL** till serien
3. Ange **Nedladdningsmapp** där du vill spara serien (t.ex. `D:\TV-Serier\På Spåret`)
4. Välj kvalitet och övriga inställningar
5. Klicka på **"Spara profil"**

**För att använda en sparad profil:**
1. Välj profilen från **"Sparade serier"**-dropdown
2. Alla inställningar fylls i automatiskt
3. Klicka på **"Starta nedladdning"**

**För att ta bort en profil:**
1. Välj profilen från dropdown
2. Klicka på papperskorgs-ikonen bredvid dropdown

**Användningsfall:**
- Ladda ner nya avsnitt av "På Spåret" varje vecka utan att ange URL och mapp varje gång
- Ha olika profiler för olika serier med olika nedladdningsmappar
- Spara inställningar för återkommande nedladdningar

### Anpassade nedladdningsmappar

Du kan ange var filer ska laddas ner genom att fylla i "Nedladdningsmapp"-fältet:

**Exempel:**
- Windows: `D:\TV-Serier` eller `C:\Users\Anders\Videos\Serier`
- macOS: `/Users/anders/Videos/Serier`
- Linux: `/home/anders/videos/serier`

**Filstruktur:**
Programmet skapar automatiskt undermappar för varje serie:
```
D:\TV-Serier\
├── På Spåret\
│   ├── På Spåret_S01E01_Avsnitt 1.mp4
│   └── På Spåret_S01E02_Avsnitt 2.mp4
└── Aktuellt\
    └── Aktuellt_Kvällens nyheter.mp4
```

**Om inget anges:** Filer hamnar i standardmappen `downloads/` i projektets katalog.

### Hämta information

Innan du laddar ner kan du klicka på "Hämta info" för att se:
- Om det är en serie eller ett enskilt program
- Antal tillgängliga avsnitt
- URL:er till alla avsnitt

### Nedladdade filer

- Filer hamnar i den angivna mappen (eller `downloads/` om ingen mapp angetts)
- Du kan ladda ner filer direkt från webbgränssnittet
- Filer namnges automatiskt med programmets titel och avsnittsnummer
- Varje serie får sin egen undermapp

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

## Underhåll och uppdatering

### Uppdatera svtplay-dl

Du kan uppdatera svtplay-dl till senaste versionen **utan att ändra din kod**:

1. **Aktivera den virtuella miljön** (se installationsinstruktioner ovan)

2. **Uppdatera svtplay-dl:**
   ```bash
   pip install --upgrade svtplay-dl
   ```

3. **Kontrollera versionen:**
   ```bash
   svtplay-dl --version
   ```

4. **Testa att det fungerar** genom att ladda ner ett testprogram i webbgränssnittet

**Varför det fungerar:** Din kod använder svtplay-dl som ett externt kommandoradsverktyg. Så länge kommandoradsgränssnittet förblir kompatibelt (vilket det nästan alltid gör), kommer allt fungera efter uppdatering.

**När du bör uppdatera:**
- När nya funktioner läggs till i svtplay-dl
- När säkerhetsuppdateringar släpps
- När nedladdningar plötsligt slutar fungera (kan bero på ändringar på streamingsajterna)

### Uppdatera alla Python-paket

För att uppdatera alla paket (Flask, svtplay-dl, etc.):

```bash
pip install --upgrade -r requirements.txt
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
- Kontrollera att Python är installerat: `python --version` (eller `python3 --version` på macOS/Linux)
- **Windows**: Se till att Python finns i PATH (bocka i "Add Python to PATH" vid installation)
- **macOS/Linux**: Installera via pakethanterare eller python.org

### "ffmpeg hittades inte"
- Kontrollera att ffmpeg är installerat: `ffmpeg -version`
- **Windows**: Se till att ffmpeg finns i PATH, eller installera via Chocolatey/Scoop
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` eller `sudo dnf install ffmpeg`

### "Kan inte aktivera virtuell miljö" (PowerShell)
- Kör: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Eller använd Windows Terminal istället för gamla PowerShell

### "Kan inte nå servern från annan dator"
- **Alla OS**: Kontrollera att servern körs på `0.0.0.0` (inte `127.0.0.1`) i `config.py`
- **Windows**: Kontrollera brandväggsinställningar (se sektion nedan)
- **macOS**: Kontrollera System Preferences → Security & Privacy → Firewall
- **Linux**: Kontrollera firewall: `sudo ufw allow 5000` (Ubuntu) eller `sudo firewall-cmd --add-port=5000/tcp` (Fedora)
- Verifiera IP-adressen:
  - Windows: `ipconfig`
  - macOS: `ifconfig`
  - Linux: `ip addr` eller `hostname -I`

### "Nedladdningen misslyckas"
- Kontrollera att URL:en är korrekt
- Vissa program kan vara geo-blockerade eller kräva inloggning
- Kontrollera att svtplay-dl fungerar via kommandoraden: `svtplay-dl [URL]`
- Försök uppdatera svtplay-dl: `pip install --upgrade svtplay-dl`

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
