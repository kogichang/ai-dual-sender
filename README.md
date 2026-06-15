# AI 雙送工具 (ai-dual-sender)

一鍵同時送檔案給 ChatGPT 和 Claude，省去每天手動上傳兩次的麻煩。

---

## 檔案結構

```
~/ai-dual-sender/
├── run.sh              ← book 指令的啟動腳本
├── run_yt.sh           ← yt 指令的啟動腳本
├── run_class.sh        ← class 指令的啟動腳本
├── send_to_both.py     ← 主程式
├── prompt.txt          ← 書籍用的預設 prompt
├── prompt_yt.txt       ← YouTube 逐字稿用的 prompt
├── prompt_class.txt    ← 開放式課程用的 prompt
├── venv/               ← Python 虛擬環境
└── README.md           ← 本文件
```

---

## 三個指令

| 指令 | 用途 | 資料夾 | Prompt 檔 |
|---|---|---|---|
| `book` | 書籍 md 檔 | `~/Desktop/Claude Cowork/PDFconvert/output/` | `prompt.txt` |
| `yt` | YouTube 逐字稿 | `~/Desktop/Claude Cowork/Obsidian Vault Kogi/Clippings/` | `prompt_yt.txt` |
| `class` | 開放式課程逐字稿 | `~/Desktop/Claude Cowork/Obsidian Vault Kogi/Clippings/` | `prompt_class.txt` |

---

## 使用方式

### 日常使用

打開 Terminal，輸入指令即可：

```bash
book       # 書籍
yt         # YouTube 逐字稿
class      # 開放式課程逐字稿
```

流程：
1. 顯示檔案選單（支援進入子資料夾和返回上層）
2. 選擇檔案後，選擇送給誰：
   - `1. All（ChatGPT + Claude）`
   - `2. ChatGPT`
   - `3. Claude`
3. 自動開啟瀏覽器送出

### 重新登入（登入過期時才需要）

```bash
~/ai-dual-sender/run.sh --login
```

會開啟瀏覽器，手動登入 ChatGPT 和 Claude 後，回到 Terminal 按 Enter 儲存。

### 修改 Prompt

直接編輯對應的 prompt 檔案：

```bash
open ~/ai-dual-sender/prompt.txt         # 書籍 prompt
open ~/ai-dual-sender/prompt_yt.txt      # YouTube prompt
open ~/ai-dual-sender/prompt_class.txt   # 課程 prompt
```

---

## 建置過程紀錄

### 安裝了什麼

1. **Python 虛擬環境 (venv)**
   - 位置：`~/ai-dual-sender/venv/`
   - 不影響系統 Python，所有套件都裝在這裡

2. **Playwright（Python 套件）**
   - 瀏覽器自動化工具，安裝在 venv 內
   - 版本：1.60.0

3. **Chromium（Playwright 下載）**
   - Playwright 自動下載的瀏覽器引擎
   - 位置：`~/Library/Caches/ms-playwright/`
   - 實際運行時使用系統已安裝的 Chrome（`channel="chrome"`）

4. **Shell 別名 (alias)**
   - 在 `~/.zshrc` 中新增了 `book`、`yt`、`class` 三個 alias

5. **瀏覽器登入資料**
   - 位置：`~/.ai-dual-sender-profile/`
   - 儲存 Playwright 瀏覽器的登入 session

### 建置指令（供參考）

```bash
# 1. 建立專案資料夾
mkdir -p ~/ai-dual-sender

# 2. 建立 Python 虛擬環境並安裝 Playwright
cd ~/ai-dual-sender
python3 -m venv venv
source venv/bin/activate
pip install playwright
python -m playwright install chromium

# 3. 在 ~/.zshrc 加入 alias
echo 'alias book="~/ai-dual-sender/run.sh"' >> ~/.zshrc
echo 'alias yt="~/ai-dual-sender/run_yt.sh"' >> ~/.zshrc
echo 'alias class="~/ai-dual-sender/run_class.sh"' >> ~/.zshrc
```

---

## 完整解除安裝

如果要完全移除這個工具，依序執行以下步驟：

### 1. 刪除專案資料夾

```bash
rm -rf ~/ai-dual-sender
```

### 2. 刪除瀏覽器登入資料

```bash
rm -rf ~/.ai-dual-sender-profile
```

### 3. 刪除 Playwright 下載的瀏覽器

```bash
rm -rf ~/Library/Caches/ms-playwright
```

### 4. 移除 shell alias

打開 `~/.zshrc`：

```bash
open ~/.zshrc
```

找到並刪除以下幾行：

```
# --- AI 雙送工具 ---
alias book="~/ai-dual-sender/run.sh"
alias yt="~/ai-dual-sender/run_yt.sh"
alias class="~/ai-dual-sender/run_class.sh"
```

儲存後重新開 Terminal 即可。

### 一鍵完整移除（除了 .zshrc 需手動編輯）

```bash
rm -rf ~/ai-dual-sender ~/.ai-dual-sender-profile ~/Library/Caches/ms-playwright
```

然後手動編輯 `~/.zshrc` 刪除 alias 那幾行。

---

## 已知限制

- ChatGPT 和 Claude 的網頁介面改版時，可能需要更新 `send_to_both.py` 中的 selector
- 登入 session 會過期，需要重新跑 `--login`
- 不使用 API，依賴網頁介面操作

---

## 疑難排解

### 登入過期

```bash
~/ai-dual-sender/run.sh --login
```

### 指令找不到（command not found）

重新開一個 Terminal 視窗，或執行：

```bash
source ~/.zshrc
```

### Playwright 報錯 selector 找不到

ChatGPT 或 Claude 可能改版了，需要更新 `send_to_both.py` 中的 CSS selector。
