#!/usr/bin/env python3
"""Generator situs Lensa Hukum Banyuwangi.

Semua isi (berita, halaman, kategori, pengaturan) dibaca dari folder content/,
yang diedit lewat CMS di /admin. Tidak perlu mengubah file ini untuk menulis berita.
Hasil build ada di folder dist/.   Jalankan:  python3 build.py
"""
import glob, json, math, os, re, shutil, sys
from html import escape

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "dist")
CUR = ' aria-current="page"'
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return json.load(f)


# ---------- Markdown mini (aman: semua teks di-escape) ----------
def _safe_url(u):
    u = u.strip()
    return u if re.match(r"^(https?://|mailto:|/|#|\.{0,2}/|[\w-]+)", u) and not re.match(r"^\s*(javascript|data|vbscript):", u, re.I) else "#"


def inline(t):
    t = escape(t, quote=False)
    t = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", lambda m: f'<img src="{escape(_safe_url(m[2]))}" alt="{escape(m[1])}" loading="lazy">', t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{escape(_safe_url(m[2]))}">{m[1]}</a>', t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    return t


def md(text):
    out, para, lst, quote = [], [], None, []

    def flush():
        nonlocal para, lst, quote
        if para:
            out.append("<p>" + "<br>".join(inline(x) for x in para) + "</p>")
        if lst:
            tag, items = lst
            out.append(f"<{tag}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{tag}>")
        if quote:
            out.append("<blockquote><p>" + "<br>".join(inline(x) for x in quote) + "</p></blockquote>")
        para, lst, quote = [], None, []

    for raw in (text or "").replace("\r", "").split("\n"):
        line = raw.rstrip()
        if not line.strip():
            flush(); continue
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            flush(); lvl = max(2, min(len(m[1]), 4))  # h1 dipakai judul halaman
            out.append(f"<h{lvl}>{inline(m[2])}</h{lvl}>"); continue
        if re.match(r"^(-{3,}|\*{3,})$", line):
            flush(); out.append("<hr>"); continue
        m = re.match(r"^\s*[-*+]\s+(.*)$", line)
        if m:
            if not (lst and lst[0] == "ul"): flush(); lst = ("ul", [])
            lst[1].append(m[1]); continue
        m = re.match(r"^\s*\d+[.)]\s+(.*)$", line)
        if m:
            if not (lst and lst[0] == "ol"): flush(); lst = ("ol", [])
            lst[1].append(m[1]); continue
        m = re.match(r"^>\s?(.*)$", line)
        if m:
            if not quote: flush()
            quote.append(m[1]); continue
        if lst or quote: flush()
        para.append(line.strip())
    flush()
    return "\n".join(out)


# ---------- Muat konten ----------
S = load("content/pengaturan/situs.json")
SITE = S.get("nama_situs") or "Lensa Hukum Banyuwangi"
EMAIL = S.get("email", "")
CATEGORIES = [(c["slug"], c["nama"], c.get("deskripsi", "")) for c in load("content/pengaturan/kategori.json")["kategori"]]
CAT_NAME = {s: n for s, n, _ in CATEGORIES}


def fmt_date(iso):
    y, m, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
    return f"{d} {BULAN[m - 1]} {y}"


def load_articles():
    arts = []
    for p in sorted(glob.glob(os.path.join(ROOT, "content/berita/*.json"))):
        slug = os.path.splitext(os.path.basename(p))[0]
        d = json.load(open(p, encoding="utf-8"))
        if d.get("status", "terbit") != "terbit":
            continue
        cats = [c for c in d.get("kategori", []) if c in CAT_NAME]
        if not cats:
            print(f"PERINGATAN: berita '{slug}' dilewati karena belum punya kategori yang valid", file=sys.stderr)
            continue
        words = len(re.findall(r"\w+", d.get("isi", "")))
        tgl = d.get("tanggal", "2000-01-01T00:00")
        arts.append(dict(
            slug=slug, url=f"artikel/{slug}.html", title=d["judul"], cats=cats, cat=cats[0],
            lead=d.get("ringkasan", ""), excerpt=d.get("kutipan") or d.get("ringkasan", ""),
            img=d.get("gambar") or "", alt=d.get("alt", ""), author=d.get("penulis") or "Redaksi",
            utama=bool(d.get("utama")), pilihan=bool(d.get("pilihan")), note=d.get("catatan", ""), source=d.get("sumber", ""),
            body=d.get("isi", ""), mins=max(1, math.ceil(words / 200)), iso=tgl, date=fmt_date(tgl)))
    arts.sort(key=lambda a: a["iso"], reverse=True)
    return arts


ARTICLES = load_articles()

