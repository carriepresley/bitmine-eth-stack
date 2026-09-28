#!/usr/bin/env python3
"""Render og.jpg, the 1200x630 link-preview image for the public page.

Optional. The weekly update doesn't need it: the image carries no weekly
numbers, only the scene at its latest week. Rerun it after a redesign.

Needs Playwright with Chromium and Pillow, and network access to Google
Fonts. Run from anywhere after scripts/build.py:
    python3 scripts/og_image.py
"""
import asyncio
import io
import os
from pathlib import Path

from PIL import Image
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
W, H, SCALE = 1200, 630, 2

CSS = f"""
html,body{{width:{W}px;height:{H}px;overflow:hidden!important;margin:0}}
.obs{{height:{H}px}}
.topbar,.intro,.strip,.transport,#stake,main.below,.vlabel,.toast{{display:none!important}}
.wrap.obs-inner{{max-width:none;margin:0;padding:0;height:{H}px;position:relative}}
#viz{{position:absolute;left:440px;top:-10px;width:760px;height:{H + 20}px}}
#og{{position:absolute;left:64px;top:0;bottom:0;width:420px;z-index:3;
  display:flex;flex-direction:column;justify-content:center;gap:22px}}
#og .m{{display:flex;align-items:center;gap:12px;font:500 15px/1.4 var(--f-mono);
  letter-spacing:.14em;text-transform:uppercase;color:var(--ink-2)}}
#og .m i{{width:13px;height:13px;background:var(--lime);box-shadow:0 0 14px rgba(198,255,0,.85)}}
#og h2{{margin:0;font:600 76px/.98 var(--f-display);color:var(--ink);letter-spacing:-.01em}}
#og h2 span{{color:var(--lime);text-shadow:0 0 28px rgba(198,255,0,.35)}}
#og p{{margin:0;font:400 23px/1.4 var(--f-body);color:var(--ink-2);max-width:380px}}
#og .f{{margin-top:8px;font:500 14px/1.4 var(--f-mono);letter-spacing:.14em;
  text-transform:uppercase;color:var(--ink-3)}}
"""

CARD = """
<div class="m"><i></i>ETH supply &times; BitMine</div>
<h2>BitMine's<br><span>ETH Stack</span></h2>
<p>Every ETH BitMine has bought since June 2025, inside the entire ETH supply.</p>
<div class="f">Updated every Monday</div>
"""


async def main():
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    async with async_playwright() as p:
        browser = await p.chromium.launch(proxy={"server": proxy} if proxy else None)
        page = await browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=SCALE)
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto((ROOT / "index.html").as_uri(), wait_until="networkidle")
        await page.add_style_tag(content=CSS)
        await page.evaluate("""card => {
            const d = document.createElement('div'); d.id = 'og'; d.innerHTML = card;
            document.querySelector('.obs-inner').appendChild(d);
        }""", CARD)
        await page.evaluate("document.fonts.ready")
        # Jump to the latest week. This also stops the autoplay.
        await page.evaluate("""() => {
            const s = document.getElementById('scrub'); s.value = s.max;
            s.dispatchEvent(new Event('input', { bubbles: true }));
        }""")
        await page.wait_for_timeout(2500)          # relayout + holders ring settle
        png = await page.screenshot(clip={"x": 0, "y": 0, "width": W, "height": H})
        await browser.close()
    if errors:
        raise SystemExit(f"page errors: {errors}")
    img = Image.open(io.BytesIO(png)).convert("RGB").resize((W, H), Image.LANCZOS)
    out = ROOT / "og.jpg"
    img.save(out, "JPEG", quality=90, optimize=True, progressive=True)
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    asyncio.run(main())
