#!/usr/bin/env python3
"""Build the manual-triage dashboard: one self-contained HTML that shows every
scanned product, the images we currently hold for it, and lets you track manual
photo-work status as you go.

Reads:
  products/list-filled.xlsx   — the enriched product list (enrich.py output)
  products/berg-master.csv    — ean -> article map, to find BERG reference photos
  products/photos-{allegro,web,berg}/  — scanned image dirs

Writes:
  report/dashboard.html       — open via a local server rooted at the repo root:
                                  python3 -m http.server   # then /report/dashboard.html

Two tabs: "To do" = manual wave (override / berg-feed / dark) that needs our own
photos; "Auto / done" = catalog-safe (source=allegro) that Allegro fills itself.
Status (needs-photo / in-progress / ready) persists in the browser (localStorage)
and can be exported/imported as CSV. Pure stdlib. Run: ./scripts/reporting/build_dashboard.py
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
    # To-do first, and within each: no-image products up top (most work), then by qty.
    products.sort(key=lambda p: (p["wave"] != "todo", p["n_images"] > 0,
                                 -int(p["qty"] or 0)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(products), encoding="utf-8")
    todo = [p for p in products if p["wave"] == "todo"]
    done = [p for p in products if p["wave"] == "done"]
    print(f"{OUT.relative_to(ROOT)}: {len(products)} products "
          f"({len(todo)} to-do, {len(done)} auto) | "
          f"{sum(1 for p in todo if not p['n_images'])} to-do with NO image")
    print("Serve from the repo root:  python3 -m http.server   "
          "→  http://localhost:8000/report/dashboard.html")


def render(products):
    data = json.dumps(products, ensure_ascii=False)
    return HTML.replace("__DATA__", data)


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>sportking — product image map</title>
<style>
  :root{
    --bg:#0f1115; --card:#181b22; --card2:#1f232c; --line:#2b303b;
    --fg:#e6e8ec; --dim:#8b93a1; --accent:#6ea8fe;
    --web:#f0a35e; --berg:#c58af9; --allegro:#5dd39e; --dark:#e06c75;
    --todo-needs:#e06c75; --todo-prog:#e5c07b; --todo-ready:#5dd39e;
  }
  @media (prefers-color-scheme:light){
    :root{--bg:#f5f6f8;--card:#fff;--card2:#f0f2f5;--line:#dfe3ea;
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
             padding:6px 10px;border-radius:7px;min-width:200px}
  .chip{padding:5px 11px;border:1px solid var(--line);border-radius:20px;
        background:var(--card);cursor:pointer;font-size:12px;color:var(--dim)}
  .chip.on{color:var(--fg);border-color:var(--accent)}
  .spacer{flex:1}
  button.act{background:var(--card);border:1px solid var(--line);color:var(--fg);
             padding:6px 11px;border-radius:7px;cursor:pointer;font-size:12px}
  main{padding:16px 18px}
  .grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}
  .card{background:var(--card);border:1px solid var(--line);border-radius:11px;
        overflow:hidden;display:flex;flex-direction:column}
  .card.s-needs{border-left:4px solid var(--todo-needs)}
  .card.s-prog{border-left:4px solid var(--todo-prog)}
  .card.s-ready{border-left:4px solid var(--todo-ready)}
  .imgs{display:flex;gap:2px;background:var(--card2);min-height:120px;
        overflow-x:auto;scrollbar-width:thin}
  .imgs img{height:150px;width:auto;object-fit:contain;background:#fff;cursor:zoom-in}
  .noimg{display:flex;align-items:center;justify-content:center;min-height:120px;
         width:100%;color:var(--dim);font-size:13px;font-style:italic}
  .imgtag{position:relative}
  .imgtag span{position:absolute;left:4px;top:4px;font-size:10px;padding:1px 5px;
        border-radius:4px;background:rgba(0,0,0,.6);color:#fff;text-transform:uppercase;
        letter-spacing:.03em}
  .body{padding:10px 12px;display:flex;flex-direction:column;gap:6px}
  .name{font-weight:600;font-size:13.5px;line-height:1.3}
  .meta{color:var(--dim);font-size:12px;display:flex;flex-wrap:wrap;gap:8px}
  .src{font-size:11px;padding:1px 7px;border-radius:5px;font-weight:600}
  .src-web{background:var(--web);color:#241505}.src-berg{background:var(--berg);color:#1a0733}
  .src-allegro{background:var(--allegro);color:#053021}.src-dark{background:var(--dark);color:#2a0508}
  .note{color:var(--dim);font-size:11.5px;font-style:italic}
  .status{display:flex;gap:5px;margin-top:2px}
  .sbtn{flex:1;padding:5px;border:1px solid var(--line);border-radius:6px;
        background:var(--card2);cursor:pointer;font-size:11px;color:var(--dim);text-align:center}
  .sbtn.on{color:var(--fg);font-weight:600}
  .sbtn.needs.on{background:var(--todo-needs);color:#2a0508;border-color:var(--todo-needs)}
  .sbtn.prog.on{background:var(--todo-prog);color:#2a2205;border-color:var(--todo-prog)}
  .sbtn.ready.on{background:var(--todo-ready);color:#053021;border-color:var(--todo-ready)}
  .lightbox{position:fixed;inset:0;background:rgba(0,0,0,.9);display:none;
            align-items:center;justify-content:center;z-index:50;cursor:zoom-out}
  .lightbox.on{display:flex}
  .lightbox img{max-width:94vw;max-height:94vh;background:#fff}
  .empty{color:var(--dim);padding:40px;text-align:center}
</style>
</head>
<body>
<header>
  <h1>sportking — product image map <small id="sub"></small></h1>
  <div class="tabs">
    <div class="tab on" data-wave="todo" onclick="setTab(this)">To do (manual photos)</div>
    <div class="tab" data-wave="done" onclick="setTab(this)">Auto / catalog-safe</div>
  </div>
  <div class="bar">
    <input id="q" placeholder="search name / EAN / category…" oninput="draw()">
    <span class="chip" data-f="noimg" onclick="tog(this)">no image</span>
    <span class="chip" data-f="hasimg" onclick="tog(this)">has image</span>
    <span class="chip" data-f="needs" onclick="tog(this)">needs-photo</span>
    <span class="chip" data-f="prog" onclick="tog(this)">in-progress</span>
    <span class="chip" data-f="ready" onclick="tog(this)">ready</span>
    <span class="spacer"></span>
    <button class="act" onclick="exportCsv()">export status CSV</button>
    <label class="act" style="cursor:pointer">import<input type="file" accept=".csv"
      style="display:none" onchange="importCsv(this)"></label>
  </div>
</header>
<main><div id="grid" class="grid"></div></main>
<div class="lightbox" id="lb" onclick="this.classList.remove('on')"><img id="lbi"></div>
<script>
const DATA = __DATA__;
const KEY = "sportking-photo-status";
let status = JSON.parse(localStorage.getItem(KEY) || "{}");
let tab = "todo";
const filters = new Set();

function save(){ localStorage.setItem(KEY, JSON.stringify(status)); }
function setStatus(ean, s){
  status[ean] = (status[ean] === s) ? undefined : s;
  if(!status[ean]) delete status[ean];
  save(); draw();
}
function setTab(el){
  document.querySelectorAll(".tab").forEach(t=>t.classList.remove("on"));
  el.classList.add("on"); tab = el.dataset.wave; draw();
}
function tog(el){
  const f = el.dataset.f;
  if(filters.has(f)){ filters.delete(f); el.classList.remove("on"); }
  else { filters.add(f); el.classList.add("on"); }
  draw();
}
function stateOf(ean){ return status[ean] || "needs"; }

function pass(p){
  if(p.wave !== tab) return false;
  const q = document.getElementById("q").value.trim().toLowerCase();
  if(q && !(p.name.toLowerCase().includes(q) || p.ean.includes(q)
         || (p.category||"").toLowerCase().includes(q))) return false;
  if(filters.has("noimg") && p.n_images>0) return false;
  if(filters.has("hasimg") && p.n_images===0) return false;
  for(const s of ["needs","prog","ready"])
    if(filters.has(s) && stateOf(p.ean)!==s) return false;
  return true;
}

function draw(){
  const list = DATA.filter(pass);
  const grid = document.getElementById("grid");
  const todo = DATA.filter(p=>p.wave==="todo");
  const ready = todo.filter(p=>status[p.ean]==="ready").length;
  document.getElementById("sub").textContent =
    `· ${todo.length} to do, ${ready} marked ready · showing ${list.length}`;
  if(!list.length){ grid.innerHTML = '<div class="empty">nothing matches</div>'; return; }
  grid.innerHTML = list.map(card).join("");
}

function card(p){
  const st = stateOf(p.ean);
  const imgs = p.images.length
    ? `<div class="imgs">${p.images.map(i=>
        `<div class="imgtag"><span>${i.kind}</span>`+
        `<img loading="lazy" src="${i.src}" onclick="zoom('${i.src}')"></div>`).join("")}</div>`
    : `<div class="imgs"><div class="noimg">no image on file</div></div>`;
  const statusRow = p.wave==="todo" ? `<div class="status">
      ${sbtn(p.ean,"needs","needs-photo",st)}
      ${sbtn(p.ean,"prog","in-progress",st)}
      ${sbtn(p.ean,"ready","ready",st)}</div>` : "";
  const note = p.note ? `<div class="note">${esc(p.note)}</div>` : "";
  return `<div class="card ${p.wave==="todo"?"s-"+st:""}">
    ${imgs}
    <div class="body">
      <div class="name">${esc(p.name)}</div>
      <div class="meta">
        <span class="src src-${p.source.replace('-feed','')}">${p.source}</span>
        <span>EAN ${p.ean}</span><span>qty ${p.qty}</span>
        <span>${p.n_images} img</span>
        ${p.article?`<span>art ${p.article}</span>`:""}
      </div>
      ${p.category?`<div class="meta">${esc(p.category)}</div>`:""}
      ${note}${statusRow}
    </div></div>`;
}
function sbtn(ean,s,label,cur){
  return `<div class="sbtn ${s} ${cur===s?"on":""}" onclick="setStatus('${ean}','${s}')">${label}</div>`;
}
function zoom(src){ document.getElementById("lbi").src=src;
  document.getElementById("lb").classList.add("on"); }
function esc(s){ return String(s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c])); }

function exportCsv(){
  const rows=[["ean","name","status"]];
  DATA.filter(p=>p.wave==="todo").forEach(p=>
    rows.push([p.ean,'"'+p.name.replace(/"/g,'""')+'"',stateOf(p.ean)]));
  const blob=new Blob([rows.map(r=>r.join(",")).join("\n")],{type:"text/csv"});
  const a=document.createElement("a");a.href=URL.createObjectURL(blob);
  a.download="photo-status.csv";a.click();
}
function importCsv(inp){
  const f=inp.files[0]; if(!f) return;
  const r=new FileReader();
  r.onload=()=>{ f.text?0:0;
    r.result.split(/\r?\n/).slice(1).forEach(line=>{
      const m=line.match(/^(\d+),/); if(!m) return;
      const ean=m[1], st=line.split(",").pop().trim();
      if(["needs","prog","ready"].includes(st)){ if(st==="needs") delete status[ean]; else status[ean]=st; }
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
