# core/focus_tracker.py

import subprocess
import json
import tempfile
import os

def track_focus_order(url: str) -> list:
    """
    Besucht die Seite und protokolliert die Fokusreihenfolge beim Drücken der Tabulatortaste.
    Gibt eine Liste der fokussierten Elemente (als HTML) zurück.
    """
    script = f"""
    const puppeteer = require('puppeteer');

    (async () => {{
        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        await page.goto('{url}', {{ waitUntil: 'networkidle2' }});

        const focusedElements = [];
        for (let i = 0; i < 50; i++) {{
            await page.keyboard.press('Tab');
            await page.evaluate(() => new Promise(resolve => setTimeout(resolve, 100)));
            const active = await page.evaluate(() => document.activeElement?.outerHTML || null);
            if (!active || focusedElements.includes(active)) break;
            focusedElements.push(active);
        }}

        console.log(JSON.stringify(focusedElements));
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
            raise RuntimeError("Fehler beim Fokus-Tracking: " + result.stderr)
        return json.loads(result.stdout)
    finally:
        os.remove(js_path)