def load_videos():
    items = []
    for p in sorted(glob.glob(os.path.join(ROOT, "content/video/*.json"))):
        d = json.load(open(p, encoding="utf-8"))
        if d.get("status", "draf") != "terbit":
            continue
        iso = d.get("tanggal", "2000-01-01T00:00")
        items.append(dict(
            slug=os.path.splitext(os.path.basename(p))[0],
            title=d.get("judul", "Video Redaksi"),
            desc=d.get("deskripsi", ""),
            file=d.get("file_video", ""),
            thumb=d.get("thumbnail", ""),
            author=d.get("penulis", "Redaksi"),
            iso=iso,
            date=fmt_date(iso),
            source=d.get("sumber", ""),
            embed=d.get("url_embed", ""),
            category=d.get("kategori", "Video Redaksi")
        ))
    items.sort(key=lambda x: x["iso"], reverse=True)
    return items

VIDEOS = load_videos()
NAV = [("index.html", "Beranda", "home")] + [(f"kategori/{s}.html", n, s) for s, n, _ in CATEGORIES] + [
    ("tentang.html", "Tentang Kami", "tentang"),
    ("redaksi.html", "Redaksi", "redaksi"),
    ("kontak.html", "Kontak", "kontak"),
    ("video.html", "Video", "video"),
    ("live.html", "Live", "live"),
    ("epaper.html", "E-Paper", "epaper"),
]


def img_url(u, r):
    """Gambar unggahan CMS ditulis sebagai /uploads/x.jpg; ubah agar relatif terhadap halaman."""
    return r + u.lstrip("/") if u.startswith("/uploads/") else u


# ---------- Kerangka halaman ----------
def head(title, desc, r, extra=""):
    return f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<meta property="og:site_name" content="{escape(SITE)}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:locale" content="id_ID">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0e1b2c">
<link rel="icon" type="image/svg+xml" href="{r}assets/favicon.svg">
<link rel="stylesheet" href="{r}style.css">{extra}
{f'<script data-goatcounter="https://{escape(S["analytics_code"])}.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>' if S.get("analytics_code") else ""}
<script>
document.addEventListener("play", function(e) {{
  if (e.target && e.target.tagName === "VIDEO" && window.goatcounter && window.goatcounter.count) {{
    var card = e.target.closest("[data-video-slug]");
    if (card) window.goatcounter.count({{path: "/video-play/" + card.dataset.videoSlug, title: "Video play"}});
  }}
}}, true);
</script>
</head>
<body>
<a class="skip" href="#isi">Lompat ke konten</a>
"""


def header(r, active):
    links = "".join(f'<a href="{r}{h}"{CUR if k == active else ""}>{escape(n)}</a>' for h, n, k in NAV)
    return f"""<header class="masthead">
<div class="wrap masthead-row">
<a class="brand" href="{r}index.html"><img src="{r}assets/logo.svg" alt="" width="46" height="46"><span><strong>Lensa Hukum</strong><small>Banyuwangi</small></span></a>
<p class="tagline">{escape(S.get('tagline', ''))}</p>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu">Menu</button>
</div>
<nav class="nav" aria-label="Navigasi utama"><div class="wrap nav-row">
<div class="navlinks" id="menu">{links}</div>
<form class="search" action="{r}cari.html" method="get" role="search"><input type="search" name="q" aria-label="Cari berita" placeholder="Cari berita"><button type="submit">Cari</button></form>
</div></nav>
</header>
"""


def footer(r):
    rub = "".join(f'<a href="{r}kategori/{s}.html">{escape(n)}</a>' for s, n, _ in CATEGORIES[:6])
    mail = f'<p><a href="mailto:{escape(EMAIL)}">{escape(EMAIL)}</a></p>' if EMAIL else ""
    return f"""<footer class="site-footer"><div class="wrap">
<div class="footer-grid">
<div><div class="footer-brand"><img src="{r}assets/logo.svg" alt="" width="40" height="40"><strong>{escape(SITE)}</strong></div>
<p>Media online yang menyajikan informasi hukum, kriminal, pemerintahan, peristiwa, dan dinamika masyarakat Banyuwangi serta Indonesia.</p></div>
<div class="footer-links"><h3>Rubrik</h3>{rub}</div>
<div class="footer-links"><h3>Redaksi</h3><a href="{r}tentang.html">Tentang Kami</a><a href="{r}redaksi.html">Pedoman Redaksi</a><a href="{r}kontak.html">Kontak Redaksi</a><a href="{r}video.html">Video</a>{mail}</div>
</div>
<div class="copyright"><span>© <span data-year>2026</span> {escape(SITE)}. Hak cipta dilindungi.</span><span>Independen, berimbang, terpercaya.</span></div>
</div></footer>
<script src="{r}data.js"></script>
<script src="{r}script.js"></script>
</body>
</html>
"""


def card(a, r):
    if a["img"]:
        thumb = f'<img src="{escape(img_url(a["img"], r))}" alt="{escape(a["alt"])}" loading="lazy" width="1000" height="625">'
    else:
        thumb = '<div class="thumb-ph" aria-hidden="true"></div>'
    cats = " / ".join(CAT_NAME[c] for c in a["cats"])
    return f"""<article class="card">
