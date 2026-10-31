const { chromium } = require('C:/dev/864zeros-publisher-mcp/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
  await page.setContent(`<!DOCTYPE html>
  <html><head><style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Inter, system-ui, sans-serif; }
    body { width: 1200px; height: 630px; background: #F6EFE4; color: #2D2D2D; display: flex; align-items: center; justify-content: space-between; padding: 56px 68px; position: relative; overflow: hidden; }
    .bg-accent { position: absolute; right: -120px; top: -120px; width: 560px; height: 560px; border-radius: 50%; background: radial-gradient(circle, rgba(139,168,136,0.22) 0%, rgba(139,102,66,0.06) 65%, transparent 100%); }
    .left { max-width: 610px; z-index: 2; }
    .badge-row { display: flex; gap: 10px; margin-bottom: 22px; }
    .badge { background: #FDFCF8; border: 1.5px solid #D8CEBE; color: #5C4938; padding: 6px 14px; border-radius: 999px; font-size: 14px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
    .badge.sage { background: #E9F0E8; border-color: #8BA888; color: #2F4B2C; }
    h1 { font-size: 54px; line-height: 1.08; font-weight: 800; color: #2D2D2D; letter-spacing: -0.02em; margin-bottom: 18px; }
    h1 span { color: #8B6642; }
    p { font-size: 22px; line-height: 1.45; color: #4A433C; margin-bottom: 28px; font-weight: 500; }
    .pillars { display: flex; gap: 14px; flex-wrap: wrap; }
    .pill { background: #FDFCF8; border: 1px solid #DFD5C6; padding: 10px 18px; border-radius: 10px; font-size: 16px; font-weight: 700; color: #2D2D2D; box-shadow: 0 2px 6px rgba(45,45,45,0.04); }
    .card { width: 410px; background: #FDFCF8; border: 2px solid #D8CEBE; border-radius: 18px; padding: 24px; box-shadow: 0 18px 40px rgba(45,45,45,0.10); z-index: 2; }
    .card-hdr { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #EAE2D6; padding-bottom: 14px; margin-bottom: 16px; }
    .card-title { font-weight: 800; font-size: 18px; color: #2D2D2D; }
    .card-tag { font-size: 12px; font-weight: 700; background: #E9F0E8; color: #2F4B2C; padding: 4px 10px; border-radius: 99px; }
    .item { background: #F6EFE4; border: 1px solid #E2D9C8; border-radius: 12px; padding: 14px; margin-bottom: 12px; }
    .item-t { font-weight: 700; font-size: 15px; color: #2D2D2D; margin-bottom: 4px; }
    .item-n { font-size: 13px; color: #5C5346; margin-bottom: 10px; font-style: italic; }
    .chips { display: flex; gap: 6px; margin-bottom: 10px; }
    .chip { font-size: 11px; font-weight: 700; background: #EAE2D6; color: #5C4938; padding: 2px 8px; border-radius: 6px; }
    .btns { display: flex; gap: 8px; }
    .btn { flex: 1; text-align: center; padding: 7px 10px; border-radius: 8px; font-size: 12px; font-weight: 700; }
    .btn-md { background: #FDFCF8; border: 1px solid #C8B9A6; color: #2D2D2D; }
    .btn-ob { background: #8B6642; color: #FDFCF8; }
  </style></head><body>
    <div class='bg-accent'></div>
    <div class='left'>
      <div class='badge-row'>
        <span class='badge sage'>[CMC] LinkLater v1.0.1</span>
        <span class='badge'>Chrome &amp; Edge MV3</span>
        <span class='badge'>100% Local</span>
      </div>
      <h1>Save Links With Context. <span>Send to Obsidian.</span></h1>
      <p>Your local read-later triage queue with personal notes &amp; tags. Export clean Markdown (.md) free forever or bridge straight into your Obsidian vault in 1 click.</p>
      <div class='pillars'>
        <div class='pill'>✓ Zero Cloud Accounts</div>
        <div class='pill'>✓ Free .md Export</div>
        <div class='pill'>✓ 1-Click Obsidian Bridge</div>
      </div>
    </div>
    <div class='card'>
      <div class='card-hdr'>
        <span class='card-title'>LinkLater Queue</span>
        <span class='card-tag'>3 Unread · Local</span>
      </div>
      <div class='item'>
        <div class='item-t'>Local-First Software Architecture</div>
        <div class='item-n'>"Quote section 3 on CRDT storage in vault note"</div>
        <div class='chips'><span class='chip'>#architecture</span><span class='chip'>#local-first</span></div>
        <div class='btns'>
          <div class='btn btn-md'>Export .md</div>
          <div class='btn btn-ob'>Send to Obsidian ↗</div>
        </div>
      </div>
      <div class='item' style='margin-bottom:0;'>
        <div class='item-t'>Manifest V3 Side Panel Patterns</div>
        <div class='item-n'>"Compare narrow activeTab permissions"</div>
        <div class='chips'><span class='chip'>#mv3</span><span class='chip'>#security</span></div>
        <div class='btns'>
          <div class='btn btn-md'>Export .md</div>
          <div class='btn btn-ob'>Send to Obsidian ↗</div>
        </div>
      </div>
    </div>
  </body></html>`);
  const targets = [
    'C:/dev/864zeros-llc/LLC-DIV-3-FACTORY/extensions/link-later/store/assets/link-later-og-1200x630.png',
    'C:/dev/864zeros-llc/LLC-DIV-3-FACTORY/extensions-edge/link-later/store/assets/link-later-og-1200x630.png',
    'C:/dev/864zeros-publish/media/products/link-later/store/link-later-og-1200x630.png',
    'C:/dev/864zeros-web/products/assets/link-later-og-1200x630.png'
  ];
  for (const t of targets) {
    await page.screenshot({ path: t });
  }
  await browser.close();
  console.log('OG_RENDERED_OK');
})();
