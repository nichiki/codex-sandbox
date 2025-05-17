# Codex用サンドボックスリポジトリ

## Screenshot Tool for Windows

This repository includes a small CLI utility `screenshot_tool.py` that captures a screenshot of a selected window on Windows.

The tool uses the Windows `PrintWindow` API when possible and automatically falls back to a regular screen capture if the result appears blank. This helps when capturing hardware-accelerated applications such as modern browsers.

### Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the tool:
   ```bash
   python screenshot_tool.py
   ```
3. Choose a window from the list and the screenshot will be saved as `screenshot.png` in the current directory.
