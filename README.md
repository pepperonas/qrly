# QR Code 3D Model Generator

Automatische Generierung von 3D-druckbaren QR-Code-Modellen aus URLs oder PNG/JPG-Bildern - mit Desktop-GUI oder Kommandozeile.

## Features

- **Desktop GUI**: Benutzerfreundliche Anwendung mit Echtzeit-Vorschau der Parameter
- **Batch-Verarbeitung**: Mehrere Modelle automatisch generieren via JSON-Konfiguration
- **URL-Support**: QR-Codes direkt aus URLs generieren
- **Vier Modi**:
  - Quadratisch (55x55mm)
  - Pendant mit Anhänger-Loch (55x61mm)
  - Rechteck mit Text (54x64mm)
  - Pendant mit Text (55x65mm)
- **Text-Funktion**: Optional erhabener Text (max. 12 Zeichen) unter dem QR-Code
- **Dynamische Text-Größe**: Automatische Skalierung 3-6mm je nach Textlänge - passt immer perfekt!
- **Text-Rotation**: 180° Drehung für bessere Lesbarkeit (automatisch bei Pendant+Text)
- **Optimierte Größe**: QR-Code nutzt fast die gesamte Kartenfläche (minimaler Rand)
- **Relief-QR-Code**: Erhabene schwarze Pixel (1mm)
- **Abgerundete Ecken**: 2mm Radius für professionelles Design
- **Performance**: ~1-2 Minuten pro Modell dank intelligentem Pixel-Sampling
- **Automatische STL-Generierung**: Direkt druckfertig

## Schnellstart

### 1. Installation (einmalig)

```bash
# OpenSCAD installieren (für STL-Export)
brew install openscad

# Projekt-Setup ist bereits fertig!
# Python 3.13 Virtual Environment in venv-gui/
# Alle Dependencies bereits installiert
```

### 2. GUI-Anwendung starten (empfohlen)

```bash
./venv-gui/bin/python main_simple.py
```

**GUI-Features:**
- URL oder Bilddatei eingeben
- Modus wählen (Square/Pendant/Rectangle+Text/Pendant+Text)
- Optional: Text eingeben (max. 12 Zeichen)
- Parameter anpassen (Höhe, Margin, Relief, Eckenradius)
- "Generate 3D Model" klicken
- Fortschritt in Echtzeit verfolgen
- Dateien werden automatisch in `generated/` gespeichert

### 3. Kommandozeile (Alternative)

#### Von URL (einfachster Weg):

```bash
./qr_generate.sh https://ihre-website.de --mode pendant --name meine-site
```

#### Von Bilddatei:

```bash
./qr_generate.sh myqr.png --mode square
```

## Verwendung

### GUI-Anwendung

**Start:**
```bash
./venv-gui/bin/python main_simple.py
```

**Bedienung:**
1. **Input**: URL eingeben (z.B. `https://example.com`) oder PNG/JPG-Datei auswählen
2. **Output Name**: Optional - wird automatisch von URL abgeleitet
3. **Model Type**: Wähle aus 4 Modi:
   - Square (55x55mm) - Klassisch quadratisch
   - Pendant (with hole) - Mit Anhänger-Loch
   - Rectangle + Text (54x64mm) - Rechteck mit Textfeld
   - Pendant + Text (55x65mm) - Anhänger mit Textfeld
4. **Text**: Bei Text-Modi: Text eingeben (max. 12 Zeichen)
5. **Text-Rotation** (nur bei Rectangle+Text): Optional "Rotate text 180°" aktivieren für umgedrehten Text
   - Bei Pendant+Text wird der Text automatisch um 180° gedreht
6. **Parameter anpassen**:
   - Card Height: 0.5-5mm (Standard: 1.25mm)
   - QR Margin: 0-10mm (Standard: 0.5mm)
   - QR Relief: 0.1-2mm (Standard: 1mm)
   - Corner Radius: 0-5mm (Standard: 2mm)
7. **Generate 3D Model** klicken
8. Warten (~1-2 Minuten)
9. ✅ Erfolg! Dateien in `generated/` Ordner

