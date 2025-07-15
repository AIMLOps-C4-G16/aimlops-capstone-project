import os
from icrawler.builtin import GoogleImageCrawler
from icrawler.downloader import ImageDownloader
import string
import time
import random
import requests

CONFIG_FILE = 'unique_indian_costumes.txt'  # List of costumes
BASE_DIR = 'images/indian_costumes'  # All images will be saved here
IMAGES_PER = 3  # Desired number of images per costume

os.makedirs(BASE_DIR, exist_ok=True)

# Track downloaded filenames for captioning
downloaded_filenames = []

# Custom Image Downloader with random filenames and better error handling
class CustomNameDownloader(ImageDownloader):
    
    def __init__(self, *args, **kwargs):
        self.root_dir = kwargs.get('root_dir', BASE_DIR)
        super().__init__(*args, **kwargs)

    def get_filename(self, task, default_ext):
        random_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        full_name = f'{random_name}.{default_ext}'
        return full_name

    def download(self, task, default_ext, timeout=5, max_retry=3, **kwargs):
        try:
            file_url = task['file_url']
            ext = default_ext
            filename = self.get_filename(task, ext)
            file_path = os.path.join(self.storage.root_dir, filename)

            for attempt in range(max_retry):
                try:
                    resp = requests.get(file_url, timeout=timeout)
                    content_type = resp.headers.get('Content-Type', '')
                    if resp.status_code == 200 and not content_type.startswith('image/'):
                        self.logger.warning(f'Skipped non-image content: {task["file_url"]}')
                        return
                    if resp.status_code == 200:
                        with open(file_path, 'wb') as f:
                            f.write(resp.content)

                        if os.path.exists(file_path):
                            self.on_image_downloaded(task, file_path)
                            return True
                    else:
                        print(f"❌ Status code {resp.status_code} on attempt {attempt+1}")
                except Exception as e:
                    print(f"❌ Attempt {attempt+1} failed: {e}")

            self.on_error(task, f'Failed after {max_retry} retries')
            return False

        except Exception as e:
            self.on_error(task, e)
            return False

    def on_image_downloaded(self, task, filename):
        if os.path.exists(filename):
            print(f"✅ Image successfully downloaded: {filename}")
            downloaded_filenames.append(filename)
        else:
            print(f"❌ Image download failed for {filename}")
    
    def on_error(self, task, error):
        print(f"❌ Error downloading image: {error}")

# Function to download images and ensure exactly IMAGES_PER are downloaded
def download_images(crawler, keyword, max_num):
    downloaded_filenames.clear()  # Clear list before new download
    downloaded = 0
    try:
        crawler.crawl(
            keyword=keyword,  # Pass the search keyword here
            filters={'size': 'large','type':'photo','color': 'color'},  # Add filters for commercial use, large size, and photo type
            offset=0,  # Start from the last downloaded count
            max_num= 20,
            max_size=None
        )
        
        downloaded = len(downloaded_filenames)
    except Exception as e:
        print(f"❌ Error during crawling: {e}")
    return True

# Main logic
all_captions = []  # To store all captions for the final file
start_idx = 0
with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    items = [line.strip() for line in f if line.strip()]

for costume in items:
    # Create a directory for each costume
    costume_dir = os.path.join(BASE_DIR, costume.replace(" ", "_"))
    #os.makedirs(costume_dir, exist_ok=True)

    # Use default feeder and parser classes (GoogleImageFeeder and GoogleImageParser)
    google_crawler = GoogleImageCrawler(
        downloader_cls=CustomNameDownloader
      #  storage={'root_dir': costume_dir}  # Pass the custom directory for each costume
    )

    # Create search keyword
    keyword = f"{costume}"  # Create the search keyword
    
    print(f"Starting to download images for {costume}")
    
    # Download images for this costume
    success = download_images(google_crawler, keyword, IMAGES_PER)
   

    # Add the downloaded filenames and costume to the captions list
    for i, filename in enumerate(downloaded_filenames):
        idx = start_idx + 1
        all_captions.append(f"{filename}#{idx}\t{costume}")

    if success:
        print(f"✅ Successfully downloaded {IMAGES_PER} images for {costume}")
    else:
        print(f"❌ Failed to download {IMAGES_PER} images for {costume}. Only downloaded {len(downloaded_filenames)} images.")

    # Optional delay to avoid rate-limiting or too many requests in a short time
    time.sleep(random.uniform(1, 3))  # Random sleep be

# Save captions to a file at the end
with open('captions.txt', 'a', encoding='utf-8') as f:
    for caption in all_captions:
        f.write(caption + '\n')

print("✅ All captions saved to captions.txt")