<a class="thumb" href="{r}{a['url']}" tabindex="-1" aria-hidden="true">{thumb}</a>
<div class="card-body"><span class="category">{escape(cats)}</span>
<h3><a href="{r}{a['url']}">{escape(a['title'])}</a></h3>
<p>{escape(a['excerpt'])}</p>
<div class="meta"><time datetime="{a['iso']}">{a['date']}</time><span>{escape(a['author'])}</span></div></div>
</article>
"""


def page(path, html):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)


def static_page(path, key, active):
    d = load(f"content/halaman/{key}.json")
    extra = ""
    if key == "kontak":
        rows = []
        if S.get("email"): rows.append(f'<dt>Email</dt><dd><a href="mailto:{escape(S["email"])}">{escape(S["email"])}</a></dd>')
        if S.get("whatsapp"): rows.append(f'<dt>WhatsApp</dt><dd>{escape(S["whatsapp"])}</dd>')
        if S.get("alamat"): rows.append(f'<dt>Alamat</dt><dd>{escape(S["alamat"])}</dd>')
        if S.get("wilayah"): rows.append(f'<dt>Wilayah liputan</dt><dd>{escape(S["wilayah"])}</dd>')
        extra = f'<dl class="contact">{"".join(rows)}</dl>'
    note = f'<div class="notice">{escape(d["catatan"])}</div>' if d.get("catatan") else ""
    body = f'<h1>{escape(d["judul"])}</h1><p class="lead">{escape(d.get("lead", ""))}</p>{md(d.get("isi", ""))}{extra}{note}'
    page(path, head(f"{d['judul']} | {SITE}", d.get("lead", ""), "") + header("", active) +
         f'<main id="isi" class="wrap"><article class="article">{body}</article></main>\n' + footer(""))



def video_card(v, r=""):
    poster = img_url(v["thumb"], r) if v.get("thumb") else ""
    poster_html = f'<img src="{escape(poster)}" alt="Thumbnail: {escape(v["title"])}" loading="lazy">' if poster else '<div class="video-placeholder"><span>LENSA HUKUM TV</span></div>'
    if v.get("file"):
        media = f'<video controls preload="metadata" playsinline poster="{escape(poster)}"><source src="{escape(img_url(v["file"], r))}"></video>'
    elif v.get("embed"):
        media = f'<a class="video-embed" href="{escape(v["embed"])}" target="_blank" rel="noopener noreferrer">{poster_html}<span class="video-play">▶</span></a>'
    else:
        media = poster_html
    return f"""<article class="video-card" data-video-slug="{escape(v["slug"])}">
