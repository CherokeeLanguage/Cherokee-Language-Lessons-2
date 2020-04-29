#!/bin/bash

set -e
set -o pipefail
trap 'echo ERROR; read a' ERR

cd "$(dirname "$0")"

DPI=77 # ? 512 or 513 width ?
DPI=76 # ? 512 or 513 width ?
DPI=90
#DPI=35

cwd="$(pwd)"
PNGS=""
cd "$cwd"
for dir in *; do
	cd "$cwd"
	if [ ! -d "$dir" ]; then continue; fi
	if [ "openclipart.org" = "$dir" ]; then continue; fi
	cd "$dir"
	echo "/pngs/" >> .gitignore
	echo "/jpgs/" >> .gitignore
	mv .gitignore .gitignore.tmp
	cat .gitignore.tmp | sort | uniq > .gitignore
	rm .gitignore.tmp
	if [ ! -d "jpgs" ]; then mkdir "jpgs"; fi
	if [ ! -d "pngs" ]; then mkdir "pngs"; fi
	for jpg in jpgs/*.jpg; do
		if [ ! -f "$jpg" ]; then continue; fi
		svg="$(basename "$jpg"|sed 's/.jpg$/.svg/')"
		png="pngs/$(basename "$jpg"|sed 's/.jpg$/.png/')"
		if [[ "$jpg" == *"_backup.jpg" ]]; then rm "$jpg"; rm  "$png"; fi
		if [ ! -f "$svg" ]; then rm "$jpg"; rm "$png" || true; fi
		if [ "$jpg" -ot "$svg" ]; then rm "$jpg"; rm "$png" || true; fi
	done
	for svg in *.svg; do
		if [[ "$svg" == *"_backup.svg" ]]; then continue; fi
		if [ ! -f "$svg" ]; then continue; fi
		png="pngs/$(echo "$svg"|sed 's/.svg$/.png/')"
		jpg="jpgs/$(echo "$svg"|sed 's/.svg$/.jpg/')"
		if [ -f "$jpg" ]; then continue; fi
		echo "=== $jpg"
		inkscape -z -b=white -y=1.0 -C -d="$DPI" -e="$png" "$svg"
		#900x540
		#750x450
		#gm convert "$png" -gravity center -background white -resize 750x450 -extent 750x450 -bordercolor black -border 5 "$jpg"
		gm convert "$png" -bordercolor black -border 5 "$jpg"
		#rm "$png"
	done
done

cd "$cwd"

exit 0
