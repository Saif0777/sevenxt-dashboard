import os
import glob
import pandas as pd
import time
import win32print
import subprocess
import pyautogui
import win32gui
import win32con
import re
from datetime import datetime

# --- 1. HYPER-STRICT SEARCH LOGIC ---
def find_label_file(sku, label_folder_absolute):
    """
    Finds the label ONLY if the exact Input SKU exists as a whole word.
    NO prefix stripping. NO partial matching.
    """
    target_sku = str(sku).strip()
    if not target_sku: return None, None
    
    # Escape characters (e.g., dots or brackets in SKU)
    # This ensures we search for the literal string "SP-ATP6w"
    safe_sku = re.escape(target_sku)

    try:
        all_files = [f for f in os.listdir(label_folder_absolute) if f.lower().endswith(".lbl")]
    except FileNotFoundError:
        return None, None

    # REGEX EXPLANATION:
    # (?<![a-zA-Z0-9]) -> Lookbehind: Previous char MUST NOT be a letter or number.
    # safe_sku         -> The EXACT string from Excel (e.g., "SP-ATP6w").
    # (?![a-zA-Z0-9])  -> Lookahead: Next char MUST NOT be a letter or number.
    #
    # This treats "SP-ATP6w" as a single, unbreakable block.
    pattern = re.compile(r'(?<![a-zA-Z0-9])' + safe_sku + r'(?![a-zA-Z0-9])', re.IGNORECASE)

    for filename in all_files:
        if pattern.search(filename):
            return os.path.join(label_folder_absolute, filename), filename

    return None, None

def force_window_focus(window_name):
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if window_name.lower() in title.lower():
                try:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                except: pass
    win32gui.EnumWindows(callback, None)

def process_order_file(filepath, label_folder_absolute):
    log = []
    processed_files = []
    report_data = []
    
    log.append(f"Processing: {os.path.basename(filepath)}")
    
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

    # --- PATH TO ZEBRA ---
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
                "Status": "PRINTED",
                "Time": datetime.now().strftime("%H:%M:%S")
            })

            try:
                # Printing Workflow
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

            except Exception as e:
                log.append(f"   ⚠️ Error: {str(e)}")
                report_data[-1]["Status"] = "ERROR"
        else:
            # STRICT FAIL - If exact SKU string isn't found, fail.
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
    
    # Report Generation
    try:
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_name = f"Print_Report_{timestamp}.xlsx"
        full_save_path = os.path.join(downloads_path, report_name)
        df_report = pd.DataFrame(report_data)
        df_report.to_excel(full_save_path, index=False)
        log.append(f"📄 Report saved to Downloads")
        os.startfile(full_save_path)
    except Exception as e:
        log.append(f"⚠️ Report Error: {str(e)}")
    
    return {"log": log, "printed_images": processed_files}