<div class="video-thumb">{media}</div>
<div class="video-copy"><span class="category">{escape(v["category"])}</span>
<h2>{escape(v["title"])}</h2><p>{escape(v["desc"])}</p>
<div class="meta"><time datetime="{escape(v["iso"])}">{escape(v["date"])}</time><span>{escape(v["author"])}</span></div>
{f'<p class="video-disclaimer">Sumber: {escape(v["source"])}</p>' if v.get("source") else ""}
</div></article>"""


def home_video_section(r):
    if not VIDEOS:
        return '<div class="section-head"><h2>Video Redaksi</h2><a href="video.html">Buka kanal video</a></div><div class="video-empty">Kanal video redaksi telah tersedia. Video liputan akan tampil di sini setelah wartawan mengunggah dan redaksi menerbitkannya.</div>'
    return '<div class="section-head"><h2>Video terbaru</h2><a href="video.html">Lihat semua video</a></div><div class="video-feature">' + "".join(video_card(v, r) for v in VIDEOS[:2]) + '</div>'



def load_epapers():
    items=[]
    for fp in sorted(glob.glob(os.path.join(ROOT,"content/epaper/*.json"))):
        d=json.load(open(fp,encoding="utf-8"))
        if d.get("status","draf")=="terbit":
            d["slug"]=os.path.splitext(os.path.basename(fp))[0]
            items.append(d)
    return sorted(items,key=lambda x:x.get("tanggal",""),reverse=True)


def make_epaper_pdf(issue, article_map):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
        from reportlab.lib.units import mm
    except ImportError:
        print("PERINGATAN: reportlab tidak tersedia; PDF dilewati.",file=sys.stderr); return None
    outdir=os.path.join(OUT,"epaper"); os.makedirs(outdir,exist_ok=True)
    filename="edisi-"+str(issue.get("nomor_edisi","001"))+".pdf"
    doc=SimpleDocTemplate(os.path.join(outdir,filename),pagesize=A4,rightMargin=19*mm,leftMargin=19*mm,topMargin=20*mm,bottomMargin=20*mm,title=issue.get("judul","E-Paper"))
    st=getSampleStyleSheet()
    st.add(ParagraphStyle(name="LHmast",parent=st["Title"],fontSize=22,leading=26,textColor=colors.HexColor("#c90024"),alignment=TA_CENTER,spaceAfter=12))
    st.add(ParagraphStyle(name="LHdeck",parent=st["Normal"],fontSize=10,leading=15,textColor=colors.grey,alignment=TA_CENTER,spaceAfter=14))
    st.add(ParagraphStyle(name="LHstory",parent=st["Heading2"],fontSize=14,leading=18,textColor=colors.HexColor("#171717"),spaceBefore=12,spaceAfter=5))
    st.add(ParagraphStyle(name="LHbody",parent=st["BodyText"],fontSize=9.5,leading=14,spaceAfter=7))
    story=[Spacer(1,25*mm),Paragraph("LENSA HUKUM BANYUWANGI",st["LHmast"]),Paragraph("E-PAPER • EDISI "+escape(str(issue.get("nomor_edisi","001"))),st["LHdeck"]),Paragraph(escape(issue.get("judul","Edisi Redaksi")),st["Heading1"]),Paragraph(escape(issue.get("tanggal","")),st["LHdeck"]),Paragraph(escape(issue.get("pengantar","")),st["LHbody"]),Spacer(1,8*mm),Paragraph("ISI EDISI",st["Heading2"])]
    for slug in issue.get("artikel",[]):
        a=article_map.get(slug)
        if a:
            story.append(KeepTogether([Paragraph(escape(a["title"]),st["LHstory"]),Paragraph(escape(a["excerpt"]),st["LHbody"]),Paragraph("Penulis: "+escape(a["author"])+" • "+escape(a["date"]),st["LHbody"])]))
    story.append(Spacer(1,10*mm)); story.append(Paragraph("Kompilasi artikel terbit LENSA HUKUM BANYUWANGI. Hak koreksi dan hak jawab dapat disampaikan melalui kanal kontak redaksi.",st["LHbody"]))
    def footer(canvas,doc):
        canvas.saveState(); canvas.setStrokeColor(colors.HexColor("#c90024")); canvas.line(19*mm,15*mm,191*mm,15*mm); canvas.setFont("Helvetica",8); canvas.setFillColor(colors.grey); canvas.drawString(19*mm,10*mm,"LENSA HUKUM BANYUWANGI"); canvas.drawRightString(191*mm,10*mm,str(doc.page)); canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return "epaper/"+filename


def epaper_pages():
    issues=load_epapers(); amap={a["slug"]:a for a in ARTICLES}; cards=[]
    for issue in issues:
        pdf=make_epaper_pdf(issue,amap)
        count=sum(1 for slug in issue.get("artikel",[]) if slug in amap)
        pdf_link='<a class="btn" href="'+pdf+'">Baca / Unduh PDF</a>' if pdf else '<p>PDF belum tersedia.</p>'
        cards.append('<article class="epaper-card"><div class="epaper-cover"><span>LENSA HUKUM</span><strong>E-PAPER</strong><small>EDISI '+escape(str(issue.get("nomor_edisi","")) )+'</small></div><div class="epaper-copy"><span class="category">EDISI '+escape(str(issue.get("nomor_edisi","")) )+'</span><h2>'+escape(issue.get("judul",""))+'</h2><p>'+escape(issue.get("pengantar",""))+'</p><div class="meta"><time>'+escape(issue.get("tanggal",""))+'</time><span>'+str(count)+' artikel</span></div>'+pdf_link+'</div></article>')
    if not cards: cards=['<p class="video-empty">Belum ada edisi E-Paper yang diterbitkan.</p>']
    body='<main id="isi" class="wrap"><header class="page-head"><h1>Arsip E-Paper</h1><p>Terbitan digital LENSA HUKUM BANYUWANGI.</p></header><section class="epaper-grid">'+''.join(cards)+'</section></main>'
    page("epaper.html",head("E-Paper | "+SITE,"Arsip edisi digital.","")+header("","epaper")+body+footer(""))
    dash='<main id="isi" class="wrap"><header class="page-head"><h1>Digital Newsroom</h1><p>Pusat kerja redaksi digital.</p></header><section class="newsroom-grid">'
    tiles=[("CMS Redaksi","admin/","Kelola naskah, draf, foto dan publikasi."),("Studio Video","studio-video.html","Potong dan kompres video."),("Kanal Video","video.html","Arsip video terbit."),("E-Paper","epaper.html","Terbitan digital dan arsip PDF."),("Live Streaming","live.html","Halaman siaran langsung."),("Pedoman Redaksi","redaksi.html","Standar verifikasi dan koreksi.")]
    for title,url,desc in tiles: dash+='<a class="newsroom-tile" href="'+url+'"><b>'+title+'</b><span>'+desc+'</span></a>'
    dash+='</section><div class="notice">Hak akses operasional mengikuti akun GitHub dan persetujuan editorial.</div></main>'
    page("newsroom.html",head("Digital Newsroom | "+SITE,"Pusat kerja redaksi.","")+header("","newsroom")+dash+footer(""))

def build():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    for f in ("style.css", "script.js"):
        shutil.copy(os.path.join(ROOT, f), OUT)
    for d in ("assets", "uploads", "admin"):
        if os.path.isdir(os.path.join(ROOT, d)):
            shutil.copytree(os.path.join(ROOT, d), os.path.join(OUT, d))

    idx = [dict(t=a["title"], u=a["url"], c=" / ".join(CAT_NAME[x] for x in a["cats"]), e=a["excerpt"]) for a in ARTICLES]
    page("data.js", "window.ARTICLES = " + json.dumps(idx, ensure_ascii=False) + ";\n")

    # Beranda
    r = ""
    pool = list(ARTICLES)
    hero = next((a for a in pool if a["utama"]), pool[0] if pool else None)
    if hero: pool.remove(hero)
    side, rest = pool[:2], pool[2:]
    if hero:
        hero_style = f' style="--hero-image: url(&quot;{escape(img_url(hero["img"], r))}&quot;)"' if hero.get("img") else ""
        hero_html = f"""<a class="hero" href="{hero['url']}"{hero_style}><div class="hero-copy"><span class="category">{escape(CAT_NAME[hero['cat']])}</span>
