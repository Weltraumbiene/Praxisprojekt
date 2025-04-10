# core/aria_checker.py

from bs4 import BeautifulSoup

# Liste typischer, zulässiger ARIA-Rollen (nicht vollständig)
valid_aria_roles = {
    "banner", "main", "navigation", "contentinfo", "complementary", "form", "search",
    "button", "link", "heading", "textbox", "checkbox", "radio", "listbox", "dialog",
    "tab", "tabpanel", "alert", "tooltip", "progressbar", "menu", "menubar", "menuitem",
    "region", "status", "switch", "grid", "row", "cell", "columnheader", "rowheader"
}

def check_aria_usage(html: str) -> list[dict]:
    """
    Prüft ARIA-Rollen und Attribute auf Probleme.
    Gibt eine Liste von Warnungen oder Hinweisen zurück.
    """
    soup = BeautifulSoup(html, "html.parser")
    findings = []

    for el in soup.find_all(attrs={"role": True}):
        role = el.get("role")
        if role not in valid_aria_roles:
            findings.append({
                "type": "warn",
                "message": f'Unbekannte oder ungültige Rolle: role="{role}"',
                "element": str(el)[:150]
            })

        # Überprüfe, ob ein beschreibendes Label vorhanden ist
        if role in {"button", "link", "textbox", "switch", "checkbox"} and not (
            el.get("aria-label") or el.get("aria-labelledby") or el.text.strip()
        ):
            findings.append({
                "type": "warn",
                "message": f'role="{role}" ohne beschreibenden Text oder aria-label',
                "element": str(el)[:150]
            })

    # Allgemeine Checks: aria-hidden an interaktiven Elementen
    for el in soup.find_all(attrs={"aria-hidden": "true"}):
        if el.name in {"a", "button", "input", "select", "textarea"}:
            findings.append({
                "type": "warn",
                "message": f'Interaktives Element mit aria-hidden="true" entdeckt: <{el.name}>',
                "element": str(el)[:150]
            })

    return findings