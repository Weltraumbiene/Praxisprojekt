import subprocess
import json
import tempfile
import os

def launch_browser_with_url(url: str, inject_axe: bool = False) -> dict:
    """
    Lädt eine Webseite mit Puppeteer und gibt HTML, Titel und URL zurück.
    Optional kann axe-core mitgeladen werden.
    """
    script = f"""
const puppeteer = require('puppeteer');

(async () => {{
    const browser = await puppeteer.launch({{ headless: true }});
    const page = await browser.newPage();
    await page.goto('{url}', {{ waitUntil: 'networkidle2' }});

    {"await page.addScriptTag({ url: 'https://cdn.jsdelivr.net/npm/axe-core/axe.min.js' });" if inject_axe else ""}

    const result = {{
        html: await page.content(),
        title: await page.title(),
        url: page.url()
    }};

    console.log(JSON.stringify(result));
    await browser.close();
}})().catch(err => {{
    console.error(err);
    process.exit(1);
}});
"""

    with tempfile.NamedTemporaryFile(delete=False, suffix=".js", mode="w", encoding="utf-8") as f:
        f.write(script)
        js_path = f.name

    try:
        result = subprocess.run(["node", js_path], capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            raise RuntimeError("Fehler beim Seitenladen: " + result.stderr)

        return json.loads(result.stdout)
    finally:
        os.remove(js_path)

def extract_css_from_url(url: str) -> str:
    """
    Extrahiert alle CSS-Stile direkt aus einer Seite (inline & extern geladen),
    kombiniert sie zu einem einzigen CSS-String.
    """
    script = f"""
const puppeteer = require('puppeteer');

(async () => {{
    const browser = await puppeteer.launch({{ headless: true }});
    const page = await browser.newPage();
    await page.goto('{url}', {{ waitUntil: 'networkidle2' }});

    const styles = await page.evaluate(async () => {{
        const texts = [];

        // Inline-Styles aus <style>
        document.querySelectorAll('style').forEach(style => {{
            texts.push(style.innerHTML);
        }});

        // Externe Stylesheets laden und hinzufügen
        const promises = Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(link => {{
            return fetch(link.href).then(res => res.text()).catch(() => '');
        }});

        const externals = await Promise.all(promises);
        return texts.concat(externals);
    }});

    console.log(JSON.stringify(styles));
    await browser.close();
}})().catch(err => {{
    console.error(err);
    process.exit(1);
}});
"""

    # JavaScript-Code in temporäre Datei schreiben
    with tempfile.NamedTemporaryFile(delete=False, suffix=".js", mode="w", encoding="utf-8") as f:
        f.write(script)
        js_path = f.name

    try:
        result = subprocess.run(["node", js_path], capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            raise RuntimeError("Fehler beim CSS-Extrahieren: " + result.stderr)

        css_blocks = json.loads(result.stdout)
        return "\n".join(css_blocks)
    finally:
        os.remove(js_path)
