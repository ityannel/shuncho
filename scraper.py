import os
import re
import datetime
from datetime import timedelta
import json
import requests
from bs4 import BeautifulSoup
import pdfplumber
import urllib.request
import urllib.parse
import jpholiday

def search_yahoo_image(query):
    if not query or query == "情報なし" or "なし" in query:
        return ""
    query = query.replace('\n', '').replace('\r', '')
    query_enhanced = f"{query} 料理 レシピ"
    encoded_query = urllib.parse.quote(query_enhanced)
    url = f"https://search.yahoo.co.jp/image/search?p={encoded_query}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            match = re.search(r'(https://msp\.c\.yimg\.jp/images/[^\s"\'<]+)', html)
            if match:
                return match.group(1)
    except:
        pass
    return ""

def get_menu_pdf_url(target_date):
    url = "https://www.hakodate-ct.ac.jp/~w-ryou/index.html"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print("Failed to fetch index HTML:", e)
        return None

    links = soup.find_all('a', href=re.compile(r'\.pdf$'))
    for link in links:
        text = link.get_text()
        href = link.get('href')
        match = re.search(r'(\d+)/(\d+).*?(\d+)/(\d+)', text)
        if match:
            m1, d1, m2, d2 = map(int, match.groups())
            year = target_date.year
            start_date = datetime.datetime(year, m1, d1).date()
            end_date = datetime.datetime(year, m2, d2).date()
            
            if start_date > end_date:
                if target_date.month == 1:
                    start_date = datetime.datetime(year - 1, m1, d1).date()
                else:
                    end_date = datetime.datetime(year + 1, m2, d2).date()
                    
            if start_date <= target_date <= end_date:
                if href.startswith('http'):
                    return href
                else:
                    return f"https://www.hakodate-ct.ac.jp/~w-ryou/{href.lstrip('./')}"
    return None

def download_pdf(url, filepath):
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except:
        return False

def extract_meal_items(cell_text, meal_type):
    if not cell_text:
        return "情報なし", ""
    lines = [line.strip() for line in cell_text.split('\n') if line.strip()]
    filtered_lines = [line for line in lines if not any(x in line for x in ["ｴﾈﾙｷﾞｰ", "ﾀﾝﾊﾟｸ", "脂質", "食塩"])]
    if not filtered_lines:
        return "情報なし", ""
        
    if meal_type == "breakfast":
        main_dish = filtered_lines[2] if len(filtered_lines) >= 3 else filtered_lines[-1]
        sides = filtered_lines[3:] if len(filtered_lines) >= 4 else []
    elif meal_type == "lunch":
        main_dish = filtered_lines[0]
        sides = filtered_lines[1:]
    elif meal_type == "dinner":
        main_dish = filtered_lines[2] if len(filtered_lines) >= 3 else filtered_lines[-1]
        sides = filtered_lines[3:] if len(filtered_lines) >= 4 else []
        
    side_str = " / ".join(sides[:3])
    return main_dish, side_str

def get_meal_times_for_date(date_obj):
    is_holiday = date_obj.weekday() >= 5 or jpholiday.is_holiday(date_obj)
    if is_holiday:
        return "07:45", "12:25", "18:00"
    else:
        return "07:25", "12:10", "18:00"

def parse_date_string(date_str, current_year):
    # e.g. "6月24日\n(月)" -> return datetime.date
    match = re.search(r'(\d+)月(\d+)日', date_str)
    if match:
        m, d = map(int, match.groups())
        return datetime.date(current_year, m, d)
    return None

def main():
    # Force JST timezone
    JST = datetime.timezone(timedelta(hours=9), 'JST')
    today = datetime.datetime.now(JST).date()
    
    # We will try to fetch today's PDF and tomorrow's PDF (in case they span different weeks)
    dates_to_check = [today, today + timedelta(days=5)]
    urls_to_parse = set()
    
    for d in dates_to_check:
        url = get_menu_pdf_url(d)
        if url:
            urls_to_parse.add(url)
            
    menu_data = {}
    
    for url in urls_to_parse:
        print(f"Downloading {url}...")
        pdf_path = "temp.pdf"
        if not download_pdf(url, pdf_path):
            continue
            
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            tables = page.extract_tables()
            if not tables or not tables[0]:
                continue
            table = tables[0]
            
            # The first row contains dates
            header_row = table[0]
            for col_idx in range(1, len(header_row)):
                cell = header_row[col_idx]
                if not cell:
                    continue
                parsed_date = parse_date_string(cell, today.year)
                if not parsed_date:
                    continue
                    
                date_key = parsed_date.strftime("%Y-%m-%d")
                print(f"Parsing data for {date_key}...")
                
                b_time, l_time, d_time = get_meal_times_for_date(parsed_date)
                
                # Rows for meals: Breakfast=1, Lunch=5, Dinner=10 (from our earlier analysis)
                try:
                    b_cell = table[1][col_idx]
                    l_cell = table[5][col_idx]
                    d_cell = table[10][col_idx]
                except IndexError:
                    continue
                
                b_main, b_sides = extract_meal_items(b_cell, "breakfast")
                l_main, l_sides = extract_meal_items(l_cell, "lunch")
                d_main, d_sides = extract_meal_items(d_cell, "dinner")
                
                # Fetch images (to save API calls/time, maybe we only fetch if we don't have it, but GitHub Actions has time)
                # Let's fetch all 3
                b_img = search_yahoo_image(b_main)
                l_img = search_yahoo_image(l_main)
                d_img = search_yahoo_image(d_main)
                
                menu_data[date_key] = {
                    "breakfast": {
                        "main_dish": b_main.replace('\n', ''),
                        "side_dishes": b_sides.replace('\n', ''),
                        "image_url": b_img,
                        "time": b_time
                    },
                    "lunch": {
                        "main_dish": l_main.replace('\n', ''),
                        "side_dishes": l_sides.replace('\n', ''),
                        "image_url": l_img,
                        "time": l_time
                    },
                    "dinner": {
                        "main_dish": d_main.replace('\n', ''),
                        "side_dishes": d_sides.replace('\n', ''),
                        "image_url": d_img,
                        "time": d_time
                    }
                }
                
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    # Save to JSON
    with open('menu.json', 'w', encoding='utf-8') as f:
        json.dump(menu_data, f, ensure_ascii=False, indent=2)
        
    print("Generated menu.json successfully!")

if __name__ == "__main__":
    main()
