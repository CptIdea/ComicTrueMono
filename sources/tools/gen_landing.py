#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the single-page landing/demo (index.html at the repo root) for GitHub Pages.
Self-contained: inline CSS/JS, fonts referenced by relative path. Data (coverage,
provenance) comes from the real cmap of ComicTrueMono-Regular.
Run: python3 sources/tools/gen_landing.py
"""
from fontTools.ttLib import TTFont
import html, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT = ROOT + "/fonts/ttf/ComicTrueMono-Regular.ttf"
OUT  = ROOT + "/index.html"

cm = set(TTFont(FONT).getBestCmap())

WEIGHTS = [("Thin",100),("ExtraLight",200),("Light",300),("Regular",400),
           ("Medium",500),("SemiBold",600),("Bold",700),("ExtraBold",800),("Black",900)]

def ital_file(n):
    return "ComicTrueMono-Italic.ttf" if n == "Regular" else f"ComicTrueMono-{n}Italic.ttf"

FACES = "\n".join(
    f'@font-face{{font-family:CTM;font-weight:{w};font-style:normal;font-display:swap;src:url("fonts/ttf/ComicTrueMono-{n}.ttf");}}\n'
    f'@font-face{{font-family:CTM;font-weight:{w};font-style:italic;font-display:swap;src:url("fonts/ttf/{ital_file(n)}");}}'
    for n, w in WEIGHTS)

# ---- weight ladder rows ----
LADDER = "".join(
    f'<div class="wrow" data-w="{w}"><span class="wlab">{n}<b>{w}</b></span>'
    f'<span class="wsamp" style="font-weight:{w}">The quick brown fox — příliš žluťoučký kůň — garçon, Łódź, øre</span></div>'
    for n, w in WEIGHTS)

# ---- coverage by block ----
def block(cp):
    r = [(0x00,0x80,"Basic Latin"),(0x80,0x100,"Latin-1 Supplement"),(0x100,0x180,"Latin Extended-A"),
         (0x180,0x250,"Latin Extended-B"),(0x2000,0x2070,"Punctuation"),(0x20A0,0x20D0,"Currency"),
         (0x2100,0x2150,"Letterlike"),(0x2190,0x2200,"Arrows"),(0x2200,0x2300,"Math"),(0x370,0x400,"Greek"),
         (0xA720,0xA800,"Latin Ext-D")]
    for a,b,name in r:
        if a<=cp<b: return name
    return "Other"
groups, order = {}, []
for cp in sorted(cm):
    b = block(cp)
    groups.setdefault(b, []).append(cp)
    if b not in order: order.append(b)
COVERAGE = ""
for b in order:
    cs = "".join(html.escape(chr(cp)) for cp in groups[b])
    COVERAGE += (f'<div class="cvblk"><div class="cvhdr">{html.escape(b)}'
                 f'<span>{len(groups[b])}</span></div><div class="cvglyphs">{cs}</div></div>')

# ---- provenance story cards ----
def has(cps): return "".join(chr(c) for c in cps if c in cm)
STORY = [
    ("Comic Mono", "dtinth", "MIT", "The monospaced base — clean 1116-unit metric.",
     has(range(0x41,0x5B)) + " a b c 0 1 2"),
    ("Comic Shanns", "Shannon Miwa", "MIT", "The root letterforms + full European Latin.",
     "À Ç É Ñ Ö Ü ā ć đ ģ ķ ł ń ő ř š ž"),
    ("Serious Shanns", "kaBeech", "MIT", "The λ glyph, hand-drawn italics, and Ł ł.",
     "λ Ł ł  f g k x  (italic)"),
    ("clsn fork", "clsn — PR open since 2021", "MIT", "Ligatures & rare letters nobody merged.",
     "Æ æ Œ œ Þ þ ſ ƿ Ƿ ꝛ ∀ ∃ ∄"),
    ("lilmayu fork", "lilmayu — PR open since 2022", "MIT", "Correctly rotated caron / háček.",
     "Č č Ě ě Ř ř Š š Ž ž ˇ"),
    ("In-project", "constructed here", "new", "Absent from every source — built by hand.",
     "ø Ø ·"),
]
PROV = ""
for name, who, lic, desc, sample in STORY:
    liccls = "new" if lic == "new" else "mit"
    PROV += (f'<div class="pcard"><div class="ptop"><span class="pname">{html.escape(name)}</span>'
             f'<span class="plic {liccls}">{html.escape(lic)}</span></div>'
             f'<div class="pwho">{html.escape(who)}</div>'
             f'<div class="pdesc">{html.escape(desc)}</div>'
             f'<div class="psample">{html.escape(sample)}</div></div>')

HERO_LETTERS = "".join(
    f'<span class="hl" style="--i:{i}">{html.escape(ch)}</span>' if ch != " " else '<span class="hsp"> </span>'
    for i, ch in enumerate("Comic True Mono"))

TOTAL = len(cm)

TPL = r"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Comic True Mono — a monospaced Comic Sans for code</title>
<meta name="description" content="A free, MIT-licensed monospaced Comic Sans for code. 9 weights x italic, full European Latin, assembled from abandoned free forks.">
<style>
__FACES__
:root{
  --bg:#fbfbfa; --fg:#18191d; --mut:#6a6c74; --line:#e7e7ea; --card:#fff;
  --accent:#e8552d; --accent2:#2d7de8; --mit:#1e8449; --new:#b8842a;
  --grid:rgba(0,0,0,.035);
}
:root[data-theme="dark"], html.dark:root{}
@media (prefers-color-scheme: dark){
  :root{ --bg:#111216; --fg:#e9e9ec; --mut:#8b8e97; --line:#26272e; --card:#191a20;
         --accent:#ff6a42; --accent2:#5b9bff; --mit:#5edc9a; --new:#e0b464; --grid:rgba(255,255,255,.045); }
}
:root[data-theme="dark"]{ --bg:#111216; --fg:#e9e9ec; --mut:#8b8e97; --line:#26272e; --card:#191a20;
  --accent:#ff6a42; --accent2:#5b9bff; --mit:#5edc9a; --new:#e0b464; --grid:rgba(255,255,255,.045); }
:root[data-theme="light"]{ --bg:#fbfbfa; --fg:#18191d; --mut:#6a6c74; --line:#e7e7ea; --card:#fff;
  --accent:#e8552d; --accent2:#2d7de8; --mit:#1e8449; --new:#b8842a; --grid:rgba(0,0,0,.035); }

*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;line-height:1.5;
  -webkit-font-smoothing:antialiased;}
.mono{font-family:CTM,ui-monospace,monospace}
.wrap{max-width:1080px;margin:0 auto;padding:0 22px}
a{color:inherit}
section{padding:70px 0;border-top:1px solid var(--line)}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:700;margin:0 0 10px}
h2{font-size:clamp(24px,4vw,36px);margin:0 0 8px;letter-spacing:-.02em}
.lead{color:var(--mut);font-size:16px;max-width:60ch;margin:0 0 26px}

/* top bar */
.nav{position:sticky;top:0;z-index:40;backdrop-filter:blur(10px);
  background:color-mix(in srgb,var(--bg) 82%,transparent);border-bottom:1px solid var(--line)}
.nav .wrap{display:flex;align-items:center;gap:18px;height:56px}
.brand{font-family:CTM;font-weight:800;letter-spacing:-.02em}
.nav a.lnk{color:var(--mut);text-decoration:none;font-size:14px}
.nav a.lnk:hover{color:var(--fg)}
.nav .spacer{flex:1}
.btn{display:inline-flex;align-items:center;gap:7px;border:1px solid var(--line);border-radius:999px;
  padding:7px 15px;font-size:14px;text-decoration:none;background:var(--card);cursor:pointer;color:var(--fg)}
.btn.pri{background:var(--accent);border-color:var(--accent);color:#fff}
.btn:hover{transform:translateY(-1px)}
.btn{transition:transform .12s ease}
#theme{border:1px solid var(--line);background:var(--card);border-radius:999px;width:34px;height:34px;cursor:pointer;color:var(--fg);font-size:15px}

/* hero */
.hero{position:relative;padding:76px 0 66px;overflow:hidden;border-top:0}
.hero::before{content:"";position:absolute;inset:0;z-index:0;
  background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);
  background-size:34px 34px;mask-image:radial-gradient(ellipse 80% 70% at 50% 30%,#000 40%,transparent 100%)}
.hero .wrap{position:relative;z-index:1}
.htitle{font-family:CTM;font-weight:400;line-height:.98;letter-spacing:-.03em;
  font-size:clamp(44px,11vw,116px);margin:6px 0 4px;display:flex;flex-wrap:wrap}
.htitle .hl{display:inline-block;transition:font-weight .25s linear;will-change:font-weight}
.htitle .hsp{width:.32em}
.htag{font-size:clamp(16px,2.4vw,21px);color:var(--mut);max-width:56ch;margin:12px 0 26px}
.htag b{color:var(--fg);font-weight:600}
.hbtns{display:flex;gap:12px;flex-wrap:wrap;align-items:center}
.pill{font-family:CTM;font-size:12px;border:1px solid var(--line);border-radius:999px;padding:5px 11px;color:var(--mut)}
.stats{display:flex;gap:26px;flex-wrap:wrap;margin-top:34px}
.stat b{font-family:CTM;font-size:26px;display:block;line-height:1}
.stat span{font-size:12px;color:var(--mut)}

/* tester */
.tester{border:1px solid var(--line);border-radius:16px;background:var(--card);overflow:hidden}
.tctrl{display:flex;gap:18px;align-items:center;flex-wrap:wrap;padding:14px 16px;border-bottom:1px solid var(--line);font-size:13px;color:var(--mut)}
.tctrl label{display:flex;align-items:center;gap:8px}
.tctrl input[type=range]{accent-color:var(--accent)}
.tewrap{position:relative}
.tarea,.thl{font-family:CTM;font-size:30px;line-height:1.5;padding:20px;margin:0;border:0;width:100%;
  min-height:200px;box-sizing:border-box;white-space:pre-wrap;overflow-wrap:break-word;letter-spacing:0;tab-size:2}
.thl{position:absolute;inset:0;color:var(--fg);pointer-events:none;overflow:hidden}
.tarea{position:relative;background:transparent;color:transparent;caret-color:var(--accent);resize:vertical;outline:0}
.thl .kw{color:#a626a4}.thl .st{color:#50a14f}.thl .co{color:#2e8b8b;font-style:italic}.thl .nu{color:#986801}
@media(prefers-color-scheme:dark){.thl .kw{color:#c678dd}.thl .st{color:#98c379}.thl .co{color:#5fb9b9}.thl .nu{color:#d19a66}}
:root[data-theme="dark"] .thl .kw{color:#c678dd}:root[data-theme="dark"] .thl .st{color:#98c379}:root[data-theme="dark"] .thl .co{color:#5fb9b9}:root[data-theme="dark"] .thl .nu{color:#d19a66}
:root[data-theme="light"] .thl .kw{color:#a626a4}:root[data-theme="light"] .thl .st{color:#50a14f}:root[data-theme="light"] .thl .co{color:#2e8b8b}:root[data-theme="light"] .thl .nu{color:#986801}
.wname{font-family:CTM;color:var(--fg);min-width:78px;display:inline-block}

/* weights */
.wrow{display:flex;align-items:baseline;gap:16px;padding:9px 0;border-bottom:1px solid var(--line);cursor:default}
.wrow:hover{background:color-mix(in srgb,var(--accent) 7%,transparent)}
.wlab{width:120px;flex:none;font-size:12px;color:var(--mut);display:flex;justify-content:space-between;padding-right:12px}
.wlab b{font-family:CTM;color:var(--fg)}
.wsamp{font-family:CTM;font-size:clamp(15px,2.3vw,24px);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

/* coverage */
.cvhead{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:16px}
.cvblk{margin-bottom:14px}
.cvhdr{font-size:12px;color:var(--mut);display:flex;gap:8px;align-items:baseline;margin-bottom:3px}
.cvhdr span{font-family:CTM;font-size:11px;opacity:.7}
.cvglyphs{font-family:CTM;font-size:var(--cvfs,26px);line-height:1.7;word-break:break-all;
  background-image:repeating-linear-gradient(90deg,var(--grid) 0 1ch,transparent 1ch 2ch)}


/* provenance */
.pgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.pcard{border:1px solid var(--line);border-radius:14px;background:var(--card);padding:16px 16px 14px}
.ptop{display:flex;justify-content:space-between;align-items:center;gap:10px}
.pname{font-weight:700}
.plic{font-size:11px;font-family:CTM;padding:2px 8px;border-radius:999px}
.plic.mit{color:var(--mit);background:color-mix(in srgb,var(--mit) 15%,transparent)}
.plic.new{color:var(--new);background:color-mix(in srgb,var(--new) 16%,transparent)}
.pwho{font-size:12px;color:var(--mut);margin-top:2px}
.pdesc{font-size:14px;margin:9px 0 10px}
.psample{font-family:CTM;font-size:22px;line-height:1.5;word-break:break-all;color:var(--fg)}

/* install */
.cols{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.box{border:1px solid var(--line);border-radius:14px;background:var(--card);padding:18px}
pre.code{font-family:CTM;background:color-mix(in srgb,var(--fg) 5%,transparent);border-radius:10px;
  padding:12px 14px;overflow-x:auto;font-size:13.5px;margin:10px 0 0}
.note{color:var(--mut);font-size:13px}
.demolinks{display:flex;gap:10px;flex-wrap:wrap;margin-top:6px}
.demolinks a{font-size:13px;text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:6px 12px;color:var(--mut)}
.demolinks a:hover{color:var(--fg);border-color:var(--accent)}

footer{border-top:1px solid var(--line);padding:34px 0 60px;color:var(--mut);font-size:13px}
footer a{color:var(--accent);text-decoration:none}

.reveal{opacity:0;transform:translateY(14px);transition:opacity .6s ease,transform .6s ease}
.reveal.in{opacity:1;transform:none}
@media (max-width:720px){ .cols{grid-template-columns:1fr} .wlab{width:96px} }
@media (prefers-reduced-motion:reduce){ .htitle .hl{transition:none} .reveal{transition:none;opacity:1;transform:none} }
</style>

<div class="nav">
  <div class="wrap">
    <span class="brand">Comic True Mono</span>
    <span class="spacer"></span>
    <a class="lnk" href="#type">Type</a>
    <a class="lnk" href="#weights">Weights</a>
    <a class="lnk" href="#glyphs">Glyphs</a>
    <a class="lnk" href="#story">Story</a>
    <a class="lnk" href="#get">Get it</a>
    <button id="theme" title="Toggle theme">◐</button>
  </div>
</div>

<header class="hero">
  <div class="wrap">
    <div class="pill mono">MIT · free · monospaced</div>
    <h1 class="htitle" id="htitle">__HERO__</h1>
    <p class="htag">A monospaced <b>Comic Sans for code</b>, gathered from scattered forks and
      years-old unmerged pull requests into one free, MIT-licensed family — <b>nine weights</b>,
      italics, and full European Latin.</p>
    <div class="hbtns">
      <a class="btn pri" href="#get">Download</a>
      <a class="btn" href="https://github.com/CptIdea/ComicTrueMono" id="ghlink">GitHub ↗</a>
      <span class="pill mono">9 weights × italic</span>
    </div>
    <div class="stats mono">
      <div class="stat"><b>__TOTAL__</b><span>glyphs</span></div>
      <div class="stat"><b>9×2</b><span>weights + italic</span></div>
      <div class="stat"><b>1116</b><span>mono advance</span></div>
      <div class="stat"><b>100%</b><span>MIT</span></div>
    </div>
  </div>
</header>

<section id="type">
  <div class="wrap reveal">
    <p class="eyebrow">Try it</p>
    <h2>Type something.</h2>
    <p class="lead">Every weight and the italic are here. Edit the text, drag the weight.</p>
    <div class="tester">
      <div class="tctrl">
        <label>Weight <input id="tw" type="range" min="0" max="8" value="3" step="1"> <span class="wname" id="twn">Regular</span></label>
        <label>Size <input id="ts" type="range" min="16" max="64" value="30"> <span class="mono" id="tsn">30</span></label>
        <label><input id="ti" type="checkbox"> Italic</label>
      </div>
      <div class="tewrap">
        <pre class="thl mono" id="thl" aria-hidden="true"></pre>
        <textarea class="tarea" id="tarea" spellcheck="false">func Greet(u User) string {
	// garçon · Łódź · smørrebrød · Žižkov
	return "Ærø · Œuvre · λ = ∀x∃y ≤ ≥ ± × ÷ €"
}</textarea>
      </div>
    </div>
  </div>
</section>

<section id="weights">
  <div class="wrap reveal">
    <p class="eyebrow">Nine weights</p>
    <h2>Thin to Black — all automatic.</h2>
    <p class="lead">Bold is calibrated to the real Comic Mono Bold; every other weight and every italic
      is generated from one master. Draw a glyph once, get it in all eighteen fonts.</p>
    __LADDER__
  </div>
</section>

<section id="glyphs">
  <div class="wrap reveal">
    <div class="cvhead">
      <div><p class="eyebrow">Coverage</p><h2 style="margin:0">__TOTAL__ glyphs, one width.</h2></div>
      <label class="note mono">size <input id="cvs" type="range" min="18" max="44" value="26" style="accent-color:var(--accent)"></label>
    </div>
    <p class="lead">Full European Latin, symbols, currency, arrows, math — laid over a one-cell grid.
      Every glyph fills exactly one column: that is what monospaced means.</p>
    __COVERAGE__
  </div>
</section>

<section id="story">
  <div class="wrap reveal">
    <p class="eyebrow">How it was made</p>
    <h2>Assembled from unmerged pull requests.</h2>
    <p class="lead">Good contributions to the free monospaced Comic Sans forks sat unmerged for years —
      the original Comic Shanns went quiet in 2023, and even the maintained repos still ignore font PRs
      (kaBeech's italics have been open since 2024). Comic True Mono gathers that scattered work into one
      place — every glyph from an MIT source — and constructs the few that existed nowhere.</p>
    <div class="pgrid">__PROV__</div>
  </div>
</section>

<section id="get">
  <div class="wrap reveal">
    <p class="eyebrow">Get it</p>
    <h2>Install or build.</h2>
    <div class="cols">
      <div class="box">
        <b>Install</b>
        <p class="note">Download the family and install (double-click on macOS/Windows, or drop into
          <span class="mono">~/.local/share/fonts</span> on Linux). Set your editor font to <b>Comic True Mono</b>.</p>
        <a class="btn pri" href="https://github.com/CptIdea/ComicTrueMono/tree/main/fonts/ttf" style="margin-top:6px">Browse fonts/ttf ↗</a>
      </div>
      <div class="box">
        <b>Build from source</b>
        <p class="note">Requires FontForge + fontTools. Everything derives from one master.</p>
        <pre class="code">pip install -r requirements.txt
make            # build fonts + specimens</pre>
      </div>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    <b class="mono">Comic True Mono</b> · MIT.
    Built on Comic Mono (dtinth), Comic Shanns (Shannon Miwa), Serious Shanns (kaBeech),
    and the clsn &amp; lilmayu forks — all MIT.
    Constructed in-project: ø Ø ·.
    <br>See <a href="LICENSE">LICENSE</a> and <a href="RESEARCH.md">RESEARCH.md</a>.
  </div>
</footer>

<script>
// theme toggle (respects OS default, remembers choice)
(function(){
  const root=document.documentElement;
  const saved=localStorage.getItem('ctm-theme');
  if(saved) root.setAttribute('data-theme',saved);
  document.getElementById('theme').onclick=()=>{
    const cur=root.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
    const next=cur==='dark'?'light':'dark';
    root.setAttribute('data-theme',next); localStorage.setItem('ctm-theme',next);
  };
})();

// hero weight-wave
(function(){
  const els=[...document.querySelectorAll('#htitle .hl')];
  if(matchMedia('(prefers-reduced-motion:reduce)').matches) return;
  const steps=[100,200,300,400,500,600,700,800,900];
  let t=0;
  setInterval(()=>{
    t+=0.08;
    els.forEach((el,i)=>{
      const v=(Math.sin(t+i*0.5)+1)/2;           // 0..1
      el.style.fontWeight=steps[Math.round(v*8)];
    });
  },90);
})();

// type tester with live syntax highlighting (transparent textarea over a highlighted <pre>)
(function(){
  const NAMES=['Thin','ExtraLight','Light','Regular','Medium','SemiBold','Bold','ExtraBold','Black'];
  const W=[100,200,300,400,500,600,700,800,900];
  const ta=document.getElementById('tarea'),tw=document.getElementById('tw'),ts=document.getElementById('ts'),ti=document.getElementById('ti'),thl=document.getElementById('thl');
  const KW=/\b(func|return|package|import|type|struct|interface|map|chan|string|int|byte|rune|bool|error|for|range|if|else|switch|case|var|const|nil|true|false|go|defer)\b/;
  const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  function hl(code){
    const re=new RegExp('(//[^\\n]*)|("(?:[^"\\\\]|\\\\.)*")|'+KW.source+'|\\b(\\d+)\\b','g');
    let out='',last=0,m;
    while((m=re.exec(code))){
      out+=esc(code.slice(last,m.index));
      if(m[1])out+='<span class="co">'+esc(m[1])+'</span>';
      else if(m[2])out+='<span class="st">'+esc(m[2])+'</span>';
      else if(m[3])out+='<span class="kw">'+esc(m[3])+'</span>';
      else if(m[4])out+='<span class="nu">'+esc(m[4])+'</span>';
      last=re.lastIndex;
    }
    return out+esc(code.slice(last));
  }
  function render(){ thl.innerHTML=hl(ta.value)+'\n'; }
  function upd(){
    const w=W[+tw.value], st=ti.checked?'italic':'normal', fs=ts.value+'px';
    [ta,thl].forEach(e=>{e.style.fontWeight=w;e.style.fontStyle=st;e.style.fontSize=fs;});
    document.getElementById('twn').textContent=NAMES[+tw.value];
    document.getElementById('tsn').textContent=ts.value;
  }
  ta.addEventListener('input',render);
  ta.addEventListener('scroll',()=>{thl.scrollTop=ta.scrollTop;thl.scrollLeft=ta.scrollLeft;});
  [tw,ts,ti].forEach(e=>e.addEventListener('input',upd));
  render(); upd();
})();

// coverage size
document.getElementById('cvs').addEventListener('input',e=>{
  document.querySelectorAll('.cvglyphs').forEach(g=>g.style.setProperty('--cvfs',e.target.value+'px'));
});

// scroll reveal
(function(){
  const io=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target);}}),{threshold:.12});
  document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
})();
</script>
</html>
"""

out = (TPL.replace("__FACES__", FACES).replace("__HERO__", HERO_LETTERS)
          .replace("__TOTAL__", str(TOTAL)).replace("__LADDER__", LADDER)
          .replace("__COVERAGE__", COVERAGE).replace("__PROV__", PROV))
open(OUT, "w").write(out)
print("index.html:", TOTAL, "glyphs,", len(order), "coverage blocks,", len(STORY), "story cards")
