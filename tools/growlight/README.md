# Grow Light Planner

One HTML file. No server, no GPU, no install. PPFD heatmap, DLI, uniformity, spectrum mix and cost for any room and any mix of lamps,
with wall reflections, lamp size, asymmetric beams, IES/LDT photometric files, lumens-to-PPF conversion, plant targets, English and Estonian.

## Use it
- **Any computer (Windows, Mac, Linux):** copy `index.html` anywhere and double-click it. Everything runs in the browser. Internet is only used for the two fonts; offline it falls back to the system font.
- **Phone:** open the same file from a server (below) or the published artifact link.
- **DigitalOcean droplet (any size, no GPU):**
  ```
  sudo apt install -y nginx
  sudo mkdir -p /var/www/growlight && sudo cp index.html /var/www/growlight/
  # then point an nginx server block at /var/www/growlight, or for a quick test:
  cd /var/www/growlight && python3 -m http.server 8080      # open http://<droplet-ip>:8080
  ```
  A systemd unit for the quick server is in `deploy/growlight.service` (edit the path, then `systemctl enable --now growlight`).
- Saved plans live in the browser (localStorage) and as downloadable JSON; downloads work when the page is opened as a file or from your own server.

## Build
`app.html` is the source (also what the claude.ai artifact publishes). `./build.sh` wraps it into the standalone `index.html`.

## What it computes
Each lamp is split into several emitters over its real size; each emitter radiates with a Lambertian (120°) or cos-power beam, an elliptical beam (along × across), or the distribution from an IES (LM-63) or LDT (Eulumdat) file, normalised to the lamp's PPF. PPFD at a canopy point = Σ output × beam shape × cos(incidence) / distance². Walls add mirror images of every lamp weighted by reflectance (1–3 bounces). Spectrum per lamp as photon fractions in four bands (blue, green, red, far-red); far-red counts in ePAR, not PPFD. DLI = PPFD × hours × 0.0036. Maintenance factor default 0.9. Tiers multiply power and cost. Lux converter and McCree-weighted YPFD under Geek mode.

## Validation
Headless Chromium run in `scratchpad/shot.js` (not in repo): no console errors at desktop and phone widths; IES upload of a Lambertian table reproduces the analytic beam within 0.1 %; 630 W 6-bar in a 1.2 × 1.2 m Mylar tent at 0.45 m gives 942 µmol/m²/s average, min 643, uniformity 0.68, in line with manufacturer PPFD maps for that class.

## Check against a real offer (04.11.2026)
A vertical-farm offer (two 18 m racks, 30 shelves of 3.7 × 1.08 m, five rows of 150 cm tubes 35 cm above the plants, 10 cm free strip on each long side) was rebuilt in the planner as the "Rack shelf" example: 4 × tri-proof 50 W 6000 K 190 lm/W (tilted 10° outward), 6 × T8 25 W 6000 K in housings, 138 W of 660 nm modules, ends set to "continue" (identical neighbour block), sides open, maintenance factor 0.9.

| case | average | min / max | below 250 |
|---|---|---|---|
| offer document's own model | 309 | 261 / – | 0 % |
| this planner, same lamps, MF 0.9 | 196 | 114 / 235 | 100 % |
| this planner, MF 1.0 | 218 | 127 / 262 | 83 % |
| this planner, MF 1.0, lamps at 25 cm | 244 | 112 / 322 | 42 % |
| this planner, MF 0.9, white strips on both long sides (70 %) | 239 | 157 / 290 | 52 % |

Why the offer's model is high: its average implies that about 85 % of all emitted photons land inside the 88 cm growing strip. A Lambertian lamp 35 cm above a 88 cm wide open shelf can only put 52 % (edge rows) to 78 % (centre row) of its light on that strip; weighted over the five rows that is about 60 %, which is what this planner computes (57 % with the tilt). The rest leaves over the open long sides. A second likely cause is the lumen-to-photon factor: this planner uses CRI 80 measurements (73–76 lux per µmol, i.e. 0.0131–0.0137 µmol/s per lumen, AGi32/Bridgelux/bioRxiv values); using the sunlight factor (54 lux per µmol) would overstate every white LED by 35–40 %. With open sides, 35 cm and 428–488 W per 3.3 m² shelf, 250 µmol/m²/s at every point is not reachable with these lamps; it needs white side strips plus about 25 % more lamp output, or a lower hang height with lensed tubes.
