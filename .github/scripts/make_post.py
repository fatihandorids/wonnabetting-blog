import os, json, datetime, random, re, requests
from bs4 import BeautifulSoup as bs

topics = ["football betting tips","soccer predictions today","free betting tips",
          "high odds predictions","daily football picks","over 2.5 goals tips",
          "both teams to score tips","accumulator tips","paid betting tips",
          "sure bet predictions","betting tips","betting predictions",
          "betting analysis","betting news","betting picks",
          "betting advice","betting strategies"]
topic = topics[datetime.datetime.now().day % len(topics)]

rss_url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
rss = requests.get(rss_url, timeout=10).text
titles = re.findall(r"<title>(.*?)</title>", rss)[1:4]
python if not titles: titles = ["Default Title 1", "Default Title 2"]
seed = random.choice(titles)

prompt = f"""
Write a 650-word SEO-ready English blog post about “{topic}” inspired by “{seed}”.
Include one <h1>, two <h2>, three <h3>, meta 150 chars, and one link to /about.
"""
gem_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
payload = {"contents":[{"parts":[{"text":prompt}]}]}
headers = {"Content-Type":"application/json"}
resp = requests.post(f"{gem_url}?key={os.getenv('GEMINI_KEY')}", json=payload, headers=headers).json()
content = resp["candidates"][0]["content"]["parts"][0]["text"]

slug = re.sub(r'[^a-z0-9]+','-',content.split('\n')[0].lower())[:60].strip('-')
today = datetime.date.today().isoformat()
word_count = len(content.split())
read_time = max(1, word_count // 200)

images = [f"https://source.unsplash.com/800x450/?{topic}&sig={i}" for i in range(3)]
blocks = content.split("\n\n")
for i,img in enumerate(images):
    blocks[i] = f'<img src="{img}" alt="Image about {topic}" loading="lazy">\n\n{blocks[i]}'
final = "\n\n".join(blocks)

schema = {
  "@context":"https://schema.org",
  "@type":"BlogPosting",
  "headline":content.split('\n')[0],
  "description":re.sub(r'<[^>]+>','',content)[:150]+"...",
  "url":f"https://wonnabetting.com/blog/{slug}",
  "datePublished":today+"T09:00:00+03:00",
  "dateModified":today+"T09:05:00+03:00",
  "author":{"@type":"Person","name":"Wonna Betting Tips","url":"https://wonnabetting.com/author"},
  "image":images[0],
  "wordCount":word_count,
  "timeRequired":f"PT{read_time}M"
}

gist_id = os.getenv("GIST_ID")
token   = os.getenv("GH_TOKEN")
gist_url = f"https://api.github.com/gists/{gist_id}"
old = requests.get(gist_url).json()
data = json.loads(old["files"]["articles.json"]["content"])
data.insert(0,{
  "title":content.split('\n')[0],
  "slug":slug,
  "content":final,
  "date":today,
  "readTime":read_time,
  "wordCount":word_count,
  "author":"Wonna Betting Tips",
  "schema":schema
})
patch = {"files":{"articles.json":{"content":json.dumps(data,indent=2)}}}
requests.patch(gist_url, json=patch, headers={"Authorization":f"token {token}"})
