import json
import os
import sys

def get_base_path():
    """หา path """
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))

def openFile_as_key(key):
    base_dir = get_base_path()
    json_path = os.path.join(base_dir, "config", "config.json")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data[key]
    except FileNotFoundError:
        print(f"Error: หาไฟล์ config ไม่เจอที่ {json_path}")
        return []
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return []