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
parser = argparse.ArgumentParser(description="Indian monument image crawler using Google or Bing")
parser.add_argument(
    "--engine",
    choices=["google", "bing"],
    default="google",
    help="Search engine to use for image crawling (google or bing). Default is google."
)
args = parser.parse_args()
CRAWLER_ENGINE = args.engine

# -------------------------------
# Monuments by Indian State / UT
# -------------------------------
indian_monuments_by_state = {
    "Delhi": ["Red Fort", "Qutub Minar", "India Gate", "Lotus Temple", "Humayun's Tomb"],
    "Uttar Pradesh": ["Taj Mahal", "Agra Fort", "Fatehpur Sikri", "Sarnath Stupa", "Bara Imambara"],
    "Rajasthan": ["Hawa Mahal", "Amber Fort", "City Palace Udaipur", "Jantar Mantar", "Mehrangarh Fort"],
    "Tamil Nadu": ["Brihadeeswara Temple", "Meenakshi Temple", "Shore Temple", "Ramanathaswamy Temple"],
    "Karnataka": ["Gol Gumbaz", "Mysore Palace", "Hampi Group of Monuments", "Halebidu Temple", "Badami Caves"],
    "Maharashtra": ["Gateway of India", "Ajanta Caves", "Ellora Caves", "Raigad Fort", "Shaniwar Wada"],
    "Madhya Pradesh": ["Khajuraho Temples", "Sanchi Stupa", "Gwalior Fort", "Bhimbetka Caves", "Orchha Fort"],
    "West Bengal": ["Victoria Memorial", "Howrah Bridge", "Dakshineswar Temple", "Indian Museum", "St. Paul's Cathedral"],
    "Odisha": ["Konark Sun Temple", "Jagannath Temple", "Lingaraja Temple", "Mukteshwar Temple", "Rajarani Temple"],
    "Jammu & Kashmir": ["Shankaracharya Temple", "Mughal Gardens", "Hari Parbat Fort", "Pari Mahal"],
    "Ladakh": ["Leh Palace", "Thiksey Monastery", "Diskit Monastery", "Shanti Stupa", "Hemis Monastery"],
    "Punjab": ["Golden Temple", "Jallianwala Bagh", "Wagah Border", "Sheesh Mahal Patiala"],
    "Haryana": ["Panipat Fort", "Brahma Sarovar", "Kurukshetra Panorama", "Sheikh Chilli's Tomb"],
    "Bihar": ["Mahabodhi Temple", "Nalanda Ruins", "Vikramshila University", "Patna Sahib Gurudwara"],
    "Jharkhand": ["Jagannath Temple Ranchi", "Maluti Temples", "Netarhat Church", "Sun Temple Bundu"],
    "Chhattisgarh": ["Bhoramdeo Temple", "Kanger Valley Caves", "Rajim Group of Temples"],
    "Andhra Pradesh": ["Charminar", "Golconda Fort", "Lepakshi Temple", "Undavalli Caves"],
    "Telangana": ["Chowmahalla Palace", "Qutb Shahi Tombs", "Ramappa Temple", "Bhadrakali Temple"],
    "Gujarat": ["Sun Temple Modhera", "Rani ki Vav", "Somnath Temple", "Dwarkadhish Temple", "Laxmi Vilas Palace"],
    "Goa": ["Basilica of Bom Jesus", "Se Cathedral", "Fort Aguada", "Chapora Fort", "Reis Magos Fort"],
    "Kerala": ["Padmanabhaswamy Temple", "Bekal Fort", "Mattancherry Palace", "St. Francis Church", "Thrissur Pooram Grounds"],
    "Assam": ["Kamakhya Temple", "Sivasagar Temples", "Rang Ghar", "Kareng Ghar"],
    "Manipur": ["Kangla Fort", "Shree Govindajee Temple", "Ima Keithel"],
    "Meghalaya": ["Mawphlang Sacred Forest", "Nartiang Monoliths", "Living Root Bridge"],
    "Tripura": ["Ujjayanta Palace", "Neermahal", "Tripura Sundari Temple"],
    "Sikkim": ["Rumtek Monastery", "Pemayangtse Monastery", "Tashiding Monastery"],
    "Arunachal Pradesh": ["Tawang Monastery", "Ita Fort", "Bhismaknagar Fort"],
    "Nagaland": ["Dzukou Valley Heritage", "Khonoma Fort Village"],
    "Mizoram": ["Solomon Temple Aizawl", "Khuangchera Puk Cave"],
    "Uttarakhand": ["Kedarnath Temple", "Badrinath Temple", "Jageshwar Temples", "Har Ki Pauri"],
    "Himachal Pradesh": ["Hadimba Temple", "Tashijong Monastery", "Key Monastery", "Jwalamukhi Temple"],
    "Andaman & Nicobar Islands": ["Cellular Jail", "Ross Island Church Ruins", "Japanese Bunkers"],
    "Chandigarh": ["Capitol Complex", "Open Hand Monument", "Rock Garden"],
    "Puducherry": ["French War Memorial", "Auroville Matrimandir", "Immaculate Conception Cathedral"]
}

# -------------------------------
# Query Templates
# -------------------------------
query_templates = [
    "{monument} monument in {state}, India",
    "{monument} heritage site in {state}",
    "historical site {monument} from {state}, India",
    "architecture of {monument} in {state}"
]

# -------------------------------
# Output directory (Single folder)
# -------------------------------
image_dir = "monument_images"
log_file_path = "monument_log.csv"
images_per_monument = 4
os.makedirs(image_dir, exist_ok=True)

# -------------------------------
# Custom Downloader (with UUID)
# -------------------------------
class CustomDownloader(ImageDownloader):
    def get_filename(self, task, default_ext):
        return f"{uuid.uuid4().hex[:16]}.{default_ext}"

    def download(self, task, default_ext, timeout=5, max_retry=1, **kwargs):
        if default_ext.lower() not in ["jpg", "jpeg"]:
            print(f"Skipping file: .{default_ext}")
            return False
        return super().download(task, default_ext, timeout, max_retry, **kwargs)

# -------------------------------
# Main crawling loop
# -------------------------------
with open(log_file_path, "w") as log_file:
    log_file.write("filename,monument,state,query\n")

    for state, monuments in indian_monuments_by_state.items():
        for monument in monuments:
            query = random.choice(query_templates).format(monument=monument, state=state)
            print(f"\nDownloading images for: {query} using {CRAWLER_ENGINE.title()}")

            crawler_class = BingImageCrawler if CRAWLER_ENGINE == "bing" else GoogleImageCrawler

            crawler = crawler_class(
                downloader_cls=CustomDownloader,
                storage={"root_dir": image_dir},
                log_level="ERROR"
            )

            try:
                crawler.crawl(
                    keyword=query,
                    max_num=images_per_monument,
                    filters={"type": "photo", "size": "medium"},
                    file_idx_offset='auto'
                )
            except Exception as e:
                print(f"Error downloading for {monument}: {e}")
                continue

            # Log metadata
            for filename in os.listdir(image_dir):
                if filename.endswith((".jpg", ".jpeg")):
                    log_file.write(f"{filename},{monument},{state},{query}\n")

print(f"\n✅ Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
