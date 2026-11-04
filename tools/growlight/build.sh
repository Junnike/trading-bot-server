#!/bin/sh
# Builds index.html (standalone, double-click or serve) from app.html (artifact source without the document skeleton).
cd "$(dirname "$0")"
{ printf '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<meta name="color-scheme" content="dark light">\n</head>\n<body>\n'; cat app.html; printf '\n</body>\n</html>\n'; } > index.html
echo "built index.html ($(wc -c < index.html) bytes)"
