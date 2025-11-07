# SVTPlay-dl Web GUI

Ett webbaserat grafiskt gränssnitt för [svtplay-dl](https://svtplay-dl.se/), verktyget för att ladda ner videos från svenska streamingsajter som **SVT Play** och **TV4 Play**.

## Funktioner

- 📺 Ladda ner enskilda TV-program
- 📦 Ladda ner hela säsonger automatiskt
- 🎯 **Realtidsspårning av avsnitt** - Se exakt vilka avsnitt som laddas ner och vilka som hoppas över
- 🔑 **TV4 Play-stöd** - Fullständigt stöd med token-autentisering och enkla instruktioner
- 💾 **Anpassade nedladdningsmappar** - Välj var dina filer ska sparas med inbyggd mappbläddrare
- 📑 **Sparade profiler** - Spara inställningar för återkommande nedladdningar (perfekt för veckovisa program)
- 🌐 Webbaserat gränssnitt tillgängligt från alla datorer i nätverket
- 📊 Realtidsuppdatering av nedladdningsstatus med detaljerad episodinformation
- 🎬 Kvalitetsval (1080p, 720p, 480p eller bästa tillgängliga)
- 💬 Automatisk nedladdning av undertexter
- 📁 Automatisk organisering i undermappar per serie
- 🔄 Filhantering med möjlighet att ladda ner färdiga filer

## Supporterade sajter

**Primärt fokus och fullt stöd:**
- **SVT Play** (svtplay.se)
- **TV4 Play** (tv4play.se) - Med token-autentisering för premium-innehåll

**Andra svenska streamingsajter som stöds av svtplay-dl:**
- Viafree
- Dplay
- och många fler...

## Installation

### Enkel installation (Windows - Rekommenderat)

**Steg 1:** Installera Python 3.9+
   - Ladda ner från [python.org](https://www.python.org/downloads/)
   - **VIKTIGT**: Bocka i **"Add Python to PATH"** under installationen!

**Steg 2:** Ladda ner projektet
   - Klicka på "Code" → "Download ZIP" på GitHub
   - Packa upp ZIP-filen

**Steg 3:** Kör automatisk installation
   - Dubbelklicka på **`install.bat`**
   - Välj **[A]** för att ladda ner ffmpeg automatiskt (Rekommenderat)
   - Vänta tills installationen är klar

**Steg 4:** Starta programmet
   - Dubbelklicka på **`start.bat`**
   - Öppna webbläsare: **http://localhost:5000**

**Klart!** Ingen PATH-konfiguration eller manuell ffmpeg-installation behövs! 🎉

---

### Manuell installation (alla plattformar)

<details>
<summary><strong>Klicka här för manuell installationsguide</strong></summary>

#### Förutsättningar

1. **Python 3.9 eller senare** (rekommenderat: 3.12+)
   - **Windows**: [python.org](https://www.python.org/downloads/) - Bocka i "Add Python to PATH"
   - **macOS**: `brew install python3`
   - **Linux**: `sudo apt install python3 python3-pip` (Debian/Ubuntu)

2. **ffmpeg** (krävs för video-konvertering)
   - **Windows**: Laddar ner automatiskt via `install.bat` ELLER manuellt från [ffmpeg.org](https://ffmpeg.org/)
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

#### Steg-för-steg installation

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

   **Windows - Enklaste sättet:**
   - Dubbelklicka på `start.bat`

   **Alla plattformar - Manuellt:**
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

### Snabbstart: Ladda ner från SVT Play

1. Gå till SVT Play och hitta programmet du vill ladda ner
2. Kopiera URL:en från adressfältet
3. Klistra in URL:en i "Video-URL" fältet
4. (Valfritt) Ange en anpassad nedladdningsmapp, t.ex. `D:\TV-Serier`
5. Välj "Enskilt avsnitt" eller "Hela säsongen"
6. Välj önskad kvalitet
7. Klicka på "Starta nedladdning"

### Snabbstart: Ladda ner från TV4 Play

1. **Hämta token först** (se [TV4 Play-instruktioner](#tv4-play-och-premium-innehåll) nedan)
2. Gå till TV4 Play och hitta programmet (t.ex. "Bäst i test")
3. Kopiera URL:en (använd programsidan för hela säsongen: `https://www.tv4play.se/program/bast-i-test`)
4. Klistra in URL:en i "Video-URL" fältet
5. Klistra in din **token** i "Token"-fältet
6. Välj "Hela säsongen" för att få alla avsnitt
7. Klicka på "Starta nedladdning"
8. **Se realtidsstatus** - Listan visar vilka avsnitt som laddas ner (✅) och vilka som hoppas över (⏭️)

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

### TV4 Play och premium-innehåll

För att ladda ner från TV4 Play behöver du oftast ange en **refresh token** från din inloggning.

**Enklaste metoden att hämta token:**

1. Öppna [TV4 Play](https://www.tv4play.se/) i din webbläsare och logga in
2. Tryck `F12` för att öppna Developer Tools
3. Gå till fliken **"Console"**
4. Klistra in följande kod och tryck Enter:
   ```javascript
   document.cookie.split("; ").find((row) => row.startsWith("tv4-refresh-token="))?.split("=")[1];
   ```
5. Kopiera den text som visas (utan citattecken)
6. Klistra in i **"Token"**-fältet i GUI:t

**Alternativ metod (manuell sökning):**

1. Öppna TV4 Play och logga in
2. Tryck `F12` → Fliken "Application" (Chrome) eller "Storage" (Firefox)
3. Välj "Cookies" → "https://www.tv4play.se"
4. Hitta cookien som heter **`tv4-refresh-token`**
5. Kopiera värdet (börjar ofta med "ey...")

**Tips:**
- Token är oftast giltig i 30+ dagar
- Spara token i en profil så slipper du kopiera varje gång
- Du kan använda token från vilken dator som helst (den behöver inte vara från nedladdningsservern)
- För gratis innehåll på TV4 Play kan token behövas även om ingen inloggning krävs för att se videon

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

### Webbaserad uppgradering (enklast!)

**Öppna webbläsaren → Scrolla ner → Klicka "Uppgradera system"** 🎉

Den webbaserade uppgraderingen:
1. ✅ Visar nuvarande Python- och svtplay-dl-versioner
2. ✅ Visar git branch och senaste commit
3. ✅ Uppgraderar med ett klick direkt i webbläsaren
4. ✅ Visar real-time progress och loggar
5. ✅ Berättar om du behöver starta om servern

**Perfekt för icke-tekniska användare!** Inget behov av terminal eller kommandon.

### Uppgradering via skript (Windows)

**Dubbelklicka på `upgrade.bat`** - det är allt! 🚀

Skriptet gör automatiskt:
1. ✅ Hämtar senaste uppdateringar från GitHub
2. ✅ Uppgraderar alla Python-paket (inklusive svtplay-dl)
3. ✅ Frågar om du vill starta servern direkt

Se `UPGRADE-GUIDE.md` för mer information.

### Manuell uppdatering (alla plattformar)

#### Uppdatera svtplay-dl

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
