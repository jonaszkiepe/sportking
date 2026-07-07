#!/usr/bin/env python3
"""Build the manual-triage dashboard: one self-contained HTML that shows every
scanned product, the images we currently hold for it, and moves each manual-wave
product through a 3-stage photo-prep pipeline.

Reads:
  products/list-filled.xlsx   — the enriched product list (enrich.py output)
  products/berg-master.csv    — ean -> article map, to find BERG reference photos
  products/photos-{allegro,web,berg}/  — scanned image dirs

Writes:
  report/dashboard.html       — open via a local server rooted at the repo root:
                                  python3 -m http.server   # then /report/dashboard.html

Two tabs: "Pipeline" = manual wave (override / berg-feed / dark) that needs our own
photos; "Auto / catalog-safe" = source=allegro that Allegro fills itself.

The pipeline moves each manual product through three stages:
  1. Unverified   — images unchecked / unsafe for Allegro (starting bucket)
  2. Verified <3  — you've confirmed the folder images are safe, but there are
                    fewer than READY_MIN of them
  3. Ready        — verified AND >= READY_MIN images on disk

You toggle one flag per product ("images verified"); the stage is DERIVED from that
flag plus the live image count. Drop real photos into products/photos-web/<EAN>/,
rerun this script to refresh counts, and products climb from stage 2 to 3 on their
own. The verified flag persists in the browser (localStorage) + CSV export/import.
Pure stdlib. Run: ./scripts/reporting/build_dashboard.py
"""
import csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
from lib_xlsx import read_sheets

LIST = ROOT / "products" / "list-filled.xlsx"
BERG_MASTER = ROOT / "products" / "berg-master.csv"
PHOTOS = {
    "allegro": ROOT / "products" / "photos-allegro",
    "web": ROOT / "products" / "photos-web",
    "berg": ROOT / "products" / "photos-berg",
}
OUT = ROOT / "report" / "dashboard.html"

# Manual wave = we must supply our own photos; catalog-safe = Allegro fills it.
TODO_SOURCES = {"override", "berg-feed", ""}  # "" == dark (unidentified)
READY_MIN = 3  # a verified product needs >= this many images to reach "Ready to push"


def rows_as_dicts(path):
    """read_sheets returns row-dicts keyed by column letter; remap to header names."""
    rows = read_sheets(path)["Filled"]
    hdr = rows[0]  # {'A': 'ean', 'B': 'qty', ...}
    return [{hdr[k]: r.get(k, "") for k in hdr} for r in rows[1:]]


def ean_to_article():
    if not BERG_MASTER.exists():
        return {}
    with open(BERG_MASTER, newline="", encoding="utf-8") as f:
        return {r["ean"]: r["article"] for r in csv.DictReader(f) if r.get("ean")}


def dir_images(d):
    """Web-relative paths (../products/...) for the image files in a dir, sorted."""
    if not d.exists():
        return []
    files = sorted(p for p in d.iterdir() if p.is_file() and p.stat().st_size > 0)
    return ["../" + p.relative_to(ROOT).as_posix() for p in files]


def collect_images(ean, article):
    """Every reference image we hold for this product, tagged by source kind."""
    imgs = []
    for kind in ("allegro", "web"):
        for src in dir_images(PHOTOS[kind] / ean):
            imgs.append({"kind": kind, "src": src})
    if article:  # BERG brand/dealer assets are keyed by article, not EAN
        for src in dir_images(PHOTOS["berg"] / article):
            imgs.append({"kind": "berg", "src": src})
    return imgs


