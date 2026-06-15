#!/bin/bash
# YouTube 逐字稿 → ChatGPT / Claude
cd ~/ai-dual-sender
source venv/bin/activate
python3 send_to_both.py --pick "/Users/kogi/Desktop/Claude Cowork/Obsidian Vault Kogi/Clippings" prompt_yt.txt
