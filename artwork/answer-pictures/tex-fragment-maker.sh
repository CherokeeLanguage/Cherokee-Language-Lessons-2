#!/bin/bash

set -e
set -o pipefail

trap 'echo ERROR; read a' ERR

cd "$(dirname "$0")"

cwd="$(pwd)"
for x in [0-9][0-9]*; do
	cd "$cwd"
	if [ ! -d "$x" ]; then continue; fi
	cd "$x"
	echo "$cwd"/"$x"
	cp /dev/null 00_fragment.tex
	(
		echo "\\documentclass[avery5371,frame]{flashcards}%%Bus Card"
		echo
		echo "\\usepackage{fontspec}"
		echo "\\setmainfont[Mapping=tex-text]{FreeSerif}"
		echo "\\setsansfont[Mapping=tex-text]{FreeSans}"
		echo "\\setmonofont[Mapping=tex-text]{FreeMono}"
		echo
		echo "\\begin{document}"
		echo
	) >> 00_fragment.tex
	for png in pngs/*; do
		if [ ! -f "$png" ]; then continue; fi
		(
			echo "\\begin{flashcard}{"
			echo "\\includegraphics[width=0.95\\columnwidth,"
			echo "height=.51\\columnwidth,keepaspectratio]"
			echo "{../artwork/answer-pictures/$x/$png}"
			echo "}\\Huge xxx."
			echo "\\end{flashcard}"
			echo
		) >> 00_fragment.tex
	done
	(
		echo
		echo "\\end{document}"
		echo
	) >> 00_fragment.tex	
done
