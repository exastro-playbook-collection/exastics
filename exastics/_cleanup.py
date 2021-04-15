import os.path
import shutil

def publish_api(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    print("succeeded")