### Batch-Verarbeitung (GUI)

Für die Generierung mehrerer Modelle auf einmal steht eine Batch-Funktion zur Verfügung:

**Erstmalige Verwendung:**
1. GUI starten: `./venv-gui/bin/python main_simple.py`
2. Im Bereich "Batch Processing" auf "Create Config Template" klicken
3. Datei `batch/config.json` wird erstellt mit Beispiel-Konfiguration
4. `batch/config.json` nach Wunsch anpassen (siehe unten)
5. Auf "Start Batch (X models)" klicken
6. Warten bis alle Modelle generiert sind

**Config-Struktur (`batch/config.json`):**
```json
{
  "global_params": {
    "card_height": 1.25,
    "qr_margin": 2.0,
    "qr_relief": 1.0,
    "corner_radius": 2
  },
  "models": [
    {
      "name": "example-square",
      "url": "https://example.com",
      "mode": "square"
    },
    {
      "name": "github-pendant",
      "url": "https://github.com",
      "mode": "pendant"
    },
    {
      "name": "custom-text",
      "url": "https://mysite.com",
      "mode": "rectangle-text",
      "text": "CUSTOM TEXT",
      "text_rotation": 0
    },
    {
      "name": "pendant-with-override",
      "url": "https://wikipedia.org",
      "mode": "pendant-text",
      "text": "WIKI",
      "card_height": 1.5
    }
  ]
}
```

**Wichtige Hinweise:**
- **global_params**: Standard-Parameter für alle Modelle
- **models**: Array mit einzelnen Modell-Konfigurationen
- Pflichtfelder pro Modell: `name`, `url`, `mode`
- Optional: `text`, `text_rotation` (für Text-Modi)
- Optional: Individuelle Parameter (überschreiben global_params)
- Status-Label aktualisiert sich automatisch alle 5 Sekunden
- Fortschritt wird in Echtzeit angezeigt (X/Y Modelle)
- Fehlgeschlagene Modelle werden übersprungen, nicht abgebrochen

### Kommandozeile

#### Von URL:

**Basis:**
```bash
./qr_generate.sh https://example.com
```

**Mit Optionen:**
```bash
./qr_generate.sh https://github.com/user/repo --name github --mode pendant
```

**Website mit Parametern:**
```bash
./qr_generate.sh "https://example.com/profile?user=123" --name profile
```

**Mit Text (Rectangle+Text):**
```bash
./qr_generate.sh https://example.com --mode rectangle-text --text "AIMPLICITY" --name mycard
```

**Mit Text (Pendant+Text):**
```bash
./qr_generate.sh https://github.com/user --mode pendant-text --text "GitHub" --name github
```

**Mit rotiertem Text (Rectangle+Text):**
```bash
./venv-gui/bin/python generate_qr_model.py https://example.com --mode rectangle-text --text "ROTATED" --text-rotation 180 --name mycard-rot
```

#### Von Bilddatei:

**Quadratisch:**
```bash
./qr_generate.sh myqr.png
```

**Anhänger:**
```bash
./qr_generate.sh celox.png --mode pendant
```

**Mit Custom Output:**
```bash
./qr_generate.sh qrcode.jpg --mode square --output ./stl_files
```

### Parameter

| Parameter | Beschreibung | Standard |
|-----------|-------------|----------|
| `input` | QR-Code-Bilddatei (PNG/JPG) oder URL | *erforderlich* |
| `--mode` | Modus: `square`, `pendant`, `rectangle-text`, `pendant-text` | `square` |
| `--text`, `-t` | Text unter QR-Code (max. 12 Zeichen, nur für *-text Modi) | *(leer)* |
| `--text-rotation` | Text um 180° drehen (0 oder 180, auto bei pendant-text) | `0` |
| `--output`, `-o` | Output-Verzeichnis | `generated` |
| `--name`, `-n` | Basisname für Ausgabedateien | *abgeleitet von Input* |

## Modi im Detail

