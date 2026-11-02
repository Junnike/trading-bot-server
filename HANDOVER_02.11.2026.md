# Üleandmine (02.11.2026) - server suletakse 04.11.2026

## Mis on GitHubis (haru claude/hopeful-edison-8ytn2d)
- SERVER_RESULTS_09.10.2026.md / SERVER_RESULTS_ALL.md: kõik testid T1-T13 (T8b, T8c, T10, T11 ja T13 lisatud).
- SERVER_RESULTS_T8b_(10.10.2026).md, SERVER_RESULTS_T8c_T10_(10.10.2026).md, SERVER_RESULTS_T11_(10.10.2026).md, results/T13_results.md
- backup/data/ (51 MB): tulemusfailid, tabelid, kuumuskaardid, Kalshi küünlad (candle_parts), poly_resolution.parquet, T8b/T9/T11/T13 tabelid, skalperite ja leadlag tulemused, TradFi turgude nimekirjad, uuringud (RESEARCH_*.md).
- src/: kõik skriptid (tõmbamine, analüüs, backtestid).
- BRIEF.md ja SPEC_T11.md: spetsifikatsioonid ja reeglid.

## Mis EI ole salvestatud (19 GB toorandmed, kõik avalik ja uuesti tõmmatav)
- data/poly (14 GB Polymarket 5-min trades): src/d6_poly.py
- data/binance (1-s Binance): src/d5_binance.py
- data/prints, data/t13/tape (Kalshi trades): src/d3.py, src/t13_pull.py
- data/t11_poly, data/t11_kalshi, data/leadlag: src/t11_*_*.py, src/leadlag_*.py
- Kalshi markets/candles: src/d1.py, d2.py, d4.py
- Sekundilogi (data/seclog): ainult 1957 rida (30.10 05:20-11.02 01:32), augud 2.6 h ja 65 h. Liiga lühike lead-lag'iks, ära kasuta. Logija (src/seclog.py) ei jookse enam.

## Tulemuste kokkuvõte
- KILLED: T1, T2, T3, T4, T5, T9, T10, T11, T13 (maker-pakkumine minutil 7 ei ela täitumisi üle: -0.23c/signaal).
- T8 (Polymarket 5-min maker-redel + pull): ALIVE ainult kitsal kujul; realistlikult +18.7 USD/päev, negatiivne alates augustist. Pole kasutuskõlblik ilma forward-testita.
- Lead-lag TradFi->krüpto: ei ole.
- Uuringud: nullise maker-tasuga börsid ja litsentsid, skalperid (Hyperliquid), Patrick Wieland, TradFi perpide arv börsidel.

## Kuidas sinu arvutis edasi minna
1. Opuse sessioon sinu arvutis loeb GitHubi haru claude/hopeful-edison-8ytn2d (git pull).
2. Automaatsed backtestid: Opus seadistab sinu arvutisse ajastatud käivituse (Python + src/ skriptid), mis jookseb kui arvuti on internetis.
3. Sekundiandmeid logi sinu arvutis (src/seclog.py töötab ka seal), kui tahad lead-lag'i sekundi-tasemel.
4. Server: tühista tellimus enne 05.11.2026 kell 08:00 UTC.
