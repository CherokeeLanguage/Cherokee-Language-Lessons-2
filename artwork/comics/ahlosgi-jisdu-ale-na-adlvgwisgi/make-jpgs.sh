#!/bin/bash

cd "$(dirname "$0")" || exit 1

export OMP_NUM_THREADS=4

bksize="1325x2050" #200dpi: 6.625x10.25
pgsize="2650x4100" #400dpi: 6.625x10.25
kindlesize="1600x2560"

if [ ! -d "pages.jpg" ]; then mkdir "pages.jpg"; fi

echo "Creating pngs"
for svg in src.svg/*.svg; do
	png="$(echo "$svg"|sed 's/.svg$/.png/')"
	rm "$png"
done
for svg in src.svg/*.svg; do
	png="$(echo "$svg"|sed 's/.svg$/.png/')"
	inkscape -z -b=white -y=1.0 -e "${png}" -d 300 --export-area-page "${svg}"
done

echo "Creating jpgs"
p=0
for png in src.svg/p0*.png; do
	#T="-trim"
	if [ "$p" = 0 ]; then
		unset T
	fi
	if [ ! -f "$png" ]; then continue; fi
	p=$(($p + 1))
	page="$(printf "%03d.jpg" $p)"
	gm convert -background white -flatten $T -quality 70 "$png" "pages.jpg"/"$page"
done

echo "KINDLE jpgs"
if [ ! -d "kindle.jpg" ]; then mkdir "kindle.jpg"; fi
for jpg in pages.jpg/*.jpg; do
	if [ ! -f "$jpg" ]; then continue; fi
	page="$(basename "$jpg")"
	gm convert -background white -quality 70 -resize "$kindlesize" -gravity center -extent "$kindlesize" "$jpg" "kindle.jpg"/"$page"
done

png="src.svg/p-also-by.png"
if [ -f "$png" ]; then
	T="-trim"
	page="$(basename "$png"|sed 's/.png/.jpg/g')"
	gm convert -background white -flatten "${T}" -quality 70 "$png" "pages.jpg"/"$page"
fi

echo "Building raw pages PDF"
gm convert pages.jpg/*.jpg -filter sinc -compress JPEG -quality 10 -resize "$bksize" raw-pages.pdf

echo -n "Done"
sleep 1



