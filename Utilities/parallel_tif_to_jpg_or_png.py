import os
import sys
import tifffile
from PIL import Image
from concurrent.futures import ProcessPoolExecutor
import time

"""
This file is used to convert .tif files to .jpg or .png files in parallel
for the Vesuvius Data Download project. It is designed to be run from the
command line with the following arguments:

1. The root directory to search for .tif files and subfolders
2. The target data types to convert (volumes, masked_volumes, layers, or all)
3. The output format (jpg or png)
4. Whether to overwrite existing files (True or False)
5. The quality of the output jpg files (0-100)
6. Optional: Modulo value to filter files based on the filename eg. 5
to only process files where the filename is divisible by 5

Example usage:
python parallel_tif_to_jpg_or_png.py /path/to/directory layers jpg False 85

This will convert all .tif files in the 'layers' subfolders of the 
path/to/directory to .jpg files with a quality of 85, without overwriting

Using this script without any arguments will default to the following:
- Root directory: ./ (current directory)
- Target data types: layers Ex: volumes, masked_volumes, layers or all
- Output format: jpg
- Overwrite: False
- Quality: 95
- Modulo value: None

Thus you could pass only the root directory as an argument, if you like those defaults:
python parallel_tif_to_jpg_or_png.py /path/to/directory
or alternatively edit the default values in the script itself.
This includes editting the output path to save the converted files to a different location
than beside the original .tif files.

Note: This script requires the tifffile and Pillow libraries to be installed.
This can be done with pip: 
pip install tifffile Pillow
"""

def convert_single_tif(file_path, dest_folder, output_format='jpg', quality=95, overwrite=True):
    try:
        filename = os.path.basename(file_path)
        dest_file_path = os.path.join(dest_folder, f"{os.path.splitext(filename)[0]}.{output_format}")
        
        # Check if the file exists and if overwrite is False, skip this file
        if not overwrite and os.path.exists(dest_file_path):
            return
        
        img_array = tifffile.imread(file_path)
        if img_array.dtype != 'uint8':
            img_array = (img_array / 256).astype('uint8')
        img = Image.fromarray(img_array)
        
        if output_format == 'jpg':
            img.save(dest_file_path, "JPEG", quality=quality)
        elif output_format == 'png':
            img.save(dest_file_path, "PNG")
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def convert_tif(source_folder, output_format='jpg', quality=85, overwrite=True, mod_value=None, output_path=None):
    dest_folder_suffix = '_jpg' if output_format == 'jpg' else '_png'

    if output_path is not None:
        dest_folder = f"{output_path}{dest_folder_suffix}"
    else:
        dest_folder = f"{source_folder}{dest_folder_suffix}"
    
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    # Exclude files that start with ._ in addition to filtering for .tif and .tiff extensions
    tif_files = sorted([os.path.join(source_folder, f) for f in os.listdir(source_folder)
                        if (f.lower().endswith(('.tif', '.tiff')) and not f.startswith('._'))])
    
    # Filter files based on the modulo condition if mod_value is specified
    if mod_value is not None:
        try:
            mod_value = int(mod_value)
            tif_files = [f for f in tif_files if int(os.path.splitext(os.path.basename(f))[0]) % mod_value == 0]
        except ValueError:
            print("Modulo value must be an integer. Skipping modulo filtering.")
    
    tif_files = sorted(tif_files)

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(convert_single_tif, file_path, dest_folder, output_format, quality, overwrite) for file_path in tif_files]
        for future in futures:
            future.result()

def process_specific_folders(root_directory, target_types, output_format='jpg', quality=95, overwrite=True, mod_value=None, output_path=None):
    for root, dirs, files in os.walk(root_directory):
        # If the current directory ends with '.zarr', skip its subdirectories
        if root.endswith('.zarr'):
            dirs[:] = []  # This modifies the list in-place and os.walk() will skip the subdirectories
            continue
        
        if os.path.basename(root) in target_types:
            start_time = time.time()
            
            # Process direct subdirectories of a matching folder
            if os.path.basename(root) != 'layers':
                for sub_dir in dirs:
                    if not sub_dir.endswith(('_jpg', '_png')):
                        specific_folder_path = os.path.join(root, sub_dir)
                        print(f"Processing .tif files in {specific_folder_path} to {output_format.upper()} with quality {quality}")
                        convert_tif(specific_folder_path, output_format=output_format, quality=quality, overwrite=overwrite, mod_value=mod_value, output_path=output_path)
            else:
                convert_tif(root, output_format=output_format, quality=quality, overwrite=overwrite, mod_value=mod_value, output_path=output_path)
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Time to complete folder: {execution_time} seconds")
            
if __name__ == '__main__':
    root_directory_path = './'
    target_types = ['layers']  # Default types to check ['volumes', 'masked_volumes', 'layers']
    output_format = 'jpg'  # Default output format
    quality = 95  # Default quality
    overwrite = False  # Default overwrite
    mod_value = None # Default mod value
    output_path = None  # Default output path

    if len(sys.argv) > 1:
        root_directory_path = sys.argv[1]
    if len(sys.argv) > 2:
        target_types = [sys.argv[2]]  # Accepts one target type or 'all'
        if target_types[0] == 'all':
            target_types = ['volumes', 'masked_volumes', 'layers']
    if len(sys.argv) > 3:
        output_format = sys.argv[3]  # 'jpg' or 'png'
    if len(sys.argv) > 4:
        overwrite = sys.argv[4].lower() == 'true' # 'True' or 'False' -> default to False
    if len(sys.argv) > 5:
        quality = int(sys.argv[5])
    if len(sys.argv) > 6:
        mod_value = sys.argv[6]  # New argument for mod value


    print(f"Converting .tif files in {root_directory_path} to {output_format.upper()} with quality {quality}")
    print(f"Target data types: {target_types}")

    start_time = time.time()
    process_specific_folders(root_directory_path, target_types, output_format=output_format, quality=quality, overwrite=overwrite, mod_value=mod_value, output_path=output_path)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Total time to complete: {execution_time} seconds")