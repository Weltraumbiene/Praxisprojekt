# core/html_parser.py
from bs4 import BeautifulSoup

def extract_structure_from_html(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')

    # Hilfsfunktion: ARIA-Attribute sammeln
    def get_aria_attrs(tag):
        return {k: v for k, v in tag.attrs.items() if k.startswith('aria-')}

    return {
        "title": soup.title.string.strip() if soup.title else "",
        "language": soup.html.attrs.get("lang", "not set") if soup.html else "not set",

        "headings": [
            {"tag": tag.name.upper(), "text": tag.get_text(strip=True)}
            for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        ],

        "images": [
            {"src": img.get("src", ""), "alt": img.get("alt", "")}
            for img in soup.find_all("img")
        ],

        "links": [
            {"href": a.get("href", ""), "text": a.get_text(strip=True)}
            for a in soup.find_all("a")
        ],

        "labels": [
            {"for": label.get("for", ""), "text": label.get_text(strip=True)}
            for label in soup.find_all("label")
        ],

        "ariaElements": [
            {"tag": tag.name.upper(), "aria": get_aria_attrs(tag)}
            for tag in soup.find_all(attrs=lambda attr: attr and any(k.startswith("aria-") for k in attr))
        ],

        "tables": [
            {
                "headers": [th.get_text(strip=True) for th in table.find_all("th")],
                "rows": len(table.find_all("tr"))
            }
            for table in soup.find_all("table")
        ],

        "iframes": [
            {
                "src": iframe.get("src", ""),
                "title": iframe.get("title", ""),
                "ariaHidden": iframe.get("aria-hidden", "false")
            }
            for iframe in soup.find_all("iframe")
        ]
    }
