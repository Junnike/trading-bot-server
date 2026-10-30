n signals (cell windows with tape) = 1648; sampled windows = 7700; months = 11; hit-bid EV all signals (T1b replica) = +2.69c, z 3.0, win 82.5%
| model | fill rate | EV/filled c | EV/signal c | n fills | z (cluster day) | win% filled | win% unfilled |
|---|---|---|---|---|---|---|---|
| A optimistic (trade <= bid) | 82.9% | +1.22 | +1.01 | 1366 | 1.2 | 81.0 | 89.7 |
| B trade-through (trade < bid) | 70.4% | -0.99 | -0.70 | 1161 | -0.8 | 78.7 | 91.4 |
| C queue (depth ahead) | unmeasured | unmeasured | unmeasured | unmeasured | unmeasured | unmeasured | unmeasured |

Model B by month (EV/signal c, fill %, n): 2025-12:-1.03(41%,143) 2026-01:-0.95(59%,140) 2026-02:-3.82(71%,146) 2026-03:-4.02(76%,128) 2026-04:-4.51(75%,160) 2026-05:+0.10(72%,145) 2026-06:-1.72(76%,160) 2026-07:+1.52(78%,137) 2026-08:+1.98(76%,162) 2026-09:+3.48(75%,155) 2026-10:+0.65(75%,172)
Months positive (model B EV/signal): 5/11
Last-2-months holdout (2026-09, 2026-10): model B fill 75.2%, EV/filled +2.65c, EV/signal +1.99c, n fills 246, z 1.1
Adverse selection: filled(B) win 78.7% vs unfilled 91.4% (bid mean filled 0.797 vs unfilled 0.799); median contracts traded below bid when filled = 7482
Spread at 7:00: median 1.0c; bid on sub-cent tick (not multiple of 1c): 0.0% of signals; windows with zero trades in (7:02,8:00]: 2.3%
KILL RULE: model B EV/signal -0.70c (need > +0.5) and 5/11 months positive (need >= 8/11) -> DEAD
