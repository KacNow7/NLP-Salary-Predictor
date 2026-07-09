from playwright.sync_api import sync_playwright
import pandas as pd
from sqlalchemy import create_engine
import time
import re

def parse_salary(salary_text: str) -> float:
    if not salary_text:
        return 0.0
    cleaned = re.sub(r'[^\d-]', '', salary_text)
    if not cleaned:
        return 0.0
    parts = cleaned.split('-')
    if len(parts) == 2:
        return (float(parts[0]) + float(parts[1])) / 2
    elif len(parts) == 1:
        return float(parts[0])
    return 0.0

def find_salary_string(text: str) -> str:
    """Wyciąga bezpiecznie sam ciąg walutowy z brudnego tekstu (np. '15 000 - 20 000 PLN')"""
    match = re.search(r'([\d\s]+(?:-[\d\s]+)?)\s*(PLN|EUR|USD)', text, re.IGNORECASE)
    return match.group(0) if match else ""

def extract_jobs_from_portal(page, max_scrolls=5):
    print("Nawigowanie do portalu z ofertami (JustJoin.it)...")
    page.goto("https://justjoin.it/warszawa/python")
    
    print("Sprawdzanie obecności banera Cookies...")
    try:
        page.locator("text='Accept all'").first.click(timeout=5000)
        print("Baner Cookies zamknięty!")
        time.sleep(1)
    except Exception:
        print("Brak banera Cookies (lub już zniknął).")
    
    print("Czekam 5 sekund na wyrenderowanie ofert...")
    time.sleep(5) 

    print("Rozpoczynam przewijanie strony (Infinite Scroll)...")
    for i in range(max_scrolls):
        page.keyboard.press("PageDown")
        page.keyboard.press("PageDown")
        time.sleep(1.5)

    print("Wstrzykiwanie native JavaScript do przeglądarki...")
    
    # --- MAGIA JAVASCRIPT ---
    # Uruchamiamy kod bezpośrednio w silniku przeglądarki. 
    # Szuka on linku, a potem wspina się po drzewie DOM (max 6 poziomów), 
    # aż złapie całą kartę oferty z tekstem waluty.
    raw_offers = page.evaluate("""() => {
        let results = [];
        let links = document.querySelectorAll('a');
        
        links.forEach(a => {
            if(a.href && a.href.includes('justjoin.it')) {
                let current = a;
                let foundText = "";
                
                // Wspinamy się w górę drzewa DOM do rodziców
                for(let i=0; i<6; i++) {
                    if(current.parentElement) {
                        current = current.parentElement;
                        let text = current.innerText || "";
                        // Jeśli w kontenerze pojawi się waluta, mamy naszą kartę!
                        if(text.includes('PLN') || text.includes('EUR') || text.includes('USD')) {
                            foundText = text;
                            break;
                        }
                    }
                }
                
                if(foundText) {
                    results.push({url: a.href, text: foundText});
                }
            }
        });
        return results;
    }""")
    # ------------------------

    print(f"JavaScript zwrócił {len(raw_offers)} potencjalnych ofert. Ekstrakcja walut w Pythonie...")
    scraped_data = []
    
    for item in raw_offers:
        url = item['url']
        # Czyścimy tekst ze zbędnych spacji i enterów
        card_text_clean = " ".join(item['text'].split())

        # Wyciągamy czysty tekst wynagrodzenia naszym Regexem
        salary_str = find_salary_string(card_text_clean)
        if not salary_str:
            continue
            
        salary_num = parse_salary(salary_str)
        
        # Przeliczanie walut na PLN
        if "EUR" in salary_str.upper():
            salary_num *= 4.3 
        elif "USD" in salary_str.upper():
            salary_num *= 4.0
        
        if salary_num == 0:
            continue

        # Tytuł to najczęściej początek tekstu (pierwsze 4 słowa)
        title = " ".join(card_text_clean.split()[:4]) 

        scraped_data.append({
            "title": title,
            "technologies": card_text_clean, 
            "salary": salary_num,
            "url": url
        })
            
    # Usuwamy duplikaty powstałe przez scrollowanie i odświeżanie Reacta
    unique_data = list({v['url']:v for v in scraped_data}.values())
    print(f"SUKCES! Udało się wyciągnąć {len(unique_data)} unikalnych, poprawnych ofert pracy!")
    
    return unique_data

def save_to_database(offers: list[dict]):
    if not offers:
        print("Nie zebrano żadnych ofert z podaną pensją.")
        return

    print(f"Zapisywanie {len(offers)} ofert do bazy ML...")
    df = pd.DataFrame(offers)
    engine = create_engine('sqlite:///data/jobs_database.db')
    df.to_sql('job_offers', con=engine, if_exists='append', index=False)
    print("Sukces! Dane zasiliły rurociąg ML.")

def run_pipeline():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, jak Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        offers = extract_jobs_from_portal(page, max_scrolls=8)
        save_to_database(offers)
        
        browser.close()

if __name__ == "__main__":
    run_pipeline()