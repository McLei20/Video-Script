import subprocess

def get_video_info(filepath):
    """Get video metadata using ffprobe"""
    cmd = [
        "ffprobe",
        "-v", "quiet",                    # Hide extra output
        "-print_format", "json",          # Output as JSON
        "-show_format",                   # Show file format info
        "-show_streams",                  # Show video/audio stream info
        filepath
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    
    return result.stdout


# Test it
info = get_video_info("video/test1.mp4")
print(info)