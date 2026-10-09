#!/bin/bash
cd /home/user/trading-bot-server
true
python -I src/d4.py KXBTC15M 0 > data/d4_btc_full.log 2>&1
for S in KXETH15M KXSOL15M KXXRP15M KXDOGE15M KXBNB15M KXZEC15M KXNEAR15M KXHYPE15M; do
  python -I src/d4.py $S 60 > data/d4_${S}_60.log 2>&1
done
for S in KXETH15M KXSOL15M KXXRP15M KXDOGE15M KXBNB15M KXZEC15M KXNEAR15M KXHYPE15M; do
  python -I src/d4.py $S 0 > data/d4_${S}_full.log 2>&1
done
