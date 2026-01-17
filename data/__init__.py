import json, os

hashes_path = os.path.join(os.path.dirname(__file__), "hashes.json")

def load_hashes():
    try:
        with open(hashes_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    
def save_hashes(hashes_dict):
    with open(hashes_path, "w") as f:
        json.dump(hashes_dict, f)
