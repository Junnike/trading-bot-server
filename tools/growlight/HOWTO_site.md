# Grow Light Planner: getting it onto your site

The planner is one file, `index.html`, built from `app.html` with `build.sh`. No server code, no database. Anything that can serve a static file can host it.

## 1. Put it online (pick one)

**GitHub Pages, free, already prepared**
1. Open https://github.com/Junnike/trading-bot-server/settings/pages
2. Source: Deploy from a branch. Branch: `claude/eloquent-wright-h4abms`. Folder: `/docs`. Save.
3. After a minute: https://junnike.github.io/trading-bot-server/ is the chooser page (new planner + old calculator, with a comparison), and https://junnike.github.io/trading-bot-server/planner/ is the planner itself.

**Replace the old calculator at its current address**
1. Open the repo `kasvuvalgus-planeerija` on GitHub.
2. Upload `tools/growlight/index.html` from this repo over its `index.html` (Add file, Upload files, commit).
3. https://junnike.github.io/kasvuvalgus-planeerija/ now opens the new planner. To keep the old one as well, upload it first under another name, for example `vana.html`.

**Your own server (droplet, nginx)**
```
sudo mkdir -p /var/www/growlight && sudo cp tools/growlight/index.html /var/www/growlight/
# nginx: root /var/www/growlight; or quick test: cd /var/www/growlight && python3 -m http.server 8080
```
`deploy/growlight.service` in this repo is a systemd unit for the quick-test server.

## 2. Link it from the shop (celepaws.com, Tipsik)
1. Admin, Pages. New page: name `Kasvuvalguse planeerija`, "Show link in": header menu, enabled.
2. Add a Text block with the planner address from step 1. Save.
3. Check the storefront top bar. If the address is not clickable, the shop's page editor needs a link block; that is a change to the shop code (friend), not to the planner.
4. Product descriptions: add a line `Arvuta oma ruumi valgus: <address>` to each grow-light product. Through the shop connector Claude can do this for all products at once.

## 3. Update later
- Edit `tools/growlight/app.html`, run `sh tools/growlight/build.sh`, commit, push. GitHub Pages updates itself within a minute; the droplet needs the new `index.html` copied again.
- The chooser page is `docs/index.html`; the planner copy under `docs/planner/` must be refreshed with `cp tools/growlight/index.html docs/planner/index.html` after a build.

## 4. Local use
Double-click `index.html`. Plans are saved in the browser; use "Save JSON" to keep one as a file. Example plans are in `examples/`.
