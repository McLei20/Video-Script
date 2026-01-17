import hashlib
import json
import data

def get_video_hash(filepath):
    with open(filepath, "rb") as file:
        content = file.read()
        result = hashlib.sha256(content)
    return result.hexdigest()

def register_video(video_id, filepath):
    # Get the hash
    hash_value = get_video_hash(filepath)

    # Load existing data (or empty dict)
    hashes_dict = data.load_hashes()

    # Add new entry
    hashes_dict[video_id] = hash_value

    # Save back to file
    data.save_hashes(hashes_dict)

    print(f"Registered {video_id} with hash {hash_value}")

def check_integrity(video_id, filepath):
    # Load stored data
    hashes_dict = data.load_hashes()
    
    # Get the stored hash for this video
    stored_hash = hashes_dict[video_id]

    # Calculate Current hash
    current_hash = get_video_hash(filepath)

    # Compare and Return result
    return stored_hash == current_hash

def list_registered_videos():
    hashes_dict = data.load_hashes()
    results = []
    for key, value in hashes_dict.items():
        results.append({"id": key, "hash": value})
    return results

#register_video("video_001", "test.mp4")
result = check_integrity("video_001", "video/test1.mp4")
print(f"Integrity check: {result}")
print(list_registered_videos())

original = get_video_hash("video/test1.mp4")
copy = get_video_hash("video/copy_test.mp4")

print(f"Original: {original}")
print(f"Copy: {copy}")
print(f"Same?: {original == copy}")