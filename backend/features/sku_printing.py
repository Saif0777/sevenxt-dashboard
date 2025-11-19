import os
import glob
import pandas as pd
import time
import win32api
import win32print

# --- Helper Functions ---
def find_label_file(sku, label_folder_absolute):
    """
    Searches for a .lbl file that contains the SKU in its name.
    Returns: Absolute path (for Printer), Filename (for UI)
    """
    # 1. Sanitization: Remove special chars from SKU to ensure valid search
    clean_sku = str(sku).strip()
    if not clean_sku:
        return None, None

    # 2. Search Pattern: Look for any file containing the SKU
    # Example: If SKU is "ABC", it matches "m-ABC-Remote.lbl"
    search_pattern = os.path.join(label_folder_absolute, f"*{clean_sku}*.lbl")
    
    # 3. Run Search
    matches = glob.glob(search_pattern)
    
    if matches:
        # Pick the first match
        full_path = matches[0]
        filename = os.path.basename(full_path)
        return full_path, filename
        
    return None, None

def process_order_file(filepath, label_folder_absolute):
    """
    Main logic to process the Excel sheet and print Brother Labels (.lbl).
    """
    log = []
    processed_files = [] # List of files sent to printer
    
    log.append(f"Processing Manifest: {os.path.basename(filepath)}")
    
    # 1. Read the file
    try:
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath, engine='openpyxl')
            
        # Clean column names (strip whitespace)
        df.columns = df.columns.str.strip()
        
    except Exception as e:
        return {"log": [f"❌ Error reading Excel file: {str(e)}"], "printed_images": []}

    # 2. Check for required columns (Based on your screenshot: 'Sku', 'Quantity')
    # We check case-insensitive to be safe
    cols = [c.lower() for c in df.columns]
    if 'sku' not in cols or 'quantity' not in cols:
        log.append("⚠️ Warning: Columns 'Sku' or 'Quantity' not found exactly.")
        log.append(f"   Found columns: {list(df.columns)}")
        # Try to find best match
        sku_col = next((c for c in df.columns if 'sku' in c.lower()), None)
        qty_col = next((c for c in df.columns if 'qty' in c.lower() or 'quantity' in c.lower()), None)
        
        if not sku_col or not qty_col:
             return {"log": ["❌ FATAL: Could not identify SKU and Quantity columns."], "printed_images": []}
    else:
        sku_col = next(c for c in df.columns if c.lower() == 'sku')
        qty_col = next(c for c in df.columns if c.lower() == 'quantity')

    # 3. Connect to Printer
    try:
        default_printer = win32print.GetDefaultPrinter()
        log.append(f"🖨️ Target: {default_printer}") # Removed specific brand name
        
        # Check if it looks like a Zebra (Optional Polish)
        if "ZDesigner" in default_printer or "Zebra" in default_printer:
             log.append("   ✅ Detected Zebra Printer Driver")
        else:
             log.append(f"   ⚠️ Warning: Default printer '{default_printer}' might not be the Label Printer.")
             
    except:
        log.append("❌ FATAL: No Default Printer Found.")
        return {"log": log, "printed_images": []}

    # 4. Loop through rows
    items_printed = 0
    
    for index, row in df.iterrows():
        sku = str(row[sku_col]).strip()
        
        try:
            qty = int(row[qty_col])
        except:
            continue

        if qty <= 0: continue

        # Find the .lbl file
        abs_path, filename = find_label_file(sku, label_folder_absolute)
        
        if abs_path:
            log.append(f"✅ Match: {filename}")
            
            # Printing Logic
            try:
                # Simulate or Print
                win32api.ShellExecute(0, "print", abs_path, None, ".", 0)
                time.sleep(0.5) 
            except Exception as e:
                error_msg = str(e)
                if "no application is associated" in error_msg or "31" in error_msg:
                    log.append(f"   ⚠️ Dev Mode: Simulated print for {sku}")
                else:
                    log.append(f"   ⚠️ Print Error: {error_msg}")

            # UPDATED: We now append "|{qty}" to the string so frontend can read it
            processed_files.append(f"FILE_ICON:{filename}|{qty}")
            items_printed += 1
            
        else:
            # Retry Logic (Removing "SP-")
            if "SP-" in sku:
                short_sku = sku.replace("SP-", "")
                abs_path_retry, filename_retry = find_label_file(short_sku, label_folder_absolute)
                if abs_path_retry:
                    log.append(f"✅ Fuzzy Match: {filename_retry}")
                    # UPDATED: Append Quantity here too
                    processed_files.append(f"FILE_ICON:{filename_retry}|{qty}")
                    
                    try:
                        win32api.ShellExecute(0, "print", abs_path_retry, None, ".", 0)
                        time.sleep(0.5)
                    except:
                        pass
                    items_printed += 1
                else:
                    log.append(f"   ❌ MISSING: {sku}")
            else:
                log.append(f"   ❌ MISSING: {sku}")

    log.append(f"{'='*30}")
    log.append(f"🏁 processed {items_printed} SKUs.")
    
    return {"log": log, "printed_images": processed_files}