# README

## Build-Anleitung

Zum Kompilieren des LaTeX-Projektes benötigt man latexmk (oder LaTeX skills).


### 1. latexminted konfigurieren aufsetzen

Dieses Projekt hat einige eigene Lexer im Verzeichnis /lexers. Damit latexminted diese ausführen kann, muss eine .latexminted_config im $TEXMFHOME oder $HOME verzeichnis angelegt werden: 

Der erlaubt latexminted die .latexminted_config in diesem Projekt zu verwenden.

Der Inhalt dieser Konfiguration sollte wie folgt aussehen
```
{
    "security": {
        "enable_cwd_config": true
    }
}
```

### 2. LaTeX kompilieren 

Nun muss nur noch `latexmk thesis.tex` ausgeführt werden, und die fertige PDF-Datei liegt im Verzeichnis /out