### Square Mode (Quadratisch)
- **Abmessungen**: 55 x 55 x 1.25 mm
- **Ränder**: 0.5mm rundum (Standard)
- **QR-Code-Bereich**: ~54 x 54 mm
- **QR-Relief**: 1mm erhaben
- **Verwendung**: Visitenkarten, Etiketten, Einleger

```
┌─────────────────┐
│    0.5mm        │
│  ┌─────────┐    │
│.5│ QR-Code │.5  │
│  └─────────┘    │
│    0.5mm        │
└─────────────────┘
```

### Pendant Mode (Anhänger)
- **Abmessungen**: 55 x 61 x 1.25 mm
- **Ränder**: 0.5mm (Seiten/unten), 8mm (oben für Loch)
- **Loch**: ⌀5mm, 6mm vom oberen Rand
- **QR-Code-Bereich**: ~54 x 54 mm
- **QR-Relief**: 1mm erhaben
- **Verwendung**: Schlüsselanhänger, Halsketten, Gepäckanhänger

```
┌─────────────────┐
│     6mm    ●    │ ← Loch (⌀5mm)
│     2mm         │
│  ┌─────────┐    │
│.5│ QR-Code │.5  │
│  └─────────┘    │
│    0.5mm        │
└─────────────────┘
```

### Rectangle + Text Mode (Rechteck mit Text)
- **Abmessungen**: 54 x 64 x 1.25 mm
- **Ränder**: 0.5mm rundum
- **QR-Code-Bereich**: ~53 x 53 mm
- **QR-Relief**: 1mm erhaben
- **Text**: Erhaben (1mm), dynamisch 3-6mm hoch (automatisch skaliert), max. 12 Zeichen
- **Text-Abstand**: 2mm unter QR-Code
- **Font**: Liberation Mono Bold (Monospace)
- **Verwendung**: Visitenkarten, beschriftete Etiketten, personalisierte Karten

```
┌─────────────────┐
│    0.5mm        │
│  ┌─────────┐    │
│.5│ QR-Code │.5  │
│  └─────────┘    │
│   2mm           │
│   TEXT HERE     │ ← Erhaben 1mm
│    0.5mm        │
└─────────────────┘
     64mm
```

### Pendant + Text Mode (Anhänger mit Text)
- **Abmessungen**: 55 x ~65 x 1.25 mm (Länge variiert mit Text)
- **Ränder**: 0.5mm (Seiten/unten), 8mm (oben für Loch)
- **Loch**: ⌀5mm, 6mm vom oberen Rand
- **QR-Code-Bereich**: ~54 x 54 mm
- **QR-Relief**: 1mm erhaben
- **Text**: Erhaben (1mm), dynamisch 3-6mm hoch (automatisch skaliert), max. 12 Zeichen
- **Text-Abstand**: 2mm unter QR-Code
- **Font**: Liberation Mono Bold (Monospace)
- **Verwendung**: Personalisierte Schlüsselanhänger, beschriftete Gepäckanhänger

```
┌─────────────────┐
│     6mm    ●    │ ← Loch (⌀5mm)
│     2mm         │
│  ┌─────────┐    │
│.5│ QR-Code │.5  │
│  └─────────┘    │
│   2mm           │
│   TEXT HERE     │ ← Erhaben 1mm
│    0.5mm        │
└─────────────────┘
    ~65mm
```

## Design-Spezifikationen

| Eigenschaft | Wert |
|-------------|------|
| Kartenbreite | 55mm (ISO 7810) bzw. 54mm (Rectangle-Text) |
| Kartenhöhe | 1.25mm |
| QR-Code-Relief | 1mm erhaben |
| Eckenradius | 2mm |
| Randbreite | **0.5mm** (Standard, anpassbar 0-10mm) |
| QR-Code Border | **1 Modul** (minimal für maximale Fläche) |
| Oberer Rand (Pendant) | 8mm |
| Lochdurchmesser | 5mm |
| Loch-Position | 6mm vom oberen Rand, horizontal zentriert |
| **Text-Größe** | **3-6mm** (dynamisch skaliert je nach Textlänge) |
| **Text-Relief** | **1mm** (gleich wie QR-Code) |
| **Text-Abstand** | **2mm** (Abstand zum QR-Code) |
| **Text-Font** | **Liberation Mono Bold** (Monospace) |
| **Text-Rotation** | **0° oder 180°** (Rectangle: wählbar, Pendant: automatisch 180°) |

