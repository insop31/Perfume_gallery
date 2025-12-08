from flask import Flask, render_template_string, request, url_for
import os
import pandas as pd

app = Flask(__name__)

# CSV file candidates
CSV_CANDIDATES = ["perfume list - Sheet1.csv", "perfumes.csv", "perfume_list.csv"]
PERFUMES = []

def load_perfumes_from_csv():
    df = None
    for f in CSV_CANDIDATES:
        if os.path.exists(f):
            try:
                df = pd.read_csv(f)
                print(f"Loaded perfume data from {f}")
                break
            except Exception as e:
                print(f"Failed to read {f}: {e}")
                df = None
    if df is None:
        return None

    perfumes = []
    for _, row in df.iterrows():
        name = str(row.get('name', '')).strip()
        code = str(row.get('code', '')).strip()
        if not name or not code:
            continue
        perfumes.append({
            'name': name,
            'code': code,
            'inspired_by': name,
            'image': f"{code}.jpg",
        })
    return perfumes

loaded = load_perfumes_from_csv()
if loaded:
    PERFUMES = loaded
else:
    PERFUMES = [
        {"code": "DS-103", "name": "Dior Sauvage", "inspired_by": "Dior Sauvage", "image": "DS-103.jpg"},
        {"code": "DOI-67", "name": "Dior Oud Ispahan", "inspired_by": "Dior Oud Ispahan", "image": "DOI-67.jpg"},
        {"code": "DF-11", "name": "Dior Fahrenheit", "inspired_by": "Dior Fahrenheit", "image": "DF-11.jpg"},
    ]

# NOTE:
# The gradient is applied to the HTML element (fixed, cover) and body is transparent.
# This makes the background feel like one continuous panel across navigation.

TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Perfume Codes — Mobile Friendly</title>

    <!-- Fonts & Bootstrap -->
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>
      /* universal */
      *, *::before, *::after { box-sizing: border-box; }
      :root{
        --bg-start: #FCF5EE;
        --bg-mid1: #FFC4C4;
        --bg-mid2: #EE6983;
        --bg-end: #850E35;
        --accent-deep: #DC143C;
        --accent-mid: #F75270;
        --muted: #6b6b7a;
        --navy: #0b2545;
        --card-radius: 12px;
        --container-max: 1000px;
        --gap: 16px;
      }

      /* Put the site-wide gradient on html; keep it fixed and cover the viewport.
         Body is made transparent so html's background shows through uniformly. */
      html {
        height: 100%;
        background: linear-gradient(180deg, var(--bg-start) 0%, var(--bg-mid1) 33%, var(--bg-mid2) 66%, var(--bg-end) 100%);
        background-attachment: fixed;
        background-size: cover;
        background-repeat: no-repeat;
      }
      body{
        margin:0;
        height: 100%;
        font-family: 'Montserrat', system-ui, -apple-system, 'Segoe UI', Roboto, Arial;
        color:var(--navy);
        background: transparent; /* let html background show through */
        -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale;
        line-height:1.35;
      }

      a { text-decoration:none; color:inherit; }

      /* wrapper */
      .page-wrap{
        max-width:var(--container-max);
        margin:0 auto;
        padding:14px;
      }

      /* Header — mobile-first stacked layout */
      .site-header{
        display:flex;
        flex-direction:column;
        gap:10px;
        align-items:flex-start;
        padding:6px 4px 12px;
      }
      .header-top{
        display:flex;
        width:100%;
        gap:12px;
        align-items:center;
      }
      .logo{
        width:100px;
        height:100px;
        border-radius:12px;
        display:flex;
        align-items:left;
        justify-content:center;
        background:var(--accent-deep);
        color:white;
        font-weight:700;
        box-shadow:0 6px 20px rgba(11,37,69,0.06);
        flex-shrink:0;
      }
      .logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius:12px;

}
      .brand-block{
        display:flex;
        flex-direction:column;
        gap:2px;
      }
      .brand{
        font-family:'Playfair Display', serif;
        font-size:1.05rem;
        margin:0;
        color:var(--navy);
        font-weight:700;
      }
      .brand-sub{
        margin:0;
        color:var(--muted);
        font-size:0.85rem;
      }

      /* Search - full width on mobile */
      .search-row{
        display:flex;
        gap:8px;
        width:100%;
      }
      .search-input{
        flex:1 1 auto;
        padding:10px 14px;
        border-radius:999px;
        border:0;
        box-shadow:0 6px 18px rgba(20,20,40,0.05);
        font-size:15px;
      }
      .search-btn{
        padding:10px 14px;
        border-radius:999px;
        border:0;
        background:var(--accent-deep);
        color:white;
        font-weight:600;
      }

      /* Top info row */
      .top-row{
        display:flex;
        justify-content:space-between;
        align-items:center;
        gap:12px;
        margin-top:6px;
        margin-bottom:6px;
      }
      .top-left h2{margin:0;font-family:'Playfair Display',serif;font-size:1.15rem;}
      .top-left p{margin:4px 0 0;color:var(--muted);font-size:0.9rem;}

      /* Grid: single column on small screens, multi on wider */
      .card-grid{
        display:grid;
        grid-template-columns: 1fr;
        gap:var(--gap);
        margin-top:10px;
      }

      /* Card */
      .perfume-card{
        background:#fff;
        border-radius:var(--card-radius);
        overflow:hidden;
        display:flex;
        flex-direction:column;
        box-shadow:0 10px 26px rgba(11,37,69,0.06);
      }

      .card-media{
        width:100%;
        background:#FFF8F5;
        display:flex;
        align-items:center;
        justify-content:center;
        padding:14px;
      }
      .card-media img{max-width:100%;max-height:200px;height:auto;display:block;object-fit:contain}

      .card-body{
        padding:12px 14px;
        display:flex;
        flex-direction:column;
        gap:10px;
      }
      .title-wrap{min-height:48px}
      .perfume-title{margin:0;font-weight:700;font-size:1rem;color:var(--navy);line-height:1.2}
      .inspired{margin:0;color:var(--muted);font-style:italic;font-size:0.95rem}

      .code-row{
        display:flex;
        gap:10px;
        align-items:center;
        justify-content:space-between;
        width:100%;
      }
      .perfume-code{
        background:#FFF8F5;
        padding:8px 10px;
        border-radius:10px;
        font-weight:700;
        color:var(--navy);
        box-shadow:0 6px 14px rgba(20,20,40,0.04);
        font-size:0.95rem;
      }

      /* VIEW button: full width on mobile, inline on bigger screens */
      .actions{display:flex;align-items:center;gap:8px}
      .btn-view{
        background:var(--accent-deep);
        color:white;
        border:0;
        padding:10px 14px;
        border-radius:10px;
        font-weight:700;
        font-size:0.95rem;
      }

      /* Ensure view button not clipped — make it expand when needed */
      .btn-view.stretch{
        width:100%;
      }

      /* Footer tip */
      .tip{color:var(--muted);font-size:0.9rem;text-align:center;margin-top:12px}

      /* Desktop / wider screens: 2 or 3 columns, keep nice gaps */
      @media (min-width:560px){
        .card-grid{grid-template-columns: repeat(2, 1fr);}
      }
      @media (min-width:920px){
        .card-grid{grid-template-columns: repeat(3, 1fr);}
      }

      /* Bigger screens: header inline */
      @media (min-width:700px){
        .site-header{flex-direction:row;align-items:center;justify-content:space-between;padding:10px 6px}
        .header-top{gap:16px}
        .brand{font-size:1.2rem}
      }

      /* Mobile polish: ensure spacing and tap targets */
      @media (max-width:520px){
        .page-wrap{padding:12px}
        .logo{width:42px;height:42px}
        .brand{font-size:1rem}
        .perfume-title{font-size:1rem}
        .inspired{font-size:0.92rem}
        .btn-view{padding:12px 14px;font-size:16px}
        .btn-view.stretch{display:block}
        .code-row{flex-direction:column;align-items:stretch;gap:8px}
      }
    </style>
  </head>
  <body>
    <div class="page-wrap">
      <header class="site-header">
        <div class="header-top">
          <div class="logo">
  <img src="{{ url_for('static', filename='logo/mybrand.jpg') }}" alt="Logo" class="logo-img">
