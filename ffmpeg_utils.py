import subprocess
import os
import random
import string
import argparse
import logging
from datetime import datetime, timedelta

from hash_demo import get_video_hash

# ============================================================
# LOGGING SETUP
# ============================================================

def setup_logging(output_folder):
    """Setup logging to file and console"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{output_folder}/batch_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return log_file

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def random_string(length=8):
    """Generate random alphanumeric string"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


def random_date():
    """Generate random date within past 30 days"""
    days_ago = random.randint(1, 30)
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    date = datetime.now() - timedelta(days=days_ago, hours=hours, minutes=minutes)
    return date.strftime("%Y-%m-%dT%H:%M:%S.000000Z")

def random_transform():
    """Generate random subtle rotation/flip settings"""
    brightness = round(random.uniform(-0.05, 0.05), 3)
    contrast = round(random.uniform(0.95, 1.05), 3)
    saturation = round(random.uniform(0.95, 1.05), 3)

    # Add subtle gamma variation
    gamma = round(random.uniform(0.95, 1.05), 3)

    return {
        "brightness": brightness,
        "contrast": contrast,
        "saturation": saturation,
        "gamma": gamma,
        "filter_string": f"eq=brightness={brightness}:contrast={contrast}:saturation={saturation}:gamma={gamma}"
    }
# ============================================================
# VIDEO INFO FUNCTIONS
# ============================================================

def get_video_info(filepath):
    """Get video metadata using ffprobe"""
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        filepath
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    return result.stdout


def get_video_files(folder_path):
    """Get all mp4 files from a folder"""
    video_files = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp4"):
            full_path = os.path.join(folder_path, filename)
            video_files.append(full_path)
    return video_files


# ============================================================
# VIDEO PROCESSING FUNCTIONS
# ============================================================

def copy_video(input_path, output_path):
    """Copy video with new container"""
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-c", "copy",
        "-y",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Created: {output_path}")
    return True


def modify_metadata(input_path, output_path, title, comment):
    """Copy video with custom metadata"""
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-metadata", f"title={title}",
        "-metadata", f"comment={comment}",
        "-c", "copy",
        "-y",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Created: {output_path}")
    return True


def create_variation(input_path, output_path, reencode=False, use_filter=False, use_audio=False):
    """Create video with randomized metadata and encoding
    
    Args:
        input_path: Source video file
        output_path: Output video file
        reencode: If True, fully re-encode (slower but deeper uniqueness)
        use_filter: if True apply random visual filter (requires reencode=True)
    Returns:
        dict with path, hash, title or None if failed
    """
    # Generate random metadata
    title = f"vid_{random_string()}"
    comment = random_string(16)
    date = random_date()
    author = f"user_{random_string(6)}"
    description = f"Video created on {date[:10]}"
    copyright_text = f"Copyright {random.randint(2020, 2026)}"
    artist = f"creator_{random_string(6)}"
    
    # Build ffmpeg command
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-metadata", f"title={title}",
        "-metadata", f"comment={comment}",
        "-metadata", f"creation_time={date}",
        "-metadata", f"author={author}",
        "-metadata", f"description={description}",
        "-metadata", f"copyright={copyright_text}",
        "-metadata", f"artist={artist}",
    ]
    
    # Add encoding and filtering settings
    filter_info = None
    if reencode:
        crf = random.randint(20, 28)
        preset_options = ["fast", "medium", "slow"]
        preset = random.choice(preset_options)

        # Add visual filter if requested
        if use_filter:
            filter_info = random_filter()
            cmd.extend(["-vf", filter_info["filter_string"]])
        
        # Add audio filter if requested
        if use_audio:
            audio_info = random_audio()
            cmd.extend(["-af", audio_info["filter_string"]])
        
        cmd.extend([
            "-c:v", "libx264",
            "-crf", str(crf),
            "-preset", preset,
            "-c:a", "aac",
            "-b:a", f"{random.choice([128, 160, 192])}k"
        ])
    else:
        cmd.extend(["-c", "copy"])
    
    cmd.extend(["-y", output_path])
    
    # Run ffmpeg
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Check result
    if os.path.exists(output_path):
        video_hash = get_video_hash(output_path)
        mode = "re-encoded" if reencode else "copied"
        print(f"Created ({mode}): {output_path}")
        print(f"  Title:  {title}")
        print(f"  Author: {author}")
        if reencode:
            print(f"  CRF:    {crf}, Preset: {preset}")
        if filter_info:
            print(f" Filter: B={filter_info['brightness']}, C={filter_info['contrast']}, S={filter_info['saturation']}, G={filter_info['gamma']}")
        if use_audio:
            print(f" Audio: Vol={audio_info['volume']}, Tempo={audio_info['tempo']}")
        print(f"  Hash:   {video_hash[:16]}...")
        return {"path": output_path, "hash": video_hash, "title": title}
    else:
        print(f"Error creating {output_path}")
        return None


