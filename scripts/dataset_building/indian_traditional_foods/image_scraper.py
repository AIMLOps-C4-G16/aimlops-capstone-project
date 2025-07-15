import argparse
import os
import uuid
import random
from datetime import datetime
from icrawler.builtin import GoogleImageCrawler, BingImageCrawler
from icrawler.downloader import ImageDownloader

# -------------------------------
# CLI Argument Parser
# -------------------------------
parser = argparse.ArgumentParser(description="Indian food image crawler using Google or Bing")
parser.add_argument(
    "--engine",
    choices=["google", "bing"],
    default="google",
    help="Search engine to use for image crawling (google or bing). Default is google."
)
args = parser.parse_args()
CRAWLER_ENGINE = args.engine

# -------------------------------
# Foods by Indian state
# -------------------------------
indian_foods_by_state = {
    "Punjab": ["Sarson da Saag", "Makki di Roti", "Butter Chicken", "Amritsari Kulcha", "Chole Bhature"],
    "Delhi": ["Chole Bhature", "Aloo Tikki Chaat", "Nihari", "Paratha", "Butter Chicken Delhi Style"],
    "Jammu & Kashmir": ["Rogan Josh", "Yakhni", "Dum Aloo", "Modur Pulav", "Gushtaba"],
    "Ladakh": ["Thukpa", "Skyu", "Momos", "Butter Tea", "Chutagi"],
    "Rajasthan": ["Dal Baati Churma", "Laal Maas", "Gatte ki Sabzi", "Ker Sangri", "Mawa Kachori"],
    "West Bengal": ["Shorshe Ilish", "Chingri Malai Curry", "Luchi Aloo Dum", "Mishti Doi", "Begun Bhaja"],
    "Assam": ["Khaar", "Masor Tenga", "Duck Curry", "Aloo Pitika", "Pitha"],
    "Goa": ["Fish Curry Rice", "Prawn Balchao", "Bebinca", "Vindaloo", "Sorpotel"],
    "Karnataka": ["Bisi Bele Bath", "Mysore Pak", "Neer Dosa", "Ragi Mudde", "Udupi Sambar"],
    "Kerala": ["Kerala Sadya", "Appam with Stew", "Puttu", "Malabar Parotta", "Fish Molee"]
}

# -------------------------------
# Output directories
# -------------------------------
base_dir = "indian_traditional_foods"
image_dir = os.path.join(base_dir, "images")
caption_file = os.path.join(base_dir, "indian_traditional_foods.token.txt")
images_per_dish = 10

os.makedirs(image_dir, exist_ok=True)
if not os.path.exists(caption_file):
    with open(caption_file, "w", encoding="utf-8") as f:
        f.write("")

# -------------------------------
# Caption Templates
# -------------------------------
caption_templates = [
    "A dish called {dish} from {state}.",
    "{dish} is a popular traditional food in {state}, India.",
    "People in {state} often enjoy {dish} during festivals or meals."
]

# -------------------------------
# Query Templates
# -------------------------------
query_templates = [
    "{dish} traditional Indian food from {state}",
    "{dish} dish served in {state}, India",
    "{dish} close-up food image from {state}"
]

# -------------------------------
# Custom Downloader (Rename file to 16-char random alphanumeric names + Filter only .jpg file)
# -------------------------------
class CustomDownloader(ImageDownloader):
    def get_filename(self, task, default_ext):
        return f"{uuid.uuid4().hex[:16]}.{default_ext}"

    def download(self, task, default_ext, timeout=5, max_retry=1, **kwargs):
        allowed_exts = ["jpg", "jpeg"]
        if default_ext.lower() not in allowed_exts:
            print(f"Skipping file: .{default_ext}")
            return False

        return super().download(task, default_ext, timeout, max_retry, **kwargs)

# -------------------------------
# Main crawling loop
# -------------------------------
for state, dishes in indian_foods_by_state.items():
    for dish in dishes:
        search_query = random.choice(query_templates).format(dish=dish, state=state)
        print(f"\n Downloading images for: {search_query} using {CRAWLER_ENGINE.title()}")

        # Track existing images
        before_files = set(os.listdir(image_dir))

        # Setup crawler
        if CRAWLER_ENGINE == "bing":
            crawler = BingImageCrawler(
                downloader_cls=CustomDownloader,
                storage={"root_dir": image_dir},
                log_level="ERROR"
            )
        else:
            crawler = GoogleImageCrawler(
                downloader_cls=CustomDownloader,
                storage={"root_dir": image_dir},
                log_level="ERROR"
            )

        try:
            crawler.crawl(
                keyword=search_query,
                max_num=images_per_dish,
                filters={"type": "photo", "size": "large"},
                file_idx_offset='auto'
            )
        except Exception as e:
            print(f"Error while downloading for {dish}: {e}")
            continue

        # Find new images
        after_files = set(os.listdir(image_dir))
        new_files = sorted(after_files - before_files)
        new_images = [f for f in new_files if f.lower().endswith((".jpg", ".jpeg"))]

        # Write captions
        with open(caption_file, "a", encoding="utf-8") as f:
            for filename in new_images:
                print(f"Writing captions for {filename}")
                for i, template in enumerate(caption_templates):
                    caption = template.format(dish=dish, state=state)
                    f.write(f"{filename}#{i}\t{caption}\n")

print(f"\n Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
