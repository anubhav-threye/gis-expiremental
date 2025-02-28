import os
import subprocess

# Configuration
BLENDER_PATH = os.path.abspath("C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe")
BAKE_SCRIPT = os.path.abspath("./bake_process.py")
BLEND_FILE_DIR = os.path.abspath("D:\\Q4")
OUT_PATH = os.path.abspath("C:\\Threye\\Bake\\result")
BLENDER_ARGS = []

def find_blend_files(root_dir):
    """Recursively find all .blend files in directory"""
    blend_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.blend'):
                blend_files.append(os.path.join(dirpath, filename))
                
    return blend_files

# Function to sort blend files alphabetically by their filename
def sort_blend_files(blend_files):
    return sorted(blend_files, key=lambda x: os.path.basename(x).lower())


def run_blender_process(blend_file):
    """Run Blender with specified file and log output"""
    # Generate prefix from filename
    base_name = os.path.splitext(os.path.basename(blend_file))[0]
    
    # Build command arguments
    command = [
        BLENDER_PATH,
        *BLENDER_ARGS,
        blend_file,
        '--python', BAKE_SCRIPT,
        '--',  # Separate Blender args from script args
        base_name,
        '16384',
        OUT_PATH
    ]
    
    # Run process and capture output in real-time
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1  # Line buffered
    )
    
    # Stream output to console
    try:
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            
            log = line.strip()
            print(log)
            
            # if ("Uninitialized image" in log):
            #     process.terminate()

    except KeyboardInterrupt:
        process.terminate()
        raise
    
    return process.poll()

def main():
    blend_files = find_blend_files(BLEND_FILE_DIR)
    
    print(blend_files)
    for idx, blend_file in enumerate(blend_files, 1):
        # if ("Q3_C" in blend_file):
        #     continue
        # else:
        print(f"\nProcessing file {idx}/{len(blend_files)}: {blend_file}")
        return_code = run_blender_process(blend_file)
    
        if return_code != 0:
            print(f"Error processing {blend_file} (exit code: {return_code})")
        else:
            print(f"Successfully processed {blend_file}")

if __name__ == "__main__":
    main()