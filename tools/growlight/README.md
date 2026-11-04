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
