#!/bin/bash

latexdiff-vc --pdf --git -r "$(git describe --tags --abbrev=0 || echo "HEAD~1")" --flatten ./thesis.tex