import os
import requests
from supabase import create_client, Client
import json

# API Anahtarları ve URL'leri GitHub Secrets'tan alınır
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_API_KEY = os.environ.get("SUPABASE_API_KEY")

# Supabase istemcisi oluşturulur
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Anahtar kelimeler
KEYWORDS = "betting tips, betting predictions, betting picks, football betting news, sports betting"

def get_serpapi_results():
    """SerpApi'den Google arama sonuçlarını çeker."""
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": KEYWORDS,
        "api_key": SERPAPI_API_KEY,
        "gl": "us",
        "hl": "en"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def generate_article_with_gemini(serpapi_data):
    """Gemini API ile SEO dostu makale oluşturur."""
    prompt = f"""
    Aşağıdaki Google arama sonuçlarından elde edilen verilere dayanarak, "betting tips" anahtar kelimesine odaklanan 350 kelimelik, SEO dostu, bilgilendirici ve okunabilir bir blog makalesi oluştur. Makale, "betting tips" ve "betting predictions" anahtar kelimelerini içermelidir.

    Arama Sonuçları:
    {json.dumps(serpapi_data, indent=2)}

    Makale başlığını da oluştur. Başlık ve makale içeriğini JSON formatında döndür. Örnek: {{"title": "Makale Başlığı", "content": "Makale içeriği..."}}
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    gemini_response = response.json()
    
    try:
        raw_text = gemini_response["candidates"][0]["content"]["parts"][0]["text"].replace('```json', '').replace('```', '').strip()
        return json.loads(raw_text)
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Gemini yanıtı işlenirken hata oluştu: {e}")
        return None

def save_to_supabase(article_data):
    """Oluşturulan makaleyi Supabase'e kaydeder."""
    if not article_data:
        print("Makale verisi boş, Supabase'e kaydedilemiyor.")
        return

    data, count = supabase.table('blog_yazilari').insert({
        "title": article_data["title"],
        "content": article_data["content"]
    }).execute()
    
    print("Makale Supabase'e başarıyla kaydedildi.")

if __name__ == "__main__":
    print("Otomasyon başlatılıyor...")
    serpapi_results = get_serpapi_results()
    print("SerpApi verileri çekildi.")
    
    article_content = generate_article_with_gemini(serpapi_results)
    
    if article_content:
        print("Makale Gemini tarafından oluşturuldu.")
        save_to_supabase(article_content)
    else:
        print("Makale oluşturma başarısız oldu.")
    print("Otomasyon tamamlandı.")
