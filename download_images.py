import os
import shutil
from bing_image_downloader import downloader

os.makedirs("static/images", exist_ok=True)

queries = [
    (1, "Medical Bandage white background hd"),
    (2, "Surgical Cotton Roll medical high resolution"),
    (3, "Medical Roller Bandage white background isolated"),
    (4, "Medical Gauze Roll isolated"),
    (5, "Sterile medical cotton swabs isolated"),
    (6, "Surgical mask 3 ply isolated hd")
]

for product_id, query in queries:
    try:
        downloader.download(query, limit=1, output_dir='dataset', adult_filter_off=True, force_replace=False, timeout=10)
        
        folder_path = os.path.join("dataset", query)
        if os.path.exists(folder_path):
            files = os.listdir(folder_path)
            if files:
                img_file = files[0]
                ext = os.path.splitext(img_file)[1]
                src = os.path.join(folder_path, img_file)
                dst = f"static/images/product_{product_id}.jpg"
                shutil.copy(src, dst)
                print(f"Success: {dst} from {query}")
    except Exception as e:
        print(f"Error downloading product {product_id}: {e}")
