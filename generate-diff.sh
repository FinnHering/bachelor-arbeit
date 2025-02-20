#!/bin/bash

# Tooling for generating diff between latest tag (or commit if no tag exists)

latexdiff-vc --pdf --git -r "$(git describe --tags --abbrev=0 || echo "HEAD~1")" --dir=tmp/ --config LATEX="pdflatex -interaction=nonstopmode -shell-escape"  --flatten ./thesis.tex