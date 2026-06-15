#!/bin/bash
# 書籍 → ChatGPT / Claude
cd ~/ai-dual-sender
source venv/bin/activate
python3 send_to_both.py "$@"
