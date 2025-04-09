# core/axe.py

import subprocess
import json
import tempfile
import os

def run_axe_scan(url: str = None, html: str = None, tags: list[str] = None) -> dict:
    if not url and not html:
        raise ValueError("Entweder 'url' oder 'html' muss angegeben sein.")

    run_tags = json.dumps(tags or ["wcag2a", "wcag2aa", "best-practice"])

    if url:
        script = f"""
        const puppeteer = require('puppeteer');

        (async () => {{
            const browser = await puppeteer.launch();
            const page = await browser.newPage();
            await page.goto("{url}");
            await page.addScriptTag({{ url: 'https://cdn.jsdelivr.net/npm/axe-core@4.3.5/axe.min.js' }});

            const results = await page.evaluate(async (tags) => {{
                return await axe.run({{
                    runOnly: {{ type: 'tag', values: tags }}
                }});
            }}, {run_tags});

            console.log(JSON.stringify(results));
            await browser.close();
        }})().catch(err => {{
            console.error(err);
            process.exit(1);
        }});
        """
    else:
        html_escaped = html.replace("\\", "\\\\").replace("`", "\\`")
        script = f"""
        const puppeteer = require('puppeteer');

        (async () => {{
            const browser = await puppeteer.launch();
            const page = await browser.newPage();
            await page.setContent(`{html_escaped}`);
            await page.addScriptTag({{ url: 'https://cdn.jsdelivr.net/npm/axe-core@4.3.5/axe.min.js' }});

            const results = await page.evaluate(async (tags) => {{
                return await axe.run({{
                    runOnly: {{ type: 'tag', values: tags }}
                }});
            }}, {run_tags});

            console.log(JSON.stringify(results));
            await browser.close();
        }})().catch(err => {{
            console.error(err);
            process.exit(1);
        }});
        """

    # ➕ SCHRITT: Temporäre .js-Datei schreiben
    with tempfile.NamedTemporaryFile(delete=False, suffix=".js", mode="w", encoding="utf-8") as f:
        f.write(script)
        js_path = f.name

    try:
        result = subprocess.run(["node", js_path], capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            raise RuntimeError(f"AXE Scan Fehler: {result.stderr.strip()}")
        return json.loads(result.stdout)
    finally:
        # 🧹 Aufräumen
        os.remove(js_path)
