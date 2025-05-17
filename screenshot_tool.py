import time
import win32gui
import win32ui
import win32con
from ctypes import windll, byref, c_ulong, sizeof
from PIL import Image, ImageGrab


def is_real_window(hwnd):
    """Return True if hwnd is a visible, non-cloaked top-level window."""
    if not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd):
        return False
    if win32gui.GetWindow(hwnd, win32con.GW_OWNER) != 0:
        return False
    title = win32gui.GetWindowText(hwnd)
    if not title:
        return False
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    if ex_style & win32con.WS_EX_TOOLWINDOW:
        return False
    # Exclude windows that are cloaked by the system (e.g., background UWP apps)
    DWMWA_CLOAKED = 14
    cloaked = c_ulong(0)
    if windll.dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED,
                                           byref(cloaked),
                                           sizeof(cloaked)) == 0:
        if cloaked.value != 0:
            return False
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    if right - left <= 1 or bottom - top <= 1:
        return False
    return True


def list_windows():
    windows = []
    def callback(hwnd, _):
        if is_real_window(hwnd):
            windows.append((hwnd, win32gui.GetWindowText(hwnd)))
        return True
    win32gui.EnumWindows(callback, None)
    return windows


def screenshot_window(hwnd, path):
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    save_bitmap = win32ui.CreateBitmap()
    save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(save_bitmap)

    result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 1)

    bmpinfo = save_bitmap.GetInfo()
    bmpstr = save_bitmap.GetBitmapBits(True)
    image = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(save_bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)

    if result != 1:
        image = ImageGrab.grab(bbox=(left, top, right, bottom))

    image.save(path)


def main():
    windows = list_windows()
    if not windows:
        print("No windows found.")
        return

    print("Select a window to capture:")
    for i, (_, title) in enumerate(windows):
        print(f"{i}: {title}")

    try:
        index = int(input("Enter number: "))
    except ValueError:
        print("Invalid input.")
        return

    if index < 0 or index >= len(windows):
        print("Invalid selection.")
        return

    hwnd = windows[index][0]
    if not win32gui.IsWindow(hwnd):
        print("Selected window is no longer available.")
        return
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)
    screenshot_window(hwnd, "screenshot.png")
    print("Saved screenshot.png")


if __name__ == "__main__":
    main()
