# Indian Traditional Food Image Crawler

This script uses [`icrawler`](https://github.com/hellock/icrawler) to download traditional Indian food images from **Google** or **Bing**, and auto-generates simple captions for each image.

---

## Features

- Choose search engine: **Google** or **Bing**
- Downloads `.jpg` / `.jpeg` images only
- Auto-generates 3 template based captions per image
- Organizes images and captions for dataset creation
- CLI interface for easy usage

---

## Requirements

Install Python dependency:

```bash
pip install icrawler
```

## How to Run

To download images from Google:
```bash
python3 food_images_mod.py --engine google
```

To use Bing instead:
```bash
python3 food_images_mod.py --engine bing
```

## Output Structure
```
indian_traditional_foods/
├── images/                            # Downloaded image files
└── indian_traditional_foods.token.txt # Captions
```

## Sample Captions

Each image gets 3 captions like:
```
fd8f8aa82d7e42f1.jpg#0	A dish called Dal Baati Churma from Rajasthan.
fd8f8aa82d7e42f1.jpg#1	Dal Baati Churma is a popular traditional food in Rajasthan, India.
fd8f8aa82d7e42f1.jpg#2	People in Rajasthan often enjoy Dal Baati Churma during festivals or meals.
```

## Configuration

Edit the script to customize:

States & dishes:
```
indian_foods_by_state = {
    "Rajasthan": ["Dal Baati Churma", "Laal Maas", ...]
}
```
Output folder/files & images per dish
```
base_dir = "indian_traditional_foods"
image_dir = os.path.join(base_dir, "images")
caption_file = os.path.join(base_dir, "indian_traditional_foods.token.txt")
images_per_dish = 10
```

Caption and query templates:
```
caption_templates = [...]
query_templates = [...]
```