<h1>{escape(hero['title'])}</h1><p>{escape(hero['excerpt'])}</p></div>
<svg class="lens" viewBox="0 0 200 200" aria-hidden="true"><circle cx="100" cy="100" r="86" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="100" cy="100" r="58" fill="none" stroke="currentColor" stroke-width="2" opacity=".6"/><circle cx="100" cy="100" r="30" class="flame"/></svg></a>"""
    else:
        hero_html = '<div class="hero"><div class="hero-copy"><h1>Belum ada berita terbit</h1></div></div>'
    side_html = "".join(f'<a class="mini-hero" href="{a["url"]}"><span class="category">{escape(CAT_NAME[a["cat"]])}</span><h3>{escape(a["title"])}</h3></a>' for a in side)
    cards = "".join(card(a, r) for a in rest) or "<p>Belum ada berita lain.</p>"
    picks = [a for a in ARTICLES if a["pilihan"]][:5] or ARTICLES[:3]
    pick_html = "".join(f'<li><a href="{a["url"]}">{escape(a["title"])}<small>{escape(CAT_NAME[a["cat"]])}, {a["mins"]} menit baca</small></a></li>' for a in picks)
    tiles = "".join(f'<a href="kategori/{s}.html"><strong>{escape(n)}</strong><span>{escape(d)}</span></a>' for s, n, d in CATEGORIES[:4])
    body = f"""<main id="isi" class="wrap">
<section class="hero-grid" aria-label="Sorotan">{hero_html}<div class="side-feature">{side_html}</div></section>
<div class="section-head"><h2>Berita terbaru</h2><a href="kategori/{CATEGORIES[0][0]}.html">Lihat semua rubrik</a></div>
<div class="content-grid"><section class="cards" aria-label="Berita terbaru">{cards}</section>
<aside><div class="sidebar-box"><h3>Pilihan redaksi</h3><ol class="popular">{pick_html}</ol></div>
<div class="sidebar-box"><h3>Hubungi redaksi</h3><p>Kirim informasi, koreksi, atau hak jawab kepada redaksi.</p><a class="btn" href="kontak.html">Kontak redaksi</a></div></aside></div>
{home_video_section(r)}
<div class="epaper-home"><div><span class="category">TERBITAN DIGITAL</span><h2>Baca E-Paper LENSA HUKUM</h2><p>Rangkuman berita pilihan redaksi dalam format edisi PDF yang dapat dibaca dan disimpan.</p></div><a class="btn" href="epaper.html">Jelajahi E-Paper</a></div>
<div class="category-strip">{tiles}</div>
</main>
"""
    page("index.html", head(f"Beranda | {SITE}", "Lensa Hukum Banyuwangi: media informasi hukum, kriminal, pemerintahan, dan peristiwa.", r) + header(r, "home") + body + footer(r))

    # Kategori
    r = "../"
    for s, n, d in CATEGORIES:
        items = [a for a in ARTICLES if s in a["cats"]]
        grid = "".join(card(a, r) for a in items) or "<p>Belum ada berita pada rubrik ini.</p>"
        others = "".join(f'<li><a href="{r}kategori/{x}.html"{CUR if x == s else ""}>{escape(y)}</a></li>' for x, y, _ in CATEGORIES)
        body = f"""<main id="isi" class="wrap"><header class="page-head"><h1>{escape(n)}</h1><p>{escape(d)}</p></header>
