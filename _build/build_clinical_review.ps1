# Builds the clinical-review handoff packet from passages_core.json:
#   - clinical_review.html : self-contained reviewer app (original <-> reader <-> surface,
#                            provenance, Approve/Revise/Reject + notes, local persistence, export)
#   - clinical_review.csv  : same data for spreadsheet review (blank decision columns)
# Pulls the ORIGINAL 1939 text for each passage via its source provenance.

$root = Split-Path $PSScriptRoot -Parent
$contentDir = Join-Path $root "apps\clearstreak"
$passages = Get-Content (Join-Path $contentDir "passages_core.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$book     = Get-Content (Join-Path $contentDir "big_book.json")      -Raw -Encoding UTF8 | ConvertFrom-Json

# chapter_id -> paragraphs[] (for original-text lookup)
$chapParas = @{}
foreach($c in $book.chapters){ $chapParas[$c.id] = $c.paragraphs }

$records = New-Object System.Collections.Generic.List[object]
$csvRows = New-Object System.Collections.Generic.List[object]
foreach($p in $passages.passages){
  $cid = $p.source.chapter_id
  $pi  = [int]$p.source.paragraph_index
  $orig = ""
  if($chapParas.ContainsKey($cid) -and $pi -lt $chapParas[$cid].Count){ $orig = $chapParas[$cid][$pi] }

  $records.Add([ordered]@{
    id            = $p.id
    chapter_id    = $cid
    chapter_title = $p.source.chapter_title
    page          = $p.source.page
    paragraph_index = $pi
    moment        = @($p.labels.moment)
    halt          = $p.labels.halt
    urge_level    = $p.labels.urge_level
    stage         = $p.labels.stage
    function      = $p.labels.function
    applies_to    = @($p.applies_to)
    reading_time  = $p.reading_time
    framework_map = $p.framework_map
    faith_optional= $p.faith_optional
    original      = $orig
    reader_text   = $p.reader_text
    surface_text  = $p.surface_text
  })

  $csvRows.Add([pscustomobject]@{
    id=$p.id; chapter_id=$cid; chapter_title=$p.source.chapter_title; page=$p.source.page; paragraph_index=$pi
    moment=(@($p.labels.moment) -join '|'); halt=$p.labels.halt; urge_level=$p.labels.urge_level
    stage=$p.labels.stage; function=$p.labels.function; applies_to=(@($p.applies_to) -join '|'); reading_time=$p.reading_time
    framework_map=$p.framework_map; faith_optional=$p.faith_optional
    original_1939=$orig; reader_text=$p.reader_text; surface_text=$p.surface_text
    review_status=''; reviewer_notes=''
  })
}

# --- CSV ---
$csvRows | Export-Csv -Path (Join-Path $contentDir "clinical_review.csv") -NoTypeInformation -Encoding UTF8

# --- HTML ---
$json = ($records | ConvertTo-Json -Depth 6)
if($records.Count -eq 1){ $json = "[$json]" }   # ConvertTo-Json unwraps single element
$json = $json.Replace('</','<\/')               # safe to embed in <script>
$date = "2026-08-19 14:58"
$count = $records.Count

$tpl = @'
<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ClearStreak — Clinical Review Packet</title>
<style>
  :root { --blue:#0058ff; --ink:#0f172a; --mut:#64748b; --bg:#f6f8fc; --line:#e2e8f0;
          --green:#16a34a; --amber:#d97706; --red:#dc2626; }
  * { box-sizing:border-box; }
  body { margin:0; font:15px/1.55 -apple-system,"Segoe UI",Roboto,sans-serif; color:var(--ink); background:var(--bg); }
  .topbar { background:#fff; padding:12px 22px; border-bottom:1px solid var(--line); display:flex; justify-content:space-between; align-items:center; }
  .wordmark { font-weight:800; font-size:18px; text-decoration:none; } .wordmark .n{color:var(--blue);} .wordmark .z{color:var(--ink);}
  .hero-band { background:linear-gradient(160deg,#0b1220 0%,#0f172a 100%); color:#fff; padding:30px 24px; }
  .hero-band .inner { max-width:1100px; margin:0 auto; }
  .hero-band h1 { color:#fff; font-size:26px; margin:10px 0 6px; }
  .hero-band .sub { color:#cbd5e1; font-size:15px; margin:0 0 10px; }
  .hpill { display:inline-block; font-size:12px; font-weight:700; color:#5b9dff; background:#1e293b; border:1px solid #334155; border-radius:999px; padding:3px 11px; letter-spacing:.04em; }
  .disc { font-size:12.5px; color:#fca5a5; background:#3f1d1d; border:1px solid #7f1d1d; border-radius:8px; padding:8px 12px; margin-top:10px; }
  .wrap { max-width:1100px; margin:0 auto; padding:18px 20px 70px; }
  .controls { position:sticky; top:0; z-index:10; background:var(--bg); padding:12px 0; border-bottom:1px solid var(--line);
              display:flex; gap:8px; flex-wrap:wrap; align-items:center; }
  .controls select, .controls input[type=search] { font:13px inherit; padding:7px 10px; border:1px solid var(--line); border-radius:8px; background:#fff; color:var(--ink); }
  .controls input[type=search]{ min-width:200px; flex:1; }
  .btn { font:13px inherit; font-weight:700; padding:7px 13px; border-radius:8px; border:1px solid var(--line); background:#fff; color:var(--ink); cursor:pointer; }
  .btn.primary { background:var(--blue); color:#fff; border-color:var(--blue); }
  .btn.ghost { color:var(--mut); }
  .prog { font-size:13px; color:var(--mut); margin:12px 0 6px; }
  .prog b { color:var(--ink); }
  .bar { height:8px; background:#e2e8f0; border-radius:999px; overflow:hidden; margin-bottom:18px; }
  .bar > i { display:block; height:100%; background:var(--green); width:0%; transition:width .2s; }
  .pcard { background:#fff; border:1px solid var(--line); border-left:5px solid #cbd5e1; border-radius:12px; padding:14px 16px; margin-bottom:14px; }
  .pcard.approved { border-left-color:var(--green); }
  .pcard.revise   { border-left-color:var(--amber); }
  .pcard.rejected { border-left-color:var(--red); }
  .phead { display:flex; justify-content:space-between; align-items:baseline; gap:10px; flex-wrap:wrap; margin-bottom:4px; }
  .pid { font-family:ui-monospace,Menlo,monospace; font-size:12px; color:var(--mut); }
  .psrc { font-size:12.5px; color:var(--ink); font-weight:600; }
  .psrc .pg { color:var(--mut); font-weight:400; }
  .chips { display:flex; gap:4px; flex-wrap:wrap; margin:6px 0 10px; }
  .chip { font-size:10.5px; font-weight:700; padding:2px 7px; border-radius:6px; background:#eef2ff; color:#3730a3; }
  .chip.halt{ background:#fef3c7; color:#92400e; } .chip.urge{ background:#e0e7ff; color:#3730a3; }
  .chip.uni{ background:#dcfce7; color:#166534; } .chip.faith{ background:#f3e8ff; color:#6b21a8; }
  .fmap { font-size:12px; color:#475569; background:#f8fafc; border:1px dashed var(--line); border-radius:8px; padding:6px 10px; margin-bottom:10px; }
  .cols { display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; }
  @media(max-width:820px){ .cols{ grid-template-columns:1fr; } }
  .col { border:1px solid var(--line); border-radius:8px; padding:8px 10px; font-size:13.5px; }
  .col .lab { font-size:10.5px; font-weight:800; letter-spacing:.05em; text-transform:uppercase; margin-bottom:5px; }
  .col.orig   { background:#fbfbfd; } .col.orig .lab{ color:var(--mut); }
  .col.reader { background:#f0f7ff; } .col.reader .lab{ color:#1e40af; }
  .col.surface{ background:#f0fdf4; } .col.surface .lab{ color:#166534; }
  .faithbox { margin-top:10px; background:#faf5ff; border:1px solid #e9d5ff; border-radius:8px; padding:8px 10px; font-size:13px; color:#6b21a8; }
  .faithbox .lab { font-size:10.5px; font-weight:800; text-transform:uppercase; letter-spacing:.05em; color:#7e22ce; margin-bottom:4px; }
  .rev { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-top:12px; padding-top:10px; border-top:1px solid var(--line); }
  .rev .rb { font:13px inherit; font-weight:700; padding:6px 14px; border-radius:999px; border:1px solid var(--line); background:#fff; cursor:pointer; color:var(--mut); }
  .rev .rb.approved.on { background:var(--green); border-color:var(--green); color:#fff; }
  .rev .rb.revise.on   { background:var(--amber); border-color:var(--amber); color:#fff; }
  .rev .rb.rejected.on { background:var(--red); border-color:var(--red); color:#fff; }
  .rev textarea { flex:1; min-width:220px; font:13px inherit; padding:6px 9px; border:1px solid var(--line); border-radius:8px; resize:vertical; min-height:34px; }
  .empty { text-align:center; color:var(--mut); padding:40px; }
  .foot { margin-top:30px; color:var(--mut); font-size:12px; border-top:1px solid var(--line); padding-top:14px; }
</style>
</head>
<body>
<div class="topbar">
  <a class="wordmark" href="#"><span class="n">864</span><span class="z">zeros</span></a>
  <div><button class="btn ghost" id="clearBtn">Clear my decisions</button>
       <button class="btn" id="jsonBtn">Export JSON</button>
       <button class="btn primary" id="csvBtn">Export decisions (CSV)</button></div>
</div>
<div class="hero-band"><div class="inner">
  <span class="hpill">CLINICAL REVIEW PACKET · CLEARSTREAK</span>
  <h1>Recovery Literature — Passage Sign-off</h1>
  <p class="sub">__COUNT__ passages modernized from the public-domain 1939 Big Book. Review each: original 1939 text &rarr; reader (light-touch) &rarr; surface (moment-of-need). Approve, request revision, or reject, with notes.</p>
  <div class="disc"><b>Reviewer note:</b> This content is <b>not clinical advice</b> and has not yet been approved. Your review is the gate. Decisions save to <b>this browser only</b> (no network, no server) — use <b>Export decisions</b> to send them back. Flag anything that could mislead or harm a person in crisis.</div>
</div></div>
<div class="wrap">
  <div class="controls">
    <select id="fChapter"><option value="">All chapters</option></select>
    <select id="fStatus">
      <option value="">All statuses</option>
      <option value="undecided">Undecided</option>
      <option value="approved">Approved</option>
      <option value="revise">Needs revision</option>
      <option value="rejected">Rejected</option>
    </select>
    <select id="fFaith"><option value="">All</option><option value="faith">Has faith layer</option></select>
    <input type="search" id="fSearch" placeholder="Search text or id…">
  </div>
  <div class="prog" id="prog"></div>
  <div class="bar"><i id="barFill"></i></div>
  <div id="list"></div>
  <p class="foot">864zeros LLC · ClearStreak clinical-review packet · generated __DATE__ · self-contained &amp; offline · code wins.</p>
</div>

<script id="data" type="application/json">__DATA__</script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);
const LS = 'cs_clinical_review_v1';
let decisions = {};
try { decisions = JSON.parse(localStorage.getItem(LS) || '{}'); } catch(e){ decisions = {}; }
function save(){ localStorage.setItem(LS, JSON.stringify(decisions)); }
function esc(s){ return (s==null?'':String(s)).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

// populate chapter filter
const chSel = document.getElementById('fChapter');
[...new Set(DATA.map(d=>d.chapter_title))].forEach(t=>{ const o=document.createElement('option'); o.value=t; o.textContent=t; chSel.appendChild(o); });

const listEl = document.getElementById('list');
function statusOf(id){ return (decisions[id]&&decisions[id].status)||''; }

function render(){
  const fc=document.getElementById('fChapter').value;
  const fs=document.getElementById('fStatus').value;
  const ff=document.getElementById('fFaith').value;
  const q=document.getElementById('fSearch').value.toLowerCase().trim();
  listEl.innerHTML='';
  let shown=0;
  DATA.forEach(d=>{
    const st=statusOf(d.id)||'undecided';
    if(fc && d.chapter_title!==fc) return;
    if(fs && st!==fs) return;
    if(ff==='faith' && !d.faith_optional) return;
    if(q && !((d.original+' '+d.reader_text+' '+d.surface_text+' '+d.id).toLowerCase().includes(q))) return;
    shown++;
    const cls = st==='undecided' ? '' : st;
    const chips = []
      .concat(d.moment.map(m=>'<span class="chip">'+esc(m)+'</span>'))
      .concat(['<span class="chip halt">HALT: '+esc(d.halt)+'</span>',
               '<span class="chip urge">'+esc(d.urge_level)+'</span>',
               '<span class="chip">'+esc(d.stage)+'</span>',
               '<span class="chip">'+esc(d.function)+'</span>'])
      .concat((d.applies_to||[]).map(a=>'<span class="chip uni">'+esc(a)+'</span>'))
      .concat(d.faith_optional?['<span class="chip faith">faith layer</span>']:[])
      .join('');
    const faith = d.faith_optional ? '<div class="faithbox"><div class="lab">Faith layer (opt-in only)</div>'+esc(d.faith_optional)+'</div>' : '';
    const notes = (decisions[d.id]&&decisions[d.id].notes)||'';
    const card=document.createElement('div');
    card.className='pcard '+cls; card.id='card_'+d.id;
    card.innerHTML =
      '<div class="phead"><span class="psrc">'+esc(d.chapter_title)+' <span class="pg">· p.'+esc(d.page)+' ¶'+esc(d.paragraph_index)+' · '+esc(d.reading_time)+'</span></span><span class="pid">'+esc(d.id)+'</span></div>'
      + '<div class="chips">'+chips+'</div>'
      + (d.framework_map && d.framework_map!=='none' ? '<div class="fmap"><b>Re-map:</b> '+esc(d.framework_map)+'</div>' : '')
      + '<div class="cols">'
        + '<div class="col orig"><div class="lab">Original · 1939</div>'+esc(d.original)+'</div>'
        + '<div class="col reader"><div class="lab">Reader (light touch)</div>'+esc(d.reader_text)+'</div>'
        + '<div class="col surface"><div class="lab">Surface (moment-of-need)</div>'+esc(d.surface_text)+'</div>'
      + '</div>'
      + faith
      + '<div class="rev">'
        + '<button class="rb approved'+(st==='approved'?' on':'')+'" data-a="approved" data-id="'+d.id+'">✓ Approve</button>'
        + '<button class="rb revise'+(st==='revise'?' on':'')+'" data-a="revise" data-id="'+d.id+'">✎ Revise</button>'
        + '<button class="rb rejected'+(st==='rejected'?' on':'')+'" data-a="rejected" data-id="'+d.id+'">✕ Reject</button>'
        + '<textarea placeholder="Reviewer notes (why revise/reject, safety concerns)…" data-note="'+d.id+'">'+esc(notes)+'</textarea>'
      + '</div>';
    listEl.appendChild(card);
  });
  if(shown===0) listEl.innerHTML='<div class="empty">No passages match these filters.</div>';
  updateProgress();
}
function updateProgress(){
  const total=DATA.length;
  let a=0,r=0,x=0;
  DATA.forEach(d=>{ const s=statusOf(d.id); if(s==='approved')a++; else if(s==='revise')r++; else if(s==='rejected')x++; });
  const done=a+r+x;
  document.getElementById('prog').innerHTML='<b>'+done+'</b> / '+total+' reviewed &nbsp;·&nbsp; <b style="color:var(--green)">'+a+'</b> approved &nbsp;·&nbsp; <b style="color:var(--amber)">'+r+'</b> revise &nbsp;·&nbsp; <b style="color:var(--red)">'+x+'</b> rejected';
  document.getElementById('barFill').style.width=(total? (done/total*100):0)+'%';
}

listEl.addEventListener('click', e=>{
  const b=e.target.closest('.rb'); if(!b) return;
  const id=b.dataset.id, a=b.dataset.a;
  if(!decisions[id]) decisions[id]={};
  decisions[id].status = decisions[id].status===a ? '' : a;  // toggle off if same
  save();
  const card=document.getElementById('card_'+id);
  card.className='pcard '+(decisions[id].status||'');
  card.querySelectorAll('.rb').forEach(x=>x.classList.toggle('on', x.dataset.a===decisions[id].status));
  updateProgress();
});
listEl.addEventListener('input', e=>{
  const t=e.target.closest('textarea[data-note]'); if(!t) return;
  const id=t.dataset.note; if(!decisions[id]) decisions[id]={};
  decisions[id].notes=t.value; save();
});
['fChapter','fStatus','fFaith','fSearch'].forEach(idf=>document.getElementById(idf).addEventListener('input',render));

function download(name, text, mime){
  const blob=new Blob([text],{type:mime}); const url=URL.createObjectURL(blob);
  const a=document.createElement('a'); a.href=url; a.download=name; a.click(); URL.revokeObjectURL(url);
}
function csvCell(s){ s=(s==null?'':String(s)); return '"'+s.replace(/"/g,'""')+'"'; }
document.getElementById('csvBtn').addEventListener('click',()=>{
  const head=['id','chapter_title','page','paragraph_index','review_status','reviewer_notes','moment','halt','urge_level','stage','function','applies_to','reading_time','framework_map','faith_optional','original_1939','reader_text','surface_text'];
  const rows=[head.map(csvCell).join(',')];
  DATA.forEach(d=>{ const dec=decisions[d.id]||{};
    rows.push([d.id,d.chapter_title,d.page,d.paragraph_index,dec.status||'',dec.notes||'',(d.moment||[]).join('|'),d.halt,d.urge_level,d.stage,d.function,(d.applies_to||[]).join('|'),d.reading_time,d.framework_map,d.faith_optional,d.original,d.reader_text,d.surface_text].map(csvCell).join(','));
  });
  download('clearstreak_review_decisions.csv', '﻿'+rows.join('\r\n'), 'text/csv');
});
document.getElementById('jsonBtn').addEventListener('click',()=>{
  download('clearstreak_review_decisions.json', JSON.stringify(decisions,null,2), 'application/json');
});
document.getElementById('clearBtn').addEventListener('click',()=>{
  if(confirm('Clear ALL your review decisions in this browser? Export first if you want to keep them.')){ decisions={}; save(); render(); }
});
render();
</script>
</body></html>
'@

$html = $tpl.Replace('__DATA__', $json).Replace('__COUNT__', "$count").Replace('__DATE__', $date)
$utf8 = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText((Join-Path $contentDir "clinical_review.html"), $html, $utf8)

Write-Output "Passages: $count"
Write-Output ("CSV : " + (Join-Path $contentDir 'clinical_review.csv') + "  ($([Math]::Round((Get-Item (Join-Path $contentDir 'clinical_review.csv')).Length/1KB,1)) KB)")
Write-Output ("HTML: " + (Join-Path $contentDir 'clinical_review.html') + "  ($([Math]::Round((Get-Item (Join-Path $contentDir 'clinical_review.html')).Length/1KB,1)) KB)")
$withOrig = ($records | Where-Object { $_.original -ne '' }).Count
Write-Output "Passages with original text resolved: $withOrig / $count"
