# T8c + T10 (10.10.2026). Scripts src/t8c_crowd.py t8c_an.py t10_events.py; tables data/t8c_tables.txt, data/t10_tables.txt

## Confounders (before verdicts)
- Proxy-vs-real label gap 7.00% in T8b (data/poly_resolution.parquet vs Binance close); both T8c and T10 use the real gamma label.
- Queue position 100% unmeasured: share 0.238 is a scenario only (data/t8b/day_*.npz); competing makers are not observable from D6 trades (data/poly/*_trades.parquet).
- 239-day period (2026-02-12..10-08, data/poly/), Oct = 8 days only; 4 quartile/threshold rules tried = in-sample selection.
- T10 ask proxy = first taker BUY print of the pointed token in +120..+150 s (data/poly/*_trades.parquet), not a quoted ask; 597 of 67946 windows have no such print (excluded from EV only).
- Event dates recalled from public BLS/Fed calendars, NOT verified online (bls.gov pages only show future dates); list may be incomplete/off by a day. 08:30 sample = 21 days.

## T8c
- Reproduction: k2/share0.238/delay2/S1/real label = +18.7 USD/day, z 4.4, 1720 fills/day (data/t8b/day_*.npz) = matches T8b +18.7 (data/t8b_tables.txt). MATCH.
- Table month x vol quartile (USD/day [fills/day]; quartile edges 17.7/25.9/38.5 bp/h, data/t8c_tables.txt; windows per cell listed there):
  Feb Q1..Q4 -0.9/2.9/16.3/35.2 | Mar 0.5/5.3/19.8/41.6 | Apr 1.3/12.6/15.7/25.1 | May 5.0/13.7/13.1/13.1 | Jun -2.9/2.4/3.3/15.4
  Jul -7.7/0.5/2.2/5.9 | Aug -27.2/-2.1/-0.1/-2.3 | Sep -16.8/-8.7/0.1/0.1 | Oct(8d) -43.1/-2.3/-7.0/3.9. Month totals 53.5, 67.1, 54.7, 44.9, 18.3, 0.8, -31.8, -25.4, -48.5.
- Per month fills/day | mean p | win rate | taker ct/window at p<=0.45 (data/t8c_crowd.parquet) | median vol bp/h:
  Feb 1521|.365|.401|36366|38.2; Mar 1473|.369|.414|50287|38.2; Apr 1693|.361|.393|34027|27.0; May 1912|.354|.378|28888|19.5; Jun 1508|.367|.380|31931|32.6
  Jul 1801|.358|.359|29305|21.9; Aug 1905|.348|.332|20159|18.3; Sep 1800|.349|.335|18373|22.4; Oct 1927|.346|.321|17303|18.7. Win rate - p: +3.5 pts Feb, -1.5 pts Aug, -2.5 pts Oct (adverse selection grew).
- Attribution: median vol fell 38 -> 18-22 bp/h and fills/day rose 1500 -> 1900 (fewer pulls/more fills at low vol), but crowding proxy (taker ct/window <=0.45) FELL 36-50k -> 17-20k, so no crowding signal. Yet within Q3/Q4 vol the edge also decayed (Q4: +35 Feb -> -2 Aug, +0.1 Sep) so vol alone does not explain it. Verdict: VOL-DRIVEN IN PART (Q1 collapse), residual decay UNMEASURED (queue/competing makers invisible in trades); crowding by taker volume not supported.
- REVIVE RULE (assumption: in-sample, share 0.238, fixed ladder): "trade only when 60-min pre-open vol >= 25.9 bp/h" = +23.2 USD/day, z 9.6, 7/9 months positive (78%, data/t8c_tables.txt); crowd<=Y rules fail (best -2.6 USD/d). But same rule in Aug-Oct = -1.39 USD/d, z -0.8 (Q4 only -0.54, z -0.5), and high-vol windows are only 25-50% of windows. Formal rule passes, practical status: DEAD for the current regime (zero edge Aug-Oct even in high vol); needs a forward check.

## T10 (data/t10_tables.txt; 5-min BTC windows, +2 min Binance move direction (data/binance/) vs real label (data/poly_resolution.parquet), EV at D6 ask proxy, fee 0.07p(1-p), day-cluster bootstrap 2000)
- Dates used 08:30 NY: CPI 02-13,03-11,04-10,05-12,06-10,07-14,08-12,09-11,10-14(future, no data); NFP 02-11,03-06,04-03,05-08,06-05,07-02,08-07,09-04,10-02; FOMC 03-18,04-29,06-17,07-29,09-16.
- Type: n | hit | EV c/share (z) | months+ : 08:30 data days 105 | .724 | -4.05 (-1.1) | 4/9; 09:30 weekdays 854 | .739 | -0.48 (-0.3) | 3/9
- CME 18:00 Sun-Fri 1018 | .707 | -3.26 (-2.4) | 3/9; 00:00 UTC 1176 | .697 | -3.72 (-2.8) | 1/9; OTHER 64793 | .714 | -0.91 (-4.2) | 0/9; ALL 67946 | .714 | -1.00 | 0/9.
- Hit rate is 70-74% everywhere (event windows not different from others); the Poly ask already prices it in, EV negative in all types. Side check FOMC 14:00 NY n=25 EV +3.3 z 0.9 (not significant).
- VERDICT T10: KILLED (z<2, <60% months positive in all four event types; 08:30 n=105 borderline).
