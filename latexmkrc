# Setze den Compiler auf pdflatex
$pdf_mode = 1;

# Automatische Erkennung von Änderungen und erneutes Kompilieren
$continuous_mode = 1;

# BibTeX
$bibtex_use = 2;

# Fehlerprotokollierung
$log_file = 'latexmk.log';

# Zusätzliche Optionen für pdflatex
$pdflatex = 'pdflatex -interaction=nonstopmode -synctex=1 %O --shell-escape %S';

# Setze das Ausgabeverzeichnis
$out_dir = '.out';

@default_files = ('thesis.tex');

set_tex_cmds( '--shell-escape %O %S' );