import json

def openFile_as_key(key):
    with open("config/config.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data[key]