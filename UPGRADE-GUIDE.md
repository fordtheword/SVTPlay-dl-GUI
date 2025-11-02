# Uppgraderingsguide för SVTPlay-dl GUI

## Enkel uppgradering

Dubbelklicka på `upgrade.bat` - det är allt!

Skriptet kommer automatiskt att:
1. ✅ Hämta senaste uppdateringar från GitHub
2. ✅ Uppgradera alla Python-paket
3. ✅ Fråga om du vill starta servern direkt

## Starta servern

**Alternativ 1: Efter uppgradering**
- Svara "J" (Ja) när upgrade.bat frågar

**Alternativ 2: Starta manuellt**
- Dubbelklicka på `start.bat`

**Alternativ 3: Manuellt via CMD**
```cmd
venv\Scripts\python.exe app.py
```

## Felsökning

### "git pull" ger fel
- Kontrollera internetanslutningen
- Se till att du inte har lokala ändringar i projektet

### "pip install" ger fel
- Kör som administratör (högerklicka på upgrade.bat → "Kör som administratör")
- Kontrollera att Python 3.14 är installerat korrekt

### Servern startar inte
- Kontrollera att porten 5000 inte används av annat program
- Kör `start.bat` för att se eventuella felmeddelanden

## Vanliga frågor

**Hur ofta ska jag uppgradera?**
- När du ser nya funktioner eller buggfixar i GitHub
- När nedladdningar slutar fungera (SVT Play har ändrats)
- Minst en gång i månaden rekommenderas

**Tappar jag mina sparade profiler?**
- Nej! Dina sparade profiler (i `profiles.json`) påverkas inte av uppgradering

**Vad händer med mina nedladdningar?**
- Ingenting! Filer i `downloads/` mappen påverkas inte

## Support

Om något går fel:
1. Öppna ett nytt CMD-fönster
2. Kör kommandona manuellt för att se exakt felmeddelande
3. Öppna ett issue på GitHub med felmeddelandet