</div>
          <div class="brand-block">
            <p class="brand" style="color:#BF124D;margin:0;font-size:3rem;font-weight:800">Ali Al Attar Perfumes Trading</p>
            <p class="brand-sub">Perfume store in Ajman, United Arab Emirates</p>
          </div>
        </div>

        <form class="search-row" role="search" method="get" action="/">
          <input name="q" class="search-input" type="search" placeholder="Search by name or code" aria-label="Search" value="{{ q|e }}">
          <button class="search-btn" type="submit">Search</button>
        </form>
      </header>

      <div class="top-row">
        <div class="top-left">
          <h2 style="margin:0;font-size:3rem">Perfumes Catalogue</h2>
          <p style="margin:6px 0 0;color:var(--muted)">Click the card or tap <strong>View</strong> for details.</p>
        </div>
        <div style="color:var(--muted);font-size:0.95rem">{{ perfumes|length }} items</div>
      </div>

      <main class="card-stage">
        <div class="card-grid">
          {% for p in perfumes %}
            <article class="perfume-card" data-code="{{ p.code }}">
              <div class="card-media">
                {% if p.image_exists %}
                  <img src="{{ url_for('static', filename='images/' + p.image) }}" alt="{{ p.name }}">
                {% else %}
                  <!-- placeholder -->
                  <svg width="120" height="160" viewBox="0 0 120 180" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    <rect x="10" y="40" width="100" height="110" rx="14" fill="#fff" stroke="#f0e6fa"/>
                    <rect x="34" y="18" width="52" height="32" rx="8" fill="#fff" stroke="#f6f0ff"/>
                    <circle cx="60" cy="95" r="26" fill="#f7f3ff" />
                  </svg>
                {% endif %}
              </div>

              <div class="card-body">
                <div class="title-wrap">
                  <h3 class="perfume-title">{{ p.name }}</h3>
                  <p class="inspired">Inspired by <strong>{{ p.inspired_by }}</strong></p>
                </div>

                <div class="code-row">
                  <div class="perfume-code">{{ p.code }}</div>
                  <div class="actions">
                    <!-- button gets 'stretch' class via JS on small screens to ensure full width -->
                    <a href="{{ url_for('perfume_detail', code=p.code) }}" class="btn-view" role="button">View</a>
                  </div>
                </div>
              </div>
            </article>
          {% else %}
            <div class="alert alert-warning">No perfumes found.</div>
          {% endfor %}
        </div>
      </main>

    </div>

    <script>
      // mobility helpers:
      // 1) remove 3D/tilt interactions on touch devices
      // 2) ensure the View button becomes full-width on narrow screens

      function applyMobileButtonBehavior(){
        const isNarrow = window.matchMedia('(max-width:520px)').matches;
        document.querySelectorAll('.btn-view').forEach(btn=>{
          if(isNarrow){
            btn.classList.add('stretch');
          } else {
            btn.classList.remove('stretch');
          }
        });
      }

      // run on load and on resize (debounced)
      applyMobileButtonBehavior();
      let resizeTimer;
      window.addEventListener('resize', ()=>{
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(applyMobileButtonBehavior, 120);
      });

      // Make whole card tappable on touch devices: if user taps card outside the button, follow the View link.
      if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
        document.querySelectorAll('.perfume-card').forEach(card=>{
          card.addEventListener('click', function(e){
            // if tapping a link/button inside, do nothing (let it handle)
            if(e.target.closest('a, button')) return;
            const a = card.querySelector('a');
            if(a) window.location = a.href;
          });
        });
      }
    </script>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
