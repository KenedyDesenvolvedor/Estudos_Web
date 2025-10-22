import feedparser
import tkinter as tk
from tkinter import ttk
import webbrowser
from googletrans import Translator
import threading

# -------------------- Feeds --------------------
feeds = {
    "Top Globais": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.reuters.com/rssFeed/worldNews"
    ],
    "Estados Unidos": [
        "https://rss.nytimes.com/services/xml/rss/nyt/US.xml"
    ],
    "China": [
        "https://www.scmp.com/rss/91/feed"
    ],
    "Rússia": [
        "https://feeds.bbci.co.uk/russian/rss.xml"
    ],
    "Índia": [
        "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
    ],
    "Brasil": [
        "https://g1.globo.com/rss/g1/politica/"
    ]
}

# -------------------- Tradutor --------------------
translator = Translator()

def translate_text(text, dest='pt'):
    try:
        return translator.translate(text, dest=dest).text
    except:
        return text

# -------------------- Funções --------------------
def fetch_news(url):
    feed = feedparser.parse(url)
    news_items = []
    for entry in feed.entries:
        news_items.append({
            "title": entry.title,
            "link": entry.link,
            "summary": getattr(entry, "summary", ""),
            "date": getattr(entry, "published", "")
        })
    return news_items

def get_top_news(feed_list, max_items=10):
    all_news = []
    for url in feed_list:
        all_news.extend(fetch_news(url))
    all_news.sort(key=lambda x: x.get("date",""), reverse=True)
    return all_news[:max_items]

def open_link(event):
    webbrowser.open_new(event.widget.link)

def add_news_threadsafe(frame, news_item):
    """Tradução em background e atualização na thread principal"""
    def worker():
        title_text = translate_text(news_item["title"], dest="pt")
        summary_text = translate_text(news_item.get("summary", ""), dest="pt")

        def update_ui():
            link = tk.Label(frame, text=title_text, fg="blue", cursor="hand2", wraplength=600, justify="left")
            link.pack(anchor="w", padx=10, pady=2)
            link.link = news_item["link"]
            link.bind("<Button-1>", open_link)

            if summary_text:
                summary_lbl = tk.Label(frame, text=summary_text, wraplength=600, justify="left", fg="#333")
                summary_lbl.pack(anchor="w", padx=20)
            if news_item.get("date"):
                date_lbl = tk.Label(frame, text=news_item["date"], font=("Arial", 8), fg="#555")
                date_lbl.pack(anchor="w", padx=20, pady=(0,5))

        root.after(0, update_ui)

    threading.Thread(target=worker).start()

def create_section(frame, title, news_list, color="#1a73e8"):
    lbl = ttk.Label(frame, text=title, font=("Arial", 14, "bold"), foreground=color)
    lbl.pack(pady=(10,5), anchor="w")

    for news in news_list:
        add_news_threadsafe(frame, news)

# -------------------- GUI --------------------
root = tk.Tk()
root.title("Dashboard de Notícias de Geopolítica")
root.geometry("700x800")

canvas = tk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# -------------------- Cores por país --------------------
colors = {
    "Top Globais": "#1a73e8",
    "Estados Unidos": "#ff4500",
    "China": "#228B22",
    "Rússia": "#8B0000",
    "Índia": "#FF8C00",
    "Brasil": "#006400"
}

# -------------------- Carrega notícias --------------------
for section, urls in feeds.items():
    news = get_top_news(urls, 10)
    create_section(scrollable_frame, section, news, colors.get(section, "#1a73e8"))

root.mainloop()