# ============================================================
# BATCH PROCESSING FUNCTIONS
# ============================================================

def is_duplicate_hash(new_hash, hash_list):
    """Check if hash already exists"""
    return new_hash in hash_list


def batch_create_variations(input_folder, output_folder, variations_per_video=3, reencode=False, use_filter=False, use_audio=False):
    """Create multiple variations from all videos in a folder"""

    # Setup
    os.makedirs(output_folder, exist_ok=True)
    log_file = setup_logging(output_folder)
    source_videos = get_video_files(input_folder)
    
    total_videos = len(source_videos) * variations_per_video
    mode = "re-encode" if reencode else "copy"
    filter_status = "ON" if use_filter else "OFF"
    audio_status = "ON" if use_audio else "OFF"

    # Print header
    logging.info("=" * 50)
    logging.info("BATCH VIDEO VARIATION")
    logging.info("=" * 50)
    logging.info(f"Source videos: {len(source_videos)}")
    logging.info(f"Variations each: {variations_per_video}")
    logging.info(f"Total to create: {total_videos}")
    logging.info(f"Mode: {mode}")
    logging.info(f"Visual filter: {filter_status}")
    logging.info(f"Audio filter: {audio_status}")
    logging.info(f"Log file: {log_file}")
    logging.info("=" * 50)
    
    # Process videos
    all_hashes = []
    results = []
    duplicates = 0
    current = 0
    
    for video_path in source_videos:
        filename = os.path.basename(video_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        for i in range(variations_per_video):
            current += 1
            progress = (current / total_videos) * 100
            
            logging.info(f"[{current}/{total_videos}] ({progress:.1f}%)")
            
            output_path = f"{output_folder}/{name_without_ext}_var_{i+1:03d}.mp4"
            result = create_variation(video_path, output_path, reencode=reencode, use_filter=use_filter, use_audio=use_audio)
            
            if result:
                if is_duplicate_hash(result["hash"], all_hashes):
                    logging.warning("  ⚠ DUPLICATE DETECTED!")
                    duplicates += 1
                else:
                    all_hashes.append(result["hash"])
                    results.append(result)
    
    # Save hashes to database
    from data import load_hashes, save_hashes
    hashes_dict = load_hashes()
    for r in results:
        video_id = os.path.basename(r["path"])
        hashes_dict[video_id] = r["hash"]
    save_hashes(hashes_dict)
    
    # Print summary
    logging.info("")
    logging.info("=" * 50)
    logging.info("SUMMARY")
    logging.info("=" * 50)
    logging.info(f"Total created: {len(results)}")
    logging.info(f"Duplicates: {duplicates}")
    logging.info(f"Unique videos: {len(all_hashes)}")
    logging.info(f"Saved to hashes.json")
    logging.info(f"Log file: {log_file}")
    logging.info("=" * 50)
    
    return results

def random_filter():
    """Generate random subtle visual filter settings"""
    brightness = round(random.uniform(-0.05, 0.05), 3)
    contrast = round(random.uniform(0.95, 1.05), 3)
    saturation = round(random.uniform(0.95, 1.05), 3)
    gamma = round(random.uniform(0.95, 1.05), 3)

    return {
        "brightness": brightness,
        "contrast": contrast,
        "saturation": saturation,
        "gamma": gamma,
        "filter_string": f"eq=brightness={brightness}:contrast={contrast}:saturation={saturation}"
    }

def random_audio():
    """Generate random subtle audio settings"""
    # Volume: 0.9 to 1.1 (±10%)
    volume = round(random.uniform(0.9, 1.1), 2)
    
    # Tempo: 0.98 to 1.02 (±2% speed, subtle)
    tempo = round(random.uniform(0.98, 1.02), 2)
    
    return {
        "volume": volume,
        "tempo": tempo,
        "filter_string": f"volume={volume},atempo={tempo}"
    }
# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video Variation System")
    
    parser.add_argument("input", help="Input folder with source videos")
    parser.add_argument("output", help="Output folder for variations")
    parser.add_argument("-n", "--number", type=int, default=3, help="Variations per video (default: 3)")
    parser.add_argument("-r", "--reencode", action="store_true", help="Re-encode videos (slower but deeper uniqueness)")
    parser.add_argument("-f", "--filter", action="store_true", help="Apply visual filters (requires --reencode)")
    parser.add_argument("-a", "--audio", action="store_true", help="Apply audio variations (requires --reencode)")

    args = parser.parse_args()

    # If filter is requested, reencode must be on
    if args.filter and not args.reencode:
        print("Warning: --filter requires --reencode. Enabling re-encode.")
        args.reencode = True

    results = batch_create_variations(
        input_folder=args.input,
        output_folder=args.output,
        variations_per_video=args.number,
        reencode=args.reencode,
        use_filter=args.filter,
        use_audio=args.audio
    )

    
