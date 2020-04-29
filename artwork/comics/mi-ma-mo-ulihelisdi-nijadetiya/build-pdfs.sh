#!/bin/sh
PDF="Ꮋ-Ꮉ-Ꮌ-#2"

cd "$(dirname "$0")" || exit 1
if [ ! -d panels ]; then mkdir panels; fi
rm panels/*

cp src.panels/*.jpg panels/.

for img in panels/*.jpg; do
	w=$(gm identify "$img" | cut -f 3 -d ' ' | cut -f 1 -d '+'|cut -f 1 -d 'x')
	h=$(gm identify "$img" | cut -f 3 -d ' ' | cut -f 1 -d '+'|cut -f 2 -d 'x')
	nw=$(($w*11/10))
	nh=$(($h*11/10))
	echo "$w:$nw x $h:$nh"
	gm mogrify -gravity center -background white -extent "$nw"x"$nh" -quality 20 "$img"
done

if [ ! -d panels.lyx ]; then mkdir panels.lyx; fi
rm panels.lyx/*
cp src.panels/*.jpg panels.lyx/.

for img in panels.lyx/*.jpg; do
	gm mogrify -quality 20 "$img"
done

gm convert panels.lyx/*.jpg -filter sinc -compress JPEG -quality 30 "$PDF"-ereader.pdf

gm convert panels/*.jpg -filter sinc -compress JPEG -quality 30 tmp.pdf
pdfnup --nup 3x2 --suffix '3x2' tmp.pdf
mv tmp-3x2.pdf "$PDF"-3x2.pdf

pdfnup --no-landscape --nup 1x2 --suffix '1x2' tmp.pdf
pdfbook --short-edge --suffix 'booklet-duplex-short' tmp-1x2.pdf
pdfbook --suffix 'booklet-duplex-long' tmp-1x2.pdf

mv "tmp-1x2-booklet-duplex-long.pdf" "$PDF"-duplex-normal.pdf
mv "tmp-1x2-booklet-duplex-short.pdf" "$PDF"-duplex-short.pdf

rm tmp.pdf
rm tmp-1x2.pdf

