#!/usr/bin/env python3
"""
send_to_both.py - 同時送檔案和 prompt 給 ChatGPT 和 Claude

用法:
  首次登入:  python3 send_to_both.py --login
  送出檔案:  python3 send_to_both.py <md檔路徑>                    ← 使用預設 prompt.txt
  送出檔案:  python3 send_to_both.py <md檔路徑> <prompt檔路徑>     ← 使用自訂 prompt 檔

範例:
  python3 send_to_both.py ~/Books/my_book.md
  python3 send_to_both.py ~/Books/my_book.md ~/prompts/summarize.txt
"""

import asyncio
import sys
import os
from playwright.async_api import async_playwright

# 瀏覽器登入資料儲存位置（登入一次之後就會記住）
PROFILE_DIR = os.path.expanduser("~/.ai-dual-sender-profile")

# 預設 prompt 檔案位置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PROMPT_FILE = os.path.join(SCRIPT_DIR, "prompt.txt")


def load_prompt(prompt_arg: str = None) -> str:
    """從檔案載入 prompt。沒指定就用預設的 prompt.txt"""
    if prompt_arg:
        prompt_file = os.path.abspath(prompt_arg)
    else:
        prompt_file = DEFAULT_PROMPT_FILE

    if not os.path.exists(prompt_file):
        print(f"❌ Prompt 檔案不存在: {prompt_file}")
        if prompt_file == DEFAULT_PROMPT_FILE:
            print(f"   請先編輯預設 prompt: {DEFAULT_PROMPT_FILE}")
        sys.exit(1)

    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt = f.read().strip()

    if not prompt:
        print(f"❌ Prompt 檔案是空的: {prompt_file}")
        sys.exit(1)

    return prompt


async def login_mode():
    """首次使用：開啟瀏覽器讓使用者手動登入 ChatGPT 和 Claude"""
    print("\n🔐 登入模式")
    print("即將開啟瀏覽器，請分別登入 ChatGPT 和 Claude。\n")

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            channel="chrome",
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )

        # 開啟 ChatGPT
        page1 = await context.new_page()
        await page1.goto("https://chat.openai.com/")
        print("📌 第 1 個分頁：請登入 ChatGPT")

        # 開啟 Claude
        page2 = await context.new_page()
        await page2.goto("https://claude.ai/")
        print("📌 第 2 個分頁：請登入 Claude")

        print("\n✅ 兩個網站都登入完成後，回到這裡按 Enter 儲存登入狀態...")
        input()
        await context.close()

    print("💾 登入資訊已儲存！之後使用不需要重新登入。\n")


async def send_to_both(file_path: str, prompt: str, target: str = "both"):
    """送檔案和 prompt 給 ChatGPT 和/或 Claude
    target: "both" | "chatgpt" | "claude"
    """

    abs_file_path = os.path.abspath(file_path)
    if not os.path.exists(abs_file_path):
        print(f"❌ 檔案不存在: {abs_file_path}")
        sys.exit(1)

    target_label = {"both": "ChatGPT + Claude", "chatgpt": "ChatGPT", "claude": "Claude"}
    file_size = os.path.getsize(abs_file_path)
    print(f"\n📄 檔案: {os.path.basename(abs_file_path)} ({file_size / 1024:.0f} KB)")
    print(f"💬 Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
    print(f"🎯 目標: {target_label.get(target, target)}")
    print(f"\n🚀 正在開啟瀏覽器...\n")

    if not os.path.exists(PROFILE_DIR):
        print("❌ 尚未登入！請先執行: python3 send_to_both.py --login")
        sys.exit(1)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            channel="chrome",
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )

        # --- 根據 target 開啟對應頁面 ---
        chatgpt_page = None
        claude_page = None
        pages_to_load = []

        if target in ("both", "chatgpt"):
            chatgpt_page = await context.new_page()
            pages_to_load.append(
                chatgpt_page.goto("https://chat.openai.com/", wait_until="domcontentloaded", timeout=60000)
            )

        if target in ("both", "claude"):
            claude_page = await context.new_page()
            pages_to_load.append(
                claude_page.goto("https://claude.ai/new", wait_until="domcontentloaded", timeout=60000)
            )

        print(f"⏳ 正在載入 {target_label.get(target, target)}...")
        await asyncio.gather(*pages_to_load)
        # 等待頁面完整渲染
        await asyncio.sleep(8)

        # --- 用 insertText 貼上 prompt（保留換行，不會觸發 Enter 送出）---
        async def paste_prompt(page, label):
            """用 insertText 把 prompt 貼進輸入框，保留所有換行格式"""
            await page.keyboard.insert_text(prompt)
            print(f"  ✏️  {label}: Prompt 已輸入")
            await asyncio.sleep(1)

        # --- 送給 ChatGPT ---
        async def send_chatgpt():
            try:
                page = chatgpt_page

                # 上傳檔案（找到隱藏的 file input）
                file_input = page.locator('input[type="file"]').first
                await file_input.set_input_files(abs_file_path)
                print("  📎 ChatGPT: 檔案已上傳")
                await asyncio.sleep(3)

                # 點擊輸入框並貼上 prompt
                textarea = page.locator("#prompt-textarea, div[contenteditable='true'][id='prompt-textarea']").first
                await textarea.click()
                await asyncio.sleep(0.5)
                await paste_prompt(page, "ChatGPT")

                # 按送出按鈕
                send_btn = page.locator('button[data-testid="send-button"], button[aria-label="Send prompt"]').first
                await send_btn.click()
                print("  ✅ ChatGPT: 已送出！")

            except Exception as e:
                print(f"  ❌ ChatGPT 錯誤: {e}")
                print("     提示: ChatGPT 可能改版了，需要更新 selector")

        # --- 送給 Claude ---
        async def send_claude():
            try:
                page = claude_page

                # 上傳檔案
                file_input = page.locator('input[type="file"]').first
                await file_input.set_input_files(abs_file_path)
                print("  📎 Claude: 檔案已上傳")
                await asyncio.sleep(3)

                # 點擊輸入框並貼上 prompt
                editor = page.locator('div.ProseMirror[contenteditable="true"], div[contenteditable="true"]').first
                await editor.click()
                await asyncio.sleep(0.5)
                await paste_prompt(page, "Claude")

                # 按送出按鈕
                send_btn = page.locator('button[aria-label="Send Message"], button[aria-label="Send message"]').first
                await send_btn.click()
                print("  ✅ Claude: 已送出！")

            except Exception as e:
                print(f"  ❌ Claude 錯誤: {e}")
                print("     提示: Claude 可能改版了，需要更新 selector")

        # 送出
        tasks = []
        if chatgpt_page:
            tasks.append(send_chatgpt())
        if claude_page:
            tasks.append(send_claude())

        print("📤 正在送出...\n")
        await asyncio.gather(*tasks)

        print("\n" + "=" * 50)
        print(f"🎉 {target_label.get(target, target)} 處理中！")
        print("請切換到瀏覽器查看回覆。")
        print("回覆完成後，回到這裡按 Enter 關閉瀏覽器。")
        print("=" * 50)
        input()
        await context.close()


