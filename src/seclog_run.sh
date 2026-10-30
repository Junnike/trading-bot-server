#!/bin/bash
cd "$(dirname "$0")/.." && while true; do python3 -I src/seclog.py >> data/seclog/err.log 2>&1; sleep 3; done
