# Snabbstart Guide - SVTPlay-dl Web GUI

## Windows Installation (5 minuter)

### Steg 1: Installera förutsättningar

**Python 3.8+**
1. Gå till https://www.python.org/downloads/
2. Ladda ner senaste versionen
3. Kör installationsprogrammet
4. **VIKTIGT:** Kryssa i "Add Python to PATH"

**ffmpeg**
- Alternativ 1 (Enklast): Installera via Chocolatey
  ```
  choco install ffmpeg
  ```

- Alternativ 2: Ladda ner från https://ffmpeg.org/download.html
  - Extrahera till t.ex. `C:\ffmpeg`
  - Lägg till `C:\ffmpeg\bin` till PATH

### Steg 2: Installera SVTPlay-dl Web GUI

1. Öppna Command Prompt eller PowerShell
2. Navigera till projektmappen
3. Dubbelklicka på `install.bat` ELLER kör:
   ```
   install.bat
   ```

### Steg 3: Starta applikationen

Dubbelklicka på `start.bat` ELLER kör:
```
start.bat
```

### Steg 4: Öppna webbgränssnittet

Öppna din webbläsare och gå till:
```
http://localhost:5000
```

## Använda från andra datorer i nätverket

### Hitta din servers IP-adress:
1. Öppna Command Prompt
2. Kör: `ipconfig`
3. Leta efter "IPv4 Address", t.ex. `192.168.1.100`

### Från andra datorer:
Öppna webbläsare och gå till:
```
http://192.168.1.100:5000
```
(Ersätt med din faktiska IP-adress)

### Öppna brandväggen (om behövs):
1. Windows-sök: "Windows Defender Firewall"
2. "Avancerade inställningar"
3. "Inbound Rules" → "New Rule"
4. Port → TCP → Port 5000
5. "Allow the connection"
6. Ge regeln ett namn

## Grundläggande användning

### Ladda ner ett program:
1. Gå till svtplay.se
2. Hitta programmet du vill ha
3. Kopiera URL:en (t.ex. `https://www.svtplay.se/video/abc123`)
4. Klistra in i Web GUI
5. Välj "Enskilt avsnitt"
6. Klicka "Starta nedladdning"

### Ladda ner en hel säsong:
1. Kopiera URL till valfritt avsnitt i serien
2. Klistra in i Web GUI
3. Välj "Hela säsongen"
4. Klicka "Starta nedladdning"

### Hitta nedladdade filer:
- Filerna finns i mappen `downloads/` i projektmappen
- Eller ladda ner direkt från Web GUI under "Nedladdade filer"

## Felsökning

### "Servern startar inte"
- Kontrollera att Python är installerat: `python --version`
- Kontrollera att alla paket är installerade: kör `install.bat` igen

### "Kan inte nå servern från annan dator"
- Kontrollera IP-adressen är korrekt
- Kontrollera brandväggsinställningar
- Se till att båda datorerna är på samma nätverk

### "Nedladdningen misslyckas"
- Kontrollera att ffmpeg är installerat: `ffmpeg -version`
- Kontrollera att URL:en är korrekt
- Försök med en annan URL

### "Python hittades inte"
- Installera Python från python.org
- Se till att "Add Python to PATH" är ikryssat

## Körning som Windows-tjänst

För att applikationen ska starta automatiskt vid Windows-start:

### Med Task Scheduler:
1. Öppna "Task Scheduler"
2. "Create Basic Task"
3. Name: "SVTPlay-dl GUI"
4. Trigger: "When the computer starts"
5. Action: "Start a program"
6. Program: `C:\path\to\start.bat`
7. Finish

### Med NSSM (Avancerat):
1. Ladda ner NSSM från https://nssm.cc/
2. Kör som administratör:
   ```
   nssm install SVTPlayGUI "C:\path\to\python.exe" "C:\path\to\app.py"
   nssm start SVTPlayGUI
   ```

## Tips och tricks

### Ändra port:
Redigera `config.py`:
```python
PORT = 8080  # Ändra från 5000 till önskad port
```

### Ändra nedladdningsmapp:
Redigera `config.py`:
```python
DOWNLOAD_DIR = 'D:\\Videos\\Downloads'  # Din önskade mapp
```

### Ändra standardkvalitet:
Redigera `config.py`:
```python
DEFAULT_QUALITY = '1080p'  # Istället för 'best'
```

## Hjälp och support

- README: Fullständig dokumentation i `README.md`
- GitHub Issues: Rapportera problem
- svtplay-dl dokumentation: https://svtplay-dl.se/

## Genvägar

- **Starta servern:** `start.bat`
- **Lokal åtkomst:** http://localhost:5000
- **Nätverksåtkomst:** http://[DIN_IP]:5000
- **Nedladdningsmapp:** `downloads/`