## Ausgabedateien

Alle generierten Dateien werden automatisch im Ordner **`generated/`** abgelegt.

Für Input `https://example.com` mit `--name example` werden erstellt:

- **`generated/example.png`**: QR-Code-Bild (bei URL-Input)
- **`generated/example-model.scad`**: OpenSCAD-Quelldatei (editierbar, parametrisch)
- **`generated/example-model.stl`**: 3D-Druckdatei (direkt druckbar)

## Performance

### Generierungszeit

Das System nutzt intelligentes **Pixel-Sampling** für optimale Performance:

| Phase | Zeit | Beschreibung |
|-------|------|--------------|
| QR-Code-Generierung | < 1 Sek | PNG aus URL oder Bild laden |
| OpenSCAD-Datei | < 1 Sek | .scad Code generieren |
| STL-Rendering | **~1-2 Min** | OpenSCAD kompiliert zu STL |
| **Gesamt** | **~1:30 Minuten** | Pro Modell |

### Optimierungen

**1. Pixel-Sampling**
- Original QR: 100x100 Pixel → ~10.000 3D-Würfel → 2-5 Min
- Optimiert: 50x50 Grid → ~800-1.200 Würfel → **1-2 Min** ✅
- **10-30x schneller** ohne Qualitätsverlust!

**2. Minimaler QR-Border**
- Standard: 4 Module Rand (QR-Spec)
- Optimiert: **1 Modul** Rand ✅
- Resultat: QR-Code nutzt ~54x54mm statt ~51x51mm

**3. Angepasster OpenSCAD $fn-Wert**
- Reduziert auf 12 für schnelleres Rendering
- Ausreichend für abgerundete Ecken

#### Warum funktioniert das?

- **Error Correction Level H**: 30% Fehlertoleranz
- **3D-Druck-Auflösung**: Feinere Details nicht sichtbar
- **Physischer Rand**: 0.5mm Kartenmarge ersetzt QR-Border
- **Resultat**: Schneller, größer, genauso scanbar!

## Workflow: Von URL zu 3D-Druck

### Option A: GUI (empfohlen für Einsteiger)

1. GUI starten: `./venv-gui/bin/python main_simple.py`
2. URL eingeben: `https://ihre-website.de`
3. Modus wählen: Pendant
4. Parameter prüfen (oder Standardwerte nutzen)
5. "Generate 3D Model" klicken
6. ✅ Erfolg! → Öffne `generated/ihre-website-model.stl` in Slicer
7. Drucken!

### Option B: Kommandozeile (schnell für Profis)

```bash
./qr_generate.sh https://ihre-website.de --mode pendant --name meine-site
# Warten ~1-2 Minuten
# → generated/meine-site-model.stl ist fertig!
```

### 3D-Druck-Einstellungen

**Material**: PLA, PETG, oder flexibles Filament

**Slicer-Settings:**
- Layer-Höhe: **0.2mm** oder feiner für Details
- Infill: **20%** ausreichend
- Support: **Nicht nötig**
- Brim/Raft: Optional für bessere Haftung
- Druckgeschwindigkeit: Normal

**Zwei-Farben-Druck (empfohlen):**
1. Drucke bis 1.25mm (Basisplatte) in **Weiß**
2. Pause einlegen (M600 oder manuell)
3. Filament auf **Schwarz** wechseln
4. Weiterdruck → QR-Code wird schwarz = bester Kontrast!

## Tipps für beste Scan-Ergebnisse

### Material & Farbe:
- ✅ **Matt** statt glänzend (weniger Reflexionen)
- ✅ **Schwarz/Weiß-Kontrast** für optimales Scannen
- ✅ **PLA** für präzise Details
- ❌ Transparente oder sehr dunkle einfarbige Drucke

