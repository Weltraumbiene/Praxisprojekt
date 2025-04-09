# core/validator.py

def validate_structure(data: dict) -> list[dict]:
    """
    Prüft semantische Anforderungen an HTML-Struktur.
    :param data: Dictionary mit extrahierten HTML-Daten
    :return: Liste von Prüfproblemen (Typ + Nachricht)
    """
    issues = []

    # 1. <h1> Prüfung
    h1s = [h for h in data.get("headings", []) if h.get("tag", "").upper() == "H1"]
    if len(h1s) == 0:
        issues.append({"type": "Fehler", "message": "Es wurde kein <h1>-Element gefunden."})
    elif len(h1s) > 1:
        issues.append({"type": "Fehler", "message": f"Es wurden {len(h1s)} <h1>-Elemente gefunden."})

    # 2. Bilder ohne alt-Text
    for img in data.get("images", []):
        if not img.get("alt"):
            issues.append({
                "type": "Fehler",
                "message": f"Bild ohne alt-Text: {img.get('src', 'Unbekannt')}"
            })

    # 3. Leere Links
    for link in data.get("links", []):
        if not link.get("text", "").strip():
            issues.append({
                "type": "Fehler",
                "message": f"Leerer Linktext: {link.get('href', 'Unbekannt')}"
            })

    # 4. Labels ohne for
    for label in data.get("labels", []):
        if not label.get("for"):
            issues.append({
                "type": "Warnung",
                "message": f'Label ohne "for": {label.get("text", "")}'
            })

    # 5. Iframes ohne title
    for iframe in data.get("iframes", []):
        if not iframe.get("title"):
            issues.append({
                "type": "Fehler",
                "message": f'Iframe ohne title: {iframe.get("src", "Unbekannt")}'
            })

    # 6. Fehlendes lang-Attribut
    if not data.get("language") or data.get("language") == "not set":
        issues.append({"type": "Fehler", "message": "Es wurde kein lang-Attribut am <html>-Element gefunden."})

    return issues
