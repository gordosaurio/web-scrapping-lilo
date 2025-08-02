# Prima Coffee Scraper ☕️

Welcome! This project is a web scraper built with **Selenium** to extract coffee brewing products from [Prima Coffee](https://prima-coffee.com/brew/coffee). It collects both general product listings and detailed information for analysis.

---

## 🚀 Features

- Collects product **titles**, **URLs**, and **prices** from all listing pages.
- Supports **pagination**, so you won’t miss a single item.
- Automatically selects the **top 5 cheapest products** and scrapes their:
  - Reviews
  - Star ratings
  - SKU, UPC, and MPN
  - Condition
  - Full description
  - Product images
- Downloads all top 5 product images locally.
- Outputs the data into **CSV files** for easy analysis or integration.

---

## 🛠️ Setup

1. **Clone this repository** to your machine:

   ```bash
   git clone https://github.com/yourusername/prima-coffee-scraper.git
   cd prima-coffee-scraper

# (Optional but recommended) Create and activate virtual environment
python -m venv venv && source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the scraper
python coffee.py
