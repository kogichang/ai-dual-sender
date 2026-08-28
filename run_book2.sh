#!/bin/bash
# 醫學教科書 → ChatGPT / Claude
cd ~/ai-dual-sender
source venv/bin/activate
python3 send_to_both.py --pick "/Users/kogi/Desktop/Claude Cowork/PDFconvert/output" prompt_medical.txt
