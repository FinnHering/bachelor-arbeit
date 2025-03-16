# Setze den Compiler auf pdflatex
$pdf_mode = 1;

# Automatische Erkennung von Änderungen und erneutes Kompilieren
$continuous_mode = 1;

# Fehlerprotokollierung
$log_file = 'latexmk.log';

# Zusätzliche Optionen für pdflatex
$pdflatex = 'pdflatex -synctex=1 %O --shell-escape --main-memory=100000000 %S';

@default_files = ('thesis');