import os
import glob
import pandas as pd
import time
import subprocess
import re
from datetime import datetime

# --- 1. SAFE IMPORTS FOR HYBRID CLOUD/LOCAL SUPPORT ---
# This prevents the server from crashing on Linux (Render) where these libraries don't exist.
try:
    import win32print
    import win32gui
    import win32con
    import pyautogui
    PRINTING_AVAILABLE = True
except ImportError:
    # If we are on Linux/Render, these will fail. We catch the error here.
    win32print = None
    win32gui = None
    win32con = None
    pyautogui = None
    PRINTING_AVAILABLE = False
    print("⚠️ Host is Linux/Cloud: Physical printing disabled.")

# --- 2. HYPER-STRICT SEARCH LOGIC ---
def find_label_file(sku, label_folder_absolute):
    """
    Finds the label ONLY if the exact Input SKU exists as a whole word.
    NO prefix stripping. NO partial matching.
    """
    target_sku = str(sku).strip()
    if not target_sku: return None, None
    
    # Escape characters (e.g., dots or brackets in SKU)
    safe_sku = re.escape(target_sku)

    try:
        all_files = [f for f in os.listdir(label_folder_absolute) if f.lower().endswith(".lbl")]
    except FileNotFoundError:
        return None, None

    # REGEX: Lookbehind/Lookahead ensures "SP-ATP6w" is a distinct word
    pattern = re.compile(r'(?<![a-zA-Z0-9])' + safe_sku + r'(?![a-zA-Z0-9])', re.IGNORECASE)

    for filename in all_files:
        if pattern.search(filename):
            return os.path.join(label_folder_absolute, filename), filename

    return None, None

def force_window_focus(window_name):
    if not PRINTING_AVAILABLE: return # Skip on cloud
    
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if window_name.lower() in title.lower():
                try:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                except: pass
    try:
        win32gui.EnumWindows(callback, None)
    except Exception:
        pass

def process_order_file(filepath, label_folder_absolute):
    log = []
    processed_files = []
    report_data = []
    
    log.append(f"Processing: {os.path.basename(filepath)}")
    
    # --- CLOUD CHECK ---
    if not PRINTING_AVAILABLE:
        log.append("⚠️ SERVER NOTICE: Physical printing is disabled on Cloud Hosting.")
        log.append("ℹ️ This feature only works on the Local Windows App.")
        # We continue just to parse the file and show what WOULD have happened
    
    # Read Data
    try:
        if filepath.endswith('.csv'): df = pd.read_csv(filepath)
        else: df = pd.read_excel(filepath, engine='openpyxl')
        df.columns = df.columns.str.strip()
        
        # Check Headers
        col_names = [str(c).lower() for c in df.columns]
        if not any('sku' in c for c in col_names):
            log.append("⚠️ No headers found. Assuming Col A=SKU, Col B=Qty")
            if filepath.endswith('.csv'): df = pd.read_csv(filepath, header=None)
            else: df = pd.read_excel(filepath, engine='openpyxl', header=None)
            df.rename(columns={0: 'TargetSKU', 1: 'TargetQty'}, inplace=True)
            
    except Exception as e:
        return {"log": [f"❌ Error: {str(e)}"], "printed_images": []}

    # Identify Columns
    cols = [c.lower() for c in df.columns]
    sku_col = next((c for c in df.columns if 'sku' in c.lower()), None)
    qty_col = next((c for c in df.columns if 'qty' in c.lower() or 'quantity' in c.lower()), None)
    
    if not sku_col or not qty_col:
         return {"log": ["❌ FATAL: Columns Missing."], "printed_images": []}

    # --- PATH TO ZEBRA (Only used if printing is available) ---
    zebra_exe = r"C:\Program Files (x86)\Zebra Technologies\ZebraDesigner 2\bin\Design.exe"

    items_processed = 0
    
    for index, row in df.iterrows():
        sku = str(row[sku_col]).strip()
        try: qty = int(row[qty_col])
        except: qty = 0
            
        if qty <= 0: continue

        # --- STRICT SEARCH CALL ---
        abs_path, filename = find_label_file(sku, label_folder_absolute)
        
        if abs_path:
            log.append(f"✅ Match: {sku} -> {filename}")
            processed_files.append(f"FILE_ICON:{filename}|{qty}")
            items_processed += 1
            
            report_data.append({
                "SKU Input": sku,
                "Label File": filename,
                "Quantity": qty,
                "Status": "QUEUED" if PRINTING_AVAILABLE else "CLOUD_PREVIEW",
                "Time": datetime.now().strftime("%H:%M:%S")
            })

            # --- PHYSICAL PRINTING (WINDOWS ONLY) ---
            if PRINTING_AVAILABLE:
                try:
                    subprocess.Popen([zebra_exe, abs_path])
                    time.sleep(12) 
                    force_window_focus("ZebraDesigner")
                    time.sleep(1)
                    pyautogui.hotkey('ctrl', 'p')
                    time.sleep(2)
                    pyautogui.typewrite(str(qty))
                    time.sleep(0.5)
                    pyautogui.press('enter')
                    time.sleep(0.5)
                    pyautogui.hotkey('alt', 'p') 
                    time.sleep(8)
                    os.system("taskkill /f /im Design.exe")
                    time.sleep(2)
                    report_data[-1]["Status"] = "PRINTED"
                except Exception as e:
                    log.append(f"   ⚠️ Print Error: {str(e)}")
                    report_data[-1]["Status"] = "ERROR"
            else:
                # On Cloud, we just log that we would have printed it
                log.append(f"   ℹ️ [Cloud] Skipped physical print for {qty} copies.")

        else:
            # STRICT FAIL
            log.append(f"   ❌ SKU NOT FOUND: {sku}")
            report_data.append({
                "SKU Input": sku,
                "Label File": "NOT FOUND",
                "Quantity": qty,
                "Status": "MISSING",
                "Time": datetime.now().strftime("%H:%M:%S")
            })

    log.append(f"{'='*30}")
    log.append(f"🏁 Processed {items_processed} rows.")
    
    # Report Generation (Save to Downloads on Local, or Uploads on Cloud)
    try:
        if PRINTING_AVAILABLE:
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            # Opens file locally
            open_file = True
        else:
            # On cloud, save to the app's upload folder (or tmp)
            downloads_path = "uploads" 
            if not os.path.exists(downloads_path): os.makedirs(downloads_path)
            open_file = False

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_name = f"Print_Report_{timestamp}.xlsx"
        full_save_path = os.path.join(downloads_path, report_name)
        
        df_report = pd.DataFrame(report_data)
        df_report.to_excel(full_save_path, index=False)
        
        log.append(f"📄 Report saved: {report_name}")
        
        if open_file:
            os.startfile(full_save_path)
            
    except Exception as e:
        log.append(f"⚠️ Report Error: {str(e)}")
    
    return {"log": log, "printed_images": processed_files}