<div class="content-grid"><section class="cards" aria-label="Berita {escape(n)}">{grid}</section>
<aside><div class="sidebar-box"><h3>Rubrik</h3><ul class="rubrik-list">{others}</ul></div></aside></div></main>
"""
        page(f"kategori/{s}.html", head(f"{n} | {SITE}", d or n, r) + header(r, s) + body + footer(r))

    # Artikel
    for a in ARTICLES:
        cats = " / ".join(CAT_NAME[c] for c in a["cats"])
        cover = f'<figure><img class="cover" src="{escape(img_url(a["img"], r))}" alt="{escape(a["alt"])}" width="1000" height="625"></figure>' if a["img"] else ""
        notice = f'<div class="notice">Catatan redaksi: {escape(a["note"])}</div>' if a["note"] else ""
        related = [x for x in ARTICLES if x is not a and set(x["cats"]) & set(a["cats"])][:2] or [x for x in ARTICLES if x is not a][:2]
        rel = "".join(f'<li><a href="{r}{x["url"]}">{escape(x["title"])}</a></li>' for x in related)
        relsec = f'<section class="related"><h2>Berita terkait</h2><ul>{rel}</ul></section>' if rel else ""
        ld = json.dumps({"@context": "https://schema.org", "@type": "NewsArticle", "headline": a["title"],
                         "datePublished": a["iso"], "author": {"@type": "Person" if a["author"] != "Redaksi" else "Organization", "name": a["author"]},
                         "publisher": {"@type": "Organization", "name": SITE}}, ensure_ascii=False).replace("</", "<\\/")
        extra = f'\n<script type="application/ld+json">{ld}</script>'
        body = f"""<main id="isi" class="wrap"><article class="article">
<nav class="crumbs" aria-label="Jejak"><a href="{r}index.html">Beranda</a><a href="{r}kategori/{a['cat']}.html">{escape(CAT_NAME[a['cat']])}</a></nav>
<span class="category">{escape(cats)}</span>
<h1>{escape(a['title'])}</h1>
<p class="lead">{escape(a['lead'])}</p>
<div class="meta"><span>{escape(a['author'])}</span><time datetime="{a['iso']}">{a['date']}</time><span>{a['mins']} menit baca</span></div>
{cover}{md(a['body'])}
<div class="article-tools"><button type="button" class="share-btn" data-share>Bagikan berita</button><button type="button" class="share-btn" data-copy-url>Salin tautan</button></div>
{f'<p class="source-note"><strong>Sumber/rujukan:</strong> {escape(a["source"])}</p>' if a.get("source") else ""}
{notice}{relsec}
</article></main>
"""
        page(a["url"], head(f"{a['title']} | {SITE}", a["lead"], r, extra) + header(r, a["cat"]) + body + footer(r))

    # Kanal video redaksi: hanya video berstatus terbit yang ditampilkan.
    video_cards = "".join(video_card(v, "") for v in VIDEOS)
    if not video_cards:
        video_cards = '<p class="video-empty">Belum ada video yang diterbitkan. Wartawan dapat menambahkan video melalui menu Video Redaksi di /admin.</p>'
    video_body = f"""<main id="isi" class="wrap">
<header class="page-head"><h1>Video Redaksi</h1><p>Dokumentasi video dan liputan audiovisual LENSA HUKUM BANYUWANGI.</p></header>
<section class="video-feature">{video_cards}</section>
<div class="notice">Video yang tampil di halaman ini telah melalui proses penyuntingan redaksi. Pastikan seluruh rekaman, musik, dan materi visual memiliki izin penggunaan.</div>
</main>"""
    page("video.html", head(f"Video Redaksi | {SITE}", "Kanal video resmi LENSA HUKUM BANYUWANGI.", "") + header("", "video") + video_body + footer(""))


    studio_html = """<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Studio Video Redaksi</title><link rel="stylesheet" href="style.css"><style>
.studio{max-width:900px;margin:30px auto;padding:20px}.studio-panel{border:1px solid #ddd;padding:18px;margin:16px 0}.studio label{display:block;font-weight:bold;margin:12px 0 5px}.studio input{max-width:100%}.studio video{width:100%;max-height:420px;background:#111}.studio button{padding:10px 16px;background:#c90024;color:#fff;border:0;margin:8px 6px 8px 0;font-weight:bold}.studio input[type=range]{width:100%}.studio small{color:#666}
</style></head><body><main class="studio"><h1>Studio Video Redaksi</h1><p>Alat bantu pemotongan dan kompresi ringan di browser. Hasilnya diunduh ke perangkat; unggah hasil akhir melalui <a href="admin/">CMS /admin → Video Redaksi</a>.</p>
<section class="studio-panel"><label>Pilih video dari HP/kamera</label><input id="file" type="file" accept="video/*"><video id="preview" controls playsinline></video>
<label>Mulai (detik)</label><input id="start" type="number" min="0" value="0" step="0.5">
<label>Akhir (detik)</label><input id="end" type="number" min="0" value="0" step="0.5">
<label>Resolusi maksimum</label><select id="width"><option value="1280">720p (lebar 1280)</option><option value="854">480p (lebar 854)</option><option value="640">360p (lebar 640)</option></select>
<label>Bitrate video</label><select id="rate"><option value="1800000">1,8 Mbps</option><option value="1000000">1 Mbps</option><option value="700000">700 Kbps</option></select>
<button id="process" disabled>Potong & kompres video</button><a id="download" hidden>Unduh hasil WebM</a><p id="status" role="status">Pilih video untuk memulai.</p><small>Memerlukan browser yang mendukung MediaRecorder dan captureStream. Hasil WebM dapat diunggah ke CMS. Uji pemutaran sebelum diterbitkan.</small></section>
<section class="studio-panel"><h2>Alur publikasi</h2><ol><li>Unduh hasil kompresi.</li><li>Buka CMS dan pilih Video Redaksi.</li><li>Isi judul, deskripsi, reporter, thumbnail, dan sumber/izin.</li><li>Simpan Draf untuk diperiksa editor; ubah ke Terbit setelah disetujui.</li></ol></section>
</main><script>
const file=document.getElementById('file'),v=document.getElementById('preview'),start=document.getElementById('start'),end=document.getElementById('end'),btn=document.getElementById('process'),status=document.getElementById('status'),dl=document.getElementById('download');
let sourceUrl='';
file.addEventListener('change',()=>{if(sourceUrl)URL.revokeObjectURL(sourceUrl);if(!file.files[0])return;sourceUrl=URL.createObjectURL(file.files[0]);v.src=sourceUrl;v.onloadedmetadata=()=>{start.max=v.duration;end.max=v.duration;end.value=v.duration;btn.disabled=false;status.textContent='Video siap. Tentukan titik awal dan akhir.';}});
btn.addEventListener('click',async()=>{try{
 if(!v.captureStream&&!v.mozCaptureStream)throw Error('Browser tidak mendukung captureStream. Gunakan Chrome Android terbaru atau unggah file asli melalui CMS.');
 const a=Number(start.value),b=Number(end.value);if(!(b>a&&b<=v.duration))throw Error('Rentang waktu tidak valid.');
 const streamFn=v.captureStream||v.mozCaptureStream;const stream=streamFn.call(v);
 const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d'),maxW=Number(document.getElementById('width').value),scale=Math.min(1,maxW/v.videoWidth);
 canvas.width=Math.round(v.videoWidth*scale/2)*2;canvas.height=Math.round(v.videoHeight*scale/2)*2;
 const canvasStream=canvas.captureStream(24);stream.getAudioTracks().forEach(t=>canvasStream.addTrack(t));
 const mime=['video/webm;codecs=vp9,opus','video/webm;codecs=vp8,opus','video/webm'].find(t=>MediaRecorder.isTypeSupported(t));
 if(!mime)throw Error('Format WebM tidak didukung browser ini.');
 const rec=new MediaRecorder(canvasStream,{mimeType:mime,videoBitsPerSecond:Number(document.getElementById('rate').value)}),chunks=[];
 rec.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};
 const done=new Promise(resolve=>rec.onstop=resolve);
 v.pause();v.currentTime=a;await new Promise(resolve=>v.onseeked=resolve);
 rec.start(500);status.textContent='Memproses video… jangan tutup halaman.';
 await v.play();
 const draw=()=>{if(!v.paused&&!v.ended){ctx.drawImage(v,0,0,canvas.width,canvas.height);requestAnimationFrame(draw);}};draw();
 await new Promise(resolve=>{const tick=()=>{if(v.currentTime>=b||v.ended){v.pause();resolve();}else requestAnimationFrame(tick);};tick();});
 rec.stop();await done;canvasStream.getTracks().forEach(t=>t.stop());
 const blob=new Blob(chunks,{type:mime}),url=URL.createObjectURL(blob);dl.href=url;dl.download=(file.files[0].name.replace(/\\.[^.]+$/,'')+'-edit.webm');dl.hidden=false;dl.textContent='Unduh hasil ('+(blob.size/1024/1024).toFixed(1)+' MB)';status.textContent='Selesai. Periksa hasil, unduh, lalu unggah melalui CMS.';
 }catch(e){status.textContent='Tidak dapat memproses: '+e.message;}});