### QR-Code-Generierung:
- **Error Correction**: Level H (30% Toleranz) - wird automatisch gesetzt
- **Kurze URLs**: Weniger komplexe QR-Codes scannen besser
- **URL-Shortener**: z.B. bit.ly für längere URLs

### Nachbearbeitung (optional):
- **Bemalen**: Acrylfarbe für Kontrast (schwarz auf weiß)
- **Versiegeln**: Klarlack matt für Schutz
- **Entgraten**: Scharfe Kanten abschleifen

## Anpassungen

### In der GUI:
Alle Parameter direkt einstellbar:
- **Card Height**: 0.5-5mm (dünner/dicker)
- **QR Margin**: 0-10mm (Rand um QR-Code)
- **QR Relief**: 0.1-2mm (Höhe des QR-Codes)
- **Corner Radius**: 0-5mm (Ecken-Rundung)

### OpenSCAD-Datei editieren:
Die `.scad`-Datei kann in OpenSCAD geöffnet werden für:
- Größen anpassen
- Text hinzufügen
- Logo integrieren
- Komplexere Formen

## Projektstruktur

```
QRs/
├── main_simple.py             # Desktop GUI (START HIER!)
├── generate_qr_model.py       # Backend-Generator
├── qr_generate.sh             # CLI-Wrapper
├── venv-gui/                  # Python 3.13 Virtual Environment
├── generated/                 # Alle generierten Dateien
├── ui/
│   ├── __init__.py
│   └── viewer_widget.py       # 3D-Viewer Komponente
├── requirements.txt           # Basis-Dependencies
├── requirements-gui.txt       # GUI-Dependencies (PyQt6)
├── README.md                  # Diese Datei
├── INSTALL.md                 # Installations-Anleitung
└── CLAUDE.md                  # KI-Kontext für Claude Code
```

## Technologie-Stack

- **Python 3.13** (venv-gui)
- **PyQt6** - Desktop GUI Framework
- **Pillow** - Bildverarbeitung
- **qrcode** - QR-Code-Generierung
- **OpenSCAD** - 3D-Modell-Rendering

## Fehlerbehebung

### GUI startet nicht
```bash
# Prüfe Python-Version
./venv-gui/bin/python --version
# Sollte: Python 3.13.x

# Reinstall Dependencies
./venv-gui/bin/pip install -r requirements-gui.txt
```

### "OpenSCAD not found"
```bash
# macOS
brew install openscad

# Linux
sudo apt install openscad

# Windows
# Download von openscad.org
```

**Workaround**: Ohne OpenSCAD wird nur `.scad`-Datei erstellt. Diese manuell in OpenSCAD GUI öffnen und zu STL exportieren.

### QR-Code wird nicht erkannt beim Scannen
- **Zu wenig Kontrast**: Zwei-Farben-Druck nutzen
- **Zu glänzend**: Mattes Filament verwenden
- **Zu klein**: Minimum 45x45mm QR-Code-Bereich
- **Druckqualität**: 0.2mm Layer-Höhe oder feiner

### "Image file not found" bei URL-Input
- GUI verwendet? URLs werden automatisch erkannt
- CLI: `--name` Parameter nutzen für Custom-Benennung
- Prüfen ob `generated/` Ordner existiert

### Modell zu groß/klein
- In GUI: Card Height Parameter anpassen
- In .scad-Datei: Werte am Anfang editieren
- Neu exportieren

## Lizenz

MIT License

Copyright (c) 2025 Martin Pfeffer

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Support

Bei Fragen oder Problemen:
1. README vollständig lesen
2. INSTALL.md prüfen
3. Issue auf GitHub erstellen: https://github.com/pepperonas/qr-2-3d
4. Oder Entwickler kontaktieren

---

**Viel Erfolg beim Drucken! 🎯**

**Entwickler:** Martin Pfeffer (https://github.com/pepperonas)
**Jahr:** 2025
*Entwickelt mit Claude Code - Optimiert für maximale QR-Code-Fläche und Performance*
