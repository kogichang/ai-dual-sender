#!/bin/bash
# 安裝 send_to_both.py 的相依套件

echo "📦 安裝 Playwright..."
pip3 install playwright

echo ""
echo "📦 下載 Chromium 瀏覽器引擎..."
python3 -m playwright install chromium

echo ""
echo "✅ 安裝完成！"
echo ""
echo "接下來請執行："
echo "  1. 首次登入:  python3 ~/ai-dual-sender/send_to_both.py --login"
echo "  2. 送出檔案:  python3 ~/ai-dual-sender/send_to_both.py <md檔> \"你的prompt\""
