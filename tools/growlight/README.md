# Grow Light Planner

One HTML file. No server, no GPU, no install. PPFD heatmap, DLI, uniformity, spectrum mix and cost for any room and any mix of lamps,
with wall reflections, lamp size, asymmetric beams, IES/LDT photometric files, lumens-to-PPF conversion, plant targets, English and Estonian.
Four colour themes in the top bar (Ice blue, Moss green, Sand beige, Dusk violet), each with a light and a dark version; the heat-map colours and the PNG export follow the theme, and the choice is remembered by the browser.

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

## Shelf design variants for the 95 m² offer (examples/*.json, load with "Load JSON")
Per 3.7 × 1.08 m shelf, growing area 370 × 88 cm, 16 h/day, maintenance factor 0.9, ends continue into the next block. Prices from the offer (tri-proof 150 cm 27 €, housing 9 €, T8 150 cm 8.50 €, tri-proof 120 cm 26 €, housing 120 cm 8 €, T8 120 cm 6.20 €).

| variant | W / shelf | € / shelf | avg PPFD | min / max | uniformity | kWh/day, 30 shelves |
|---|---|---|---|---|---|---|
| A standard 150 cm, matte covers, 35 cm, open sides | 500 | 264 | 197 | 111 / 236 | 0.56 | 240 |
| B A + clear covers | 500 | 264 | 200 | 112 / 240 | 0.56 | 240 |
| C B + lamps at 25 cm | 500 | 264 | 226 | 99 / 283 | 0.44 | 240 |
| D C + white strips on both long sides (70 %) | 500 | 264 | **260** | 141 / 320 | 0.54 | 240 |
| E D at 30 cm | 500 | 264 | 253 | 157 / 301 | 0.62 | 240 |
| F 6 tri-proof + 4 housings, clear, 25 cm, strips | 500 | 266 | **270** | 137 / 339 | 0.51 | 240 |
| G 120 cm format, 3 per row (6 TP + 9 H), clear, 25 cm, strips | 540 | 340 | 277 | 195 / 305 | 0.70 | 259 |
| H 120 cm format (9 TP + 6 H), clear, 25 cm, strips | 540 | 356 | 288 | 188 / 325 | 0.65 | 259 |
| I D + one extra tri-proof row | 600 | 318 | 322 | 159 / 418 | 0.50 | 288 |
Clear covers alone gain only ~2 %: the diffuser absorbs ~10 % but also narrows the tube's spread, and on an open shelf the wider spread of a bare tube is lost over the sides. The gain appears once white side strips return that light. The standard shelf in the offer has 7 housings (550 W); these variants use 6, so add ~8 % to the averages for the 550 W version.

## Recommended lamp arrangement for the offer (examples/rack_plan.json, picture examples/rack_plan_blocks5-4-3.png)
One shelf of the 18.22 m rack, computed whole (open rack ends, 0.18 m gaps between blocks), growing strip 88 cm, lamps 25 cm above the plants, white strips (70 %) on both long sides, clear covers, maintenance 0.9. Per 3.7 m block, five rows along the length, two lamps of 150 cm per row at x = 0.925 and 2.775 m: housings with 2 × T8 25 W 3000 K at y = 14, 54 and 94 cm; tri-proof 50 W 6000 K at y = 30 and 78 cm tilted 10° outward. Per 2.7 m end block the same pattern with 120 cm lamps at x = 0.75 and 1.95 m (tri-proof 36 W, housings with the measured 18 W 195 lm/W tubes).

| tubes in the 150 cm housings | block 4 avg / min | block 5 avg / min | whole shelf avg | W per shelf |
|---|---|---|---|---|
| 160 lm/W (offer) | 249 / 107 | 256 / 79 | 245 | 2,360 |
| 195 lm/W (measured family) | 279 / 117 | 257 / 79 | 271 | 2,360 |
Staggering the rows (housings at 0.80/2.30 m, tri-proofs at 1.40/2.90 m) leaves the average unchanged and lowers the minimum to 71: keep the even layout. The dark bands (100–150) are the 35 cm between two 150 cm lamps and the block joints; they are inherent to 150 cm lamps in 3.7 m blocks.