def pick_file(directory: str) -> str:
    """列出資料夾中的子資料夾和 md 檔，讓使用者選擇"""
    current_dir = directory

    while True:
        if not os.path.isdir(current_dir):
            print(f"❌ 資料夾不存在: {current_dir}")
            sys.exit(1)

        # 列出子資料夾和 md 檔
        items = sorted(os.listdir(current_dir))
        subdirs = [d for d in items if os.path.isdir(os.path.join(current_dir, d)) and not d.startswith(".")]
        md_files = [f for f in items if f.endswith(".md")]

        if not subdirs and not md_files:
            print(f"❌ 資料夾中沒有子資料夾或 .md 檔案: {current_dir}")
            sys.exit(1)

        print(f"\n📂 {current_dir}\n")

        idx = 1
        entries = []  # (type, name)

        # 顯示「返回上層」（不在根目錄時）
        if os.path.abspath(current_dir) != os.path.abspath(directory):
            print(f"  {idx:2d}. 📁 .. (返回上層)")
            entries.append(("parent", ".."))
            idx += 1

        # 顯示子資料夾
        for d in subdirs:
            sub_count = len([f for f in os.listdir(os.path.join(current_dir, d)) if f.endswith(".md") or os.path.isdir(os.path.join(current_dir, d, f))])
            print(f"  {idx:2d}. 📁 {d}/  ({sub_count} 項)")
            entries.append(("dir", d))
            idx += 1

        # 顯示 md 檔
        for f in md_files:
            size_kb = os.path.getsize(os.path.join(current_dir, f)) / 1024
            print(f"  {idx:2d}. 📄 {f}  ({size_kb:.0f} KB)")
            entries.append(("file", f))
            idx += 1

        print()
        while True:
            try:
                choice = input("請輸入編號: ").strip()
                ci = int(choice) - 1
                if 0 <= ci < len(entries):
                    entry_type, entry_name = entries[ci]
                    if entry_type == "parent":
                        current_dir = os.path.dirname(current_dir)
                        break
                    elif entry_type == "dir":
                        current_dir = os.path.join(current_dir, entry_name)
                        break
                    elif entry_type == "file":
                        selected = os.path.join(current_dir, entry_name)
                        print(f"\n✅ 已選擇: {entry_name}")
                        return selected
                else:
                    print("  編號超出範圍，請重新輸入")
            except ValueError:
                print("  請輸入數字")


def pick_target() -> str:
    """讓使用者選擇送給哪個 AI"""
    print("\n🎯 送給誰？\n")
    print("  1. All（ChatGPT + Claude）")
    print("  2. ChatGPT")
    print("  3. Claude")
    print()
    while True:
        choice = input("請輸入編號: ").strip()
        if choice == "1":
            return "both"
        elif choice == "2":
            return "chatgpt"
        elif choice == "3":
            return "claude"
        else:
            print("  請輸入 1、2 或 3")


# 預設書籍資料夾
DEFAULT_BOOK_DIR = os.path.expanduser("~/Desktop/Claude Cowork/PDFconvert/output")


async def main():
    args = list(sys.argv[1:])

    if len(args) == 0:
        # 沒給任何參數 → 顯示選單
        file_path = pick_file(DEFAULT_BOOK_DIR)
        target = pick_target()
        prompt = load_prompt()
        await send_to_both(file_path, prompt, target)
        return

    if args[0] == "--login":
        await login_mode()
    elif args[0] == "--pick":
        # --pick 模式：顯示選單
        directory = args[1] if len(args) >= 2 else DEFAULT_BOOK_DIR
        file_path = pick_file(directory)
        target = pick_target()
        prompt_arg = args[2] if len(args) >= 3 else None
        prompt = load_prompt(prompt_arg)
        await send_to_both(file_path, prompt, target)
    elif len(args) == 1:
        # 只給了 md 檔，用預設 prompt.txt
        file_path = args[0]
        target = pick_target()
        prompt = load_prompt()
        await send_to_both(file_path, prompt, target)
    elif len(args) == 2:
        # 給了 md 檔 + prompt 檔
        file_path = args[0]
        target = pick_target()
        prompt = load_prompt(args[1])
        await send_to_both(file_path, prompt, target)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