"""

DETAIL_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ perfume.code }} — Details</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      :root{
        --bg-start: #FCF5EE;
        --bg-mid1: #FFC4C4;
        --bg-mid2: #EE6983;
        --bg-end: #850E35;
        --navy: #0b2545;
      }

      /* Same single gradient on html, body transparent */
      html {
        height: 100%;
        background: linear-gradient(180deg, var(--bg-start) 0%, var(--bg-mid1) 33%, var(--bg-mid2) 66%, var(--bg-end) 100%);
        background-attachment: fixed;
        background-size: cover;
        background-repeat: no-repeat;
      }
      body{
        margin:0;
        height:100%;
        font-family:'Montserrat',sans-serif;
        background: transparent;
        color:var(--navy);
      }

      .container{padding:14px; max-width:900px; margin:0 auto}
      .card{border-radius:12px}
      .perfume-image{max-width:100%;height:auto;display:block}
      .brand{font-family:'Playfair Display',serif}
      @media (max-width:520px){
        .container{padding:10px}
        .perfume-image{max-height:320px}
      }
    </style>
  </head>
  <body>
    <div class="container">
      <a href="/" class="btn btn-link mb-3">← Back</a>
      <div class="card p-3">
        <div class="row g-0 align-items-center">
          <div class="col-12 col-md-6 mb-3 mb-md-0 text-center">
            {% if perfume.image_exists %}
              <img src="{{ url_for('static', filename='images/' + perfume.image) }}" class="perfume-image rounded" alt="{{ perfume.name }}">
            {% else %}
              <div style="height:260px;display:flex;align-items:center;justify-content:center;background:#FFF8F5;border-radius:12px;">
                <svg width="140" height="180" viewBox="0 0 120 180" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <rect x="10" y="40" width="100" height="110" rx="14" fill="#fff" stroke="#f0e6fa"/>
                  <rect x="34" y="18" width="52" height="32" rx="8" fill="#fff" stroke="#f6f0ff"/>
                  <circle cx="60" cy="95" r="26" fill="#f7f3ff" />
                </svg>
              </div>
            {% endif %}
          </div>

          <div class="col-12 col-md-6">
            <div style="padding:8px 12px">
              <h2 class="brand" style="margin-top:0">{{ perfume.code }}</h2>
              <p class="text-muted" style="margin:6px 0;">Code: <strong>{{ perfume.code }}</strong></p>
              <h5 style="margin:10px 0 6px">Inspired by</h5>
              <p style="margin:0">{{ perfume.name }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </body>
</html>
"""

def image_exists(filename: str) -> bool:
    path = os.path.join(app.static_folder or 'static', 'images', filename)
    return os.path.exists(path)

@app.route('/')
def index():
    q = request.args.get('q', '') or ''
    q_lower = q.strip().lower()

    working = [p.copy() for p in PERFUMES]
    for p in working:
        p['code'] = str(p['code']).strip()
        p['name'] = str(p['name']).strip()
        p['inspired_by'] = str(p.get('inspired_by', p['name']))
        p['image_exists'] = image_exists(p.get('image', f"{p['code']}.jpg"))

    if q_lower:
        filtered = [p for p in working if q_lower in p['name'].lower() or q_lower in p['code'].lower()]
    else:
        filtered = working

    return render_template_string(TEMPLATE, perfumes=filtered, q=q)

@app.route('/perfume/<path:code>')
def perfume_detail(code):
    match = next((p.copy() for p in PERFUMES if str(p['code']).strip().lower() == code.strip().lower()), None)
    if not match:
        return "Perfume not found", 404
    match['image_exists'] = image_exists(match.get('image', f"{match['code']}.jpg"))
    match['inspired_by'] = match.get('inspired_by', match['name'])
    return render_template_string(DETAIL_TEMPLATE, perfume=match)

if __name__ == '__main__':
    os.makedirs(os.path.join('static', 'images'), exist_ok=True)
    os.makedirs(os.path.join('static', 'logo'), exist_ok=True)
    app.run(debug=True)
