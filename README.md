# Svenska hitmakare

Svenska låtskrivare, producenter och artister bakom internationella hits. `index.html` är hela sidan i en fil, utan externa anrop (typsnitt och d3 är inbyggda).

## Hämta till egen webbserver

```sh
curl -fsSL https://raw.githubusercontent.com/hegunu/swehit/main/index.html -o /var/www/hitmakare/index.html
```

## Bygga om

```sh
python3 -I build/build.py data/svenska_hitmakare.json unknown.txt
python3 -I build/render.py template.html data/svenska_hitmakare.json page.html
python3 -I build/webpage.py page.html selfhost index.html
```

Nya låtar läggs till som rader i `raw/*.tsv` (år, titel, artist, låtskrivare, producenter, placering, källa). Svenska personer matchas mot listan i `build/swedes.py`, `build/extra_swedes.json` och `raw/*.acts.txt`.
Utgivningsdatum (för sortering inom samma år) ligger i `raw/dates.tsv` (titel, artist, YYYY-MM-DD).

Data: `data/latar.csv`, `data/personer.csv`.

Kontakt: hitmakare@hegu.nu