</script></body></html>"""
    page("studio-video.html", studio_html)
    # Live streaming page, configured by editors through CMS file collection.
    live = load("content/pengaturan/live.json")
    live_html = ""
    if live.get("status") == "terbit" and live.get("url_embed"):
        u = live["url_embed"].strip()
        # Only permit known embeddable providers to prevent arbitrary iframe injection.
        allowed = ("https://www.youtube.com/embed/", "https://www.youtube-nocookie.com/embed/", "https://www.facebook.com/plugins/video.php")
        if u.startswith(allowed):
            live_html = f'<div class="live-frame"><iframe src="{escape(u)}" title="Siaran langsung LENSA HUKUM BANYUWANGI" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe></div>'
        else:
            live_html = '<div class="notice">URL siaran belum menggunakan format embed YouTube/Facebook yang didukung.</div>'
    else:
        live_html = '<div class="video-empty">Belum ada siaran langsung terjadwal. Informasi siaran akan diumumkan oleh redaksi.</div>'
    live_title = escape(live.get("judul") or "Live LENSA HUKUM BANYUWANGI")
    live_desc = escape(live.get("deskripsi") or "Siaran langsung konferensi pers dan kegiatan publik.")
    live_body = f'<main id="isi" class="wrap"><header class="page-head"><h1>{live_title}</h1><p>{live_desc}</p></header>{live_html}<div class="notice">Siaran hanya dilakukan setelah redaksi memastikan izin perekaman/penayangan, aturan tempat, privasi pihak terkait, dan ketentuan persidangan. Jangan menyiarkan pemeriksaan tertutup atau materi yang dilarang untuk dipublikasikan.</div></main>'
    page("live.html", head(f"Live Streaming | {SITE}", live_desc, "") + header("", "live") + live_body + footer(""))

    epaper_pages()
    for key in ("tentang", "redaksi", "kontak"):
        static_page(f"{key}.html", key, key)

    page("cari.html", head(f"Cari Berita | {SITE}", "Pencarian berita.", "") + header("", "") +
         '<main id="isi" class="wrap"><header class="page-head"><h1>Hasil pencarian</h1><p id="cari-ket">Memuat…</p></header><div class="cards single" id="cari-hasil"></div></main>\n' + footer(""))
    page("404.html", head(f"Halaman tidak ditemukan | {SITE}", "Halaman tidak ditemukan.", "/") + header("/", "") +
         '<main id="isi" class="wrap"><article class="article"><h1>Halaman tidak ditemukan</h1><p class="lead">Alamat yang Anda buka tidak tersedia atau sudah dipindahkan.</p><p><a class="btn" href="/index.html">Kembali ke beranda</a></p></article></main>\n' + footer("/"))
    # Sitemap, RSS, dan robots untuk kebutuhan indeks mesin pencari.
    base = (S.get("site_url") or "").rstrip("/")
    urls = ["index.html", "tentang.html", "redaksi.html", "kontak.html", "video.html", "live.html", "epaper.html", "newsroom.html"] + [f"kategori/{slug}.html" for slug, _, _ in CATEGORIES] + [a["url"] for a in ARTICLES]
    locs = "".join(f"<url><loc>{escape(base + '/' + u if base else u)}</loc></url>" for u in urls)
    page("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + locs + "</urlset>")
    rss_items = "".join(f"<item><title>{escape(a['title'])}</title><link>{escape(base + '/' + a['url'] if base else a['url'])}</link><guid>{escape(base + '/' + a['url'] if base else a['url'])}</guid><description>{escape(a['excerpt'])}</description></item>" for a in ARTICLES[:30])
    page("feed.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>' + escape(SITE) + '</title><description>Berita hukum dan peristiwa</description><link>' + escape(base) + '</link>' + rss_items + '</channel></rss>')
    page("robots.txt", "User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: " + (base + "/sitemap.xml" if base else "/sitemap.xml") + "\n")
    print(f"Selesai: {len(ARTICLES)} berita terbit, {len(CATEGORIES)} rubrik -> {OUT}")


if __name__ == "__main__":
    build()