def build():
    e2a = ean_to_article()
    products = []
    for r in rows_as_dicts(LIST):
        ean = str(r.get("ean", "")).strip()
        if not ean:
            continue
        source = (r.get("source") or "").strip()
        article = e2a.get(ean, "")
        imgs = collect_images(ean, article)
        products.append({
            "ean": ean,
            "qty": r.get("qty", ""),
            "name": r.get("name", "") or "(no name)",
            "category": r.get("category", ""),
            "source": source or "dark",
            "article": article,
            "note": r.get("note", ""),
            # catalog-safe images are Allegro's own gallery = compliant to reuse;
            # everything in the manual wave still needs our own white packshot.
            "wave": "todo" if source in TODO_SOURCES else "done",
            "images": imgs,
            "n_images": len(imgs),
        })
    # Fewest images first within each wave (most work up top), then by qty.
    products.sort(key=lambda p: (p["wave"] != "todo", p["n_images"], -int(p["qty"] or 0)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(products), encoding="utf-8")
    todo = [p for p in products if p["wave"] == "todo"]
    done = [p for p in products if p["wave"] == "done"]
    short = sum(1 for p in todo if p["n_images"] < READY_MIN)
    print(f"{OUT.relative_to(ROOT)}: {len(products)} products "
          f"({len(todo)} in pipeline, {len(done)} auto) | "
          f"{short}/{len(todo)} manual products under {READY_MIN} images")
    print("Serve from the repo root:  python3 -m http.server   "
          "→  http://localhost:8000/report/dashboard.html")


def render(products):
    data = json.dumps(products, ensure_ascii=False)
    return HTML.replace("__DATA__", data).replace("__READY_MIN__", str(READY_MIN))


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>sportking — Allegro photo pipeline</title>
<style>
  :root{
    --bg:#0f1115; --card:#181b22; --card2:#1f232c; --line:#2b303b;
    --fg:#e6e8ec; --dim:#8b93a1; --accent:#6ea8fe;
    --web:#f0a35e; --berg:#c58af9; --allegro:#5dd39e; --dark:#e06c75;
    --s1:#e06c75; --s2:#e5c07b; --s3:#5dd39e;
  }
  @media (prefers-color-scheme:light){
    :root{--bg:#f5f6f8;--card:#fff;--card2:#eef1f5;--line:#dfe3ea;
          --fg:#1a1d23;--dim:#5a6472;}
  }
  *{box-sizing:border-box}
  body{margin:0;font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
       background:var(--bg);color:var(--fg)}
  header{position:sticky;top:0;z-index:5;background:var(--bg);
         border-bottom:1px solid var(--line);padding:12px 18px}
  h1{margin:0 0 8px;font-size:16px;font-weight:650}
  h1 small{color:var(--dim);font-weight:400;margin-left:8px}
  .tabs{display:flex;gap:6px;margin-bottom:8px}
  .tab{padding:6px 14px;border:1px solid var(--line);border-radius:7px;
       background:var(--card);cursor:pointer;color:var(--fg);font-size:13px}
  .tab.on{background:var(--accent);border-color:var(--accent);color:#08111f;font-weight:600}
  .bar{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
  .bar input{background:var(--card);border:1px solid var(--line);color:var(--fg);
             padding:6px 10px;border-radius:7px;min-width:220px}
  .spacer{flex:1}
  button.act{background:var(--card);border:1px solid var(--line);color:var(--fg);
             padding:6px 11px;border-radius:7px;cursor:pointer;font-size:12px}
  main{padding:16px 18px}
  /* pipeline columns */
  .cols{display:grid;gap:14px;grid-template-columns:repeat(3,1fr)}
  @media(max-width:940px){.cols{grid-template-columns:1fr}}
  .col{background:var(--card2);border:1px solid var(--line);border-radius:12px;padding:10px}
  .col>h2{margin:2px 4px 10px;font-size:13px;font-weight:650;display:flex;
          justify-content:space-between;align-items:center;gap:8px}
  .col.c1>h2{color:var(--s1)} .col.c2>h2{color:var(--s2)} .col.c3>h2{color:var(--s3)}
  .col>h2 .n{color:var(--dim);font-weight:500;font-size:12px}
  .stack{display:flex;flex-direction:column;gap:10px}
  /* auto grid */
  .grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}
  .card{background:var(--card);border:1px solid var(--line);border-radius:10px;
        overflow:hidden;display:flex;flex-direction:column}
  .card.c1{border-left:4px solid var(--s1)}
  .card.c2{border-left:4px solid var(--s2)}
  .card.c3{border-left:4px solid var(--s3)}
  .imgs{display:flex;gap:2px;background:var(--card2);overflow-x:auto;scrollbar-width:thin}
  .imgs img{height:120px;width:auto;object-fit:contain;background:#fff;cursor:zoom-in}
  .noimg{display:flex;align-items:center;justify-content:center;min-height:70px;
         width:100%;color:var(--dim);font-size:12px;font-style:italic}
  .imgtag{position:relative;flex:0 0 auto}
  .imgtag span{position:absolute;left:4px;top:4px;font-size:10px;padding:1px 5px;
        border-radius:4px;background:rgba(0,0,0,.6);color:#fff;text-transform:uppercase;
        letter-spacing:.03em}
  .body{padding:9px 11px;display:flex;flex-direction:column;gap:6px}
  .name{font-weight:600;font-size:13px;line-height:1.3}
  .meta{color:var(--dim);font-size:11.5px;display:flex;flex-wrap:wrap;gap:7px;align-items:center}
  .src{font-size:10.5px;padding:1px 6px;border-radius:5px;font-weight:600}
  .src-web{background:var(--web);color:#241505}.src-berg{background:var(--berg);color:#1a0733}
  .src-allegro{background:var(--allegro);color:#053021}.src-dark{background:var(--dark);color:#2a0508}
  .cnt{font-weight:600}
  .cnt.ok{color:var(--s3)} .cnt.low{color:var(--s2)}
  .note{color:var(--dim);font-size:11px;font-style:italic}
  .act-row{display:flex;gap:6px;align-items:center;margin-top:2px}
  .move{flex:1;padding:6px;border:1px solid var(--line);border-radius:6px;cursor:pointer;
        font-size:12px;font-weight:600;text-align:center;background:var(--card2);color:var(--fg)}
  .move.verify{background:var(--s3);color:#053021;border-color:var(--s3)}
  .move.undo{flex:0 0 auto;background:var(--card2);color:var(--dim);font-weight:500}
  .hint{font-size:11px;color:var(--s2)}
  .lightbox{position:fixed;inset:0;background:rgba(0,0,0,.9);display:none;
            align-items:center;justify-content:center;z-index:50;cursor:zoom-out}
  .lightbox.on{display:flex}
  .lightbox img{max-width:94vw;max-height:94vh;background:#fff}
  .empty{color:var(--dim);padding:24px;text-align:center;font-size:12px}
</style>
</head>
<body>
<header>
  <h1>sportking — Allegro photo pipeline <small id="sub"></small></h1>
  <div class="tabs">
    <div class="tab on" data-wave="todo" onclick="setTab(this)">Pipeline (manual)</div>
    <div class="tab" data-wave="done" onclick="setTab(this)">Auto / catalog-safe</div>
  </div>
  <div class="bar">
    <input id="q" placeholder="search name / EAN / category…" oninput="draw()">
    <span class="spacer"></span>
    <button class="act" onclick="exportCsv()">export CSV</button>
    <label class="act" style="cursor:pointer">import<input type="file" accept=".csv"
      style="display:none" onchange="importCsv(this)"></label>
  </div>
</header>
<main id="main"></main>
<div class="lightbox" id="lb" onclick="this.classList.remove('on')"><img id="lbi"></div>
<script>
const DATA = __DATA__;
const READY_MIN = __READY_MIN__;
const KEY = "sportking-verified";
let verified = JSON.parse(localStorage.getItem(KEY) || "{}");  // { ean: true }
let tab = "todo";
const STAGES = [
  {n:1, cls:"c1", title:"① Unverified — unsafe for Allegro"},
  {n:2, cls:"c2", title:"② Verified · needs images (<"+READY_MIN+")"},
  {n:3, cls:"c3", title:"③ Ready to push"},
];

function save(){ localStorage.setItem(KEY, JSON.stringify(verified)); }
function stageOf(p){ if(!verified[p.ean]) return 1; return p.n_images>=READY_MIN?3:2; }
function setVerified(ean,v){ if(v) verified[ean]=true; else delete verified[ean]; save(); draw(); }
function setTab(el){
  document.querySelectorAll(".tab").forEach(t=>t.classList.remove("on"));
  el.classList.add("on"); tab=el.dataset.wave; draw();
}
function matches(p){
  const q=document.getElementById("q").value.trim().toLowerCase();
  if(!q) return true;
  return p.name.toLowerCase().includes(q)||p.ean.includes(q)
       ||(p.category||"").toLowerCase().includes(q);
}

function draw(){
  const todo=DATA.filter(p=>p.wave==="todo");
  const ready=todo.filter(p=>stageOf(p)===3).length;
  document.getElementById("sub").textContent =
    `· ${todo.length} manual · ${ready} ready to push`;
  const main=document.getElementById("main");
  if(tab==="done"){
    const list=DATA.filter(p=>p.wave==="done"&&matches(p));
    main.innerHTML=`<div class="grid">${list.map(card).join("")||"<div class='empty'>none</div>"}</div>`;
    return;
  }
  main.innerHTML=`<div class="cols">${STAGES.map(s=>{
    const list=todo.filter(p=>stageOf(p)===s.n&&matches(p));
    return `<div class="col ${s.cls}"><h2><span>${s.title}</span><span class="n">${list.length}</span></h2>
      <div class="stack">${list.map(card).join("")||"<div class='empty'>—</div>"}</div></div>`;
  }).join("")}</div>`;
}

function card(p){
  const st=stageOf(p);
  const imgs=p.images.length
    ? `<div class="imgs">${p.images.map(i=>
        `<div class="imgtag"><span>${i.kind}</span>`+
        `<img loading="lazy" src="${i.src}" onclick="zoom('${i.src}')"></div>`).join("")}</div>`
    : `<div class="imgs"><div class="noimg">no image on file</div></div>`;
  const cntCls=p.n_images>=READY_MIN?"ok":"low";
  let actions="";
  if(p.wave==="todo"){
    if(st===1){
      actions=`<div class="act-row"><div class="move verify"
        onclick="setVerified('${p.ean}',true)">✓ mark images verified</div></div>`;
    } else if(st===2){
      const need=READY_MIN-p.n_images;
      actions=`<div class="hint">✓ verified — add ${need} more image${need>1?"s":""} to reach Ready</div>
        <div class="act-row"><div class="move undo"
        onclick="setVerified('${p.ean}',false)">↩ unverify</div></div>`;
    } else {
      actions=`<div class="hint" style="color:var(--s3)">✓ ready to push (${p.n_images} images)</div>
        <div class="act-row"><div class="move undo"
        onclick="setVerified('${p.ean}',false)">↩ unverify</div></div>`;
    }
  }
  const note=p.note?`<div class="note">${esc(p.note)}</div>`:"";
  return `<div class="card ${p.wave==="todo"?"c"+st:""}">
    ${imgs}
    <div class="body">
      <div class="name">${esc(p.name)}</div>
      <div class="meta">
        <span class="src src-${p.source.replace('-feed','')}">${p.source}</span>
        <span>EAN ${p.ean}</span><span>qty ${p.qty}</span>
        <span class="cnt ${cntCls}">${p.n_images} img</span>
        ${p.article?`<span>art ${p.article}</span>`:""}
      </div>
      ${p.category?`<div class="meta">${esc(p.category)}</div>`:""}
      ${note}${actions}
    </div></div>`;
}
function zoom(src){ document.getElementById("lbi").src=src;
  document.getElementById("lb").classList.add("on"); }
function esc(s){ return String(s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c])); }

function exportCsv(){
  const rows=[["ean","name","n_images","verified","stage"]];
  DATA.filter(p=>p.wave==="todo").forEach(p=>
    rows.push([p.ean,'"'+p.name.replace(/"/g,'""')+'"',p.n_images,
               verified[p.ean]?"yes":"no",stageOf(p)]));
  const blob=new Blob([rows.map(r=>r.join(",")).join("\n")],{type:"text/csv"});
  const a=document.createElement("a");a.href=URL.createObjectURL(blob);
  a.download="photo-pipeline.csv";a.click();
}
function importCsv(inp){
  const f=inp.files[0]; if(!f) return;
  const r=new FileReader();
  r.onload=()=>{
    r.result.split(/\r?\n/).slice(1).forEach(line=>{
      const cells=line.split(","); const ean=(cells[0]||"").trim();
      if(!/^\d+$/.test(ean)) return;
      const v=(cells[3]||"").trim().toLowerCase();
      if(v==="yes") verified[ean]=true; else delete verified[ean];
    }); save(); draw();
  };
  r.readAsText(f);
}
draw();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    build()
