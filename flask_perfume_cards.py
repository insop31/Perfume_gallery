from flask import Flask, render_template_string, request, url_for
import os
import pandas as pd

app = Flask(__name__)

# Try to load perfumes from CSV. The app will look for these filenames (in this order):
# 1) "perfume list - Sheet1.csv" (the exact name you uploaded)
# 2) "perfumes.csv"
# 3) "perfume_list.csv"
# If neither exists, the app falls back to an internal sample list.
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

    # Expecting columns: name, code. We'll create an "inspired_by" column equal to name
    # and assume image filename is <code>.jpg (you can change images or filenames in static/images)
    perfumes = []
    for _, row in df.iterrows():
        name = str(row.get('name', '')).strip()
        code = str(row.get('code', '')).strip()
        if not name or not code:
            continue
        perfumes.append({
            'name': name,
            'code': code,
            'inspired_by': name,  # per your request: "inspired by" filled with the name column
            'image': f"{code}.jpg",
        })
    return perfumes

# Load at startup
loaded = load_perfumes_from_csv()
if loaded:
    PERFUMES = loaded
else:
    # Fallback sample data
    PERFUMES = [
        {"code": "DS-103", "name": "Dior Sauvage", "inspired_by": "Dior Sauvage", "image": "DS-103.jpg"},
        {"code": "DOI-67", "name": "Dior Oud Ispahan", "inspired_by": "Dior Oud Ispahan", "image": "DOI-67.jpg"},
        {"code": "DF-11", "name": "Dior Fahrenheit", "inspired_by": "Dior Fahrenheit", "image": "DF-11.jpg"},
    ]

# Final refined UI: uniform card sizes + consistent spacing
TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Perfume Codes — Gallery</title>

    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">

    <!-- Bootstrap (for minimal helpers only) -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>
      :root{
        --bg-start: #FDEBD0;
        --bg-end: #FDEBD0 ;
        --accent-deep: #FDEBD0; /* primary */
        --accent-mid: #FDEBD0;  /* secondary */
        --muted: #6b6b7a;
        --navy: #0b2545;
        --card-radius: 16px;
        --container-max: 1200px;
        --card-min-width: 260px;
        --card-media-height: 200px; /* fixed media height for uniformity */
        --card-total-height: 360px; /* total card height for strict uniformity */
        --card-gap: 22px;
      }

      html,body{height:100%}
      body{
        margin:0; font-family:'Montserrat',system-ui,-apple-system,'Segoe UI',Roboto,Arial;color:var(--navy);
        background: linear-gradient(180deg, #FDEBD0 0%, #F7CAC9 100%);
        -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale; overflow-y:auto;
      }

      .page-wrap{max-width:var(--container-max); margin:28px auto; padding:18px; position:relative}

      /* header */
      .site-header{display:flex;align-items:center;gap:18px;padding:12px 0;background:transparent;margin-bottom:8px}
      .logo{width:54px;height:54px;border-radius:12px;display:grid;place-items:center;font-weight:700;color:white;background:#DC143C;box-shadow:0 10px 30px rgba(11,37,69,0.08)}
      .brand{font-family:'Playfair Display',serif;font-size:1.35rem;color:var(--navy);line-height:1}

      /* search area */
      .search-row{display:flex;gap:12px;align-items:center;width:100%}
      .search-input{border-radius:999px;padding:10px 14px;border:none;box-shadow:0 8px 20px rgba(20,30,60,0.06);width:100%;min-width:220px}
      .search-btn{border-radius:999px;padding:10px 14px;background:#DC143C;border:none;color:white}

      .top-row{display:flex;justify-content:space-between;align-items:center;margin-top:12px;margin-bottom:18px;gap:12px}
      .top-left h2{font-family:'Playfair Display',serif;margin:0;font-weight:700}
      .top-left p{margin:6px 0 0;color:var(--muted)}

      /* GRID: uniform columns and gaps */
      .card-stage{perspective:1000px}
      .card-grid{
        display:grid;
        grid-template-columns: repeat(auto-fill, minmax(var(--card-min-width), 1fr));
        gap: var(--card-gap);
        align-items:stretch;
      }

      /* Each card is a fixed-height flexible box so all cards are equal size */
      .perfume-card{
        height:var(--card-total-height);
        display:flex;
        align-items:stretch;
        justify-content:stretch;
      }

      .card-core{
        background: #ffffff;
        border-radius:calc(var(--card-radius));
        padding:0;
        width:100%;
        display:flex;
        flex-direction:column;
        overflow:hidden;
        box-shadow: 0 14px 30px rgba(11,37,69,0.06);
        transition:transform .32s cubic-bezier(.2,.9,.2,1), box-shadow .32s;
      }

      /* hover 3D lift */
      .perfume-card:hover .card-core{transform: translateY(-10px) translateZ(12px); box-shadow: 0 28px 60px rgba(11,37,69,0.12)}

      /* fixed media area */
      .card-media{
        height:var(--card-media-height);
        flex:0 0 var(--card-media-height);
        display:flex;align-items:center;justify-content:center;
        background:#FFF8F5;
      }

      .card-media img{max-height:calc(var(--card-media-height) - 20px); width:auto; object-fit:contain; display:block}

      .card-body{
        padding:12px 14px;
        display:flex;flex-direction:column;justify-content:space-between;flex:1 1 auto;
      }

      .title-wrap{min-height:56px} /* reserve space for title to keep body consistent */
      .perfume-title{font-weight:700; font-size:1.02rem; margin:0; color:var(--navy); line-height:1.2; display:block; overflow:hidden; text-overflow:ellipsis;}
      .inspired{color:var(--muted); font-style:italic; margin:6px 0 0}

      .code-row{display:flex;gap:8px;align-items:center;justify-content:space-between;margin-top:8px}
      .perfume-code{display:inline-block;padding:6px 10px;border-radius:12px;background:#FFF8F5;box-shadow: 0 6px 18px rgba(20,20,60,0.04); font-weight:600}

      .actions{display:flex;gap:8px;align-items:center}
      .btn-view{padding:8px 12px;border-radius:10px;font-weight:600;background:#DC143C;color:white;border:none;}

      .card-reflection{position:relative; height:12px; margin-top:-6px; filter:blur(10px); background:#FFF8F5; opacity:0.7}

      /* responsive tweaks */
      @media (max-width:900px){
        :root{--card-total-height:360px; --card-media-height:190px}
      }
      @media (max-width:600px){
        .page-wrap{padding:12px}
        :root{--card-total-height:340px; --card-media-height:170px; --card-gap:16px}
        .search-row{flex-direction:row}
      }

      /* detail page */
      .detail-card{border-radius:14px; padding:18px; box-shadow:0 20px 50px rgba(11,37,69,0.07)}

    </style>
  </head>
  <body>
    <div class="page-wrap">
      <div class="site-header">
        <div class="d-flex align-items-center gap-3">
          <div class="logo">P</div>
          <div>
            <div class="brand">Perfume Codes</div>
            <div style="color:var(--muted);font-size:0.9rem">A neat, uniform gallery — hover cards to lift.</div>
          </div>
        </div>

        <div style="flex:1"></div>

        <form class="search-row" role="search" method="get" action="/" style="max-width:520px;min-width:200px">
          <input name="q" class="form-control search-input" type="search" placeholder="Search by name or code — e.g. 'Versace' or 'VD-105'" aria-label="Search" value="{{ q|e }}">
          <button class="btn search-btn" type="submit">Search</button>
        </form>
      </div>

      <div class="top-row">
        <div class="top-left">
          <h2>Your Collection</h2>
          <p>Cards are now uniform in size and spacing. Click the card or the "View" button for details.</p>
        </div>
        <div style="color:var(--muted);font-size:0.95rem">{{ perfumes|length }} items</div>
      </div>

      <div class="card-stage">
        <div class="card-grid">
          {% for p in perfumes %}
            <div class="perfume-card" data-code="{{ p.code }}">
              <div class="card-core">
                <div class="card-media">
                  {% if p.image_exists %}
                    <img src="{{ url_for('static', filename='images/' + p.image) }}" alt="{{ p.name }}">
                  {% else %}
                    <svg width="120" height="160" viewBox="0 0 120 180" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <rect x="10" y="40" width="100" height="110" rx="14" fill="#fff" stroke="#f0e6fa"/>
                      <rect x="34" y="18" width="52" height="32" rx="8" fill="#fff" stroke="#f6f0ff"/>
                      <circle cx="60" cy="95" r="26" fill="#f7f3ff" />
                    </svg>
                  {% endif %}
                </div>

                <div class="card-body">
                  <div>
                    <div class="title-wrap">
                      <div class="perfume-title">{{ p.name }}</div>
                      <p class="inspired">Inspired by <strong>{{ p.inspired_by }}</strong></p>
                    </div>
                  </div>

                  <div class="code-row">
                    <div class="perfume-code">{{ p.code }}</div>
                    <div class="actions">
                      <a href="{{ url_for('perfume_detail', code=p.code) }}" class="btn btn-view">View</a>
                    </div>
                  </div>
                </div>

              </div>
            </div>
          {% else %}
            <div class="col-12">
              <div class="alert alert-warning">No perfumes found.</div>
            </div>
          {% endfor %}
        </div>
      </div>

      <div class="mt-5 text-center" style="color:var(--muted)">
        Tip: put images in <code>static/images/</code> named as the code (e.g. <code>VD-105.jpg</code>). Placeholders are used when missing.
      </div>
    </div>

    <script>
      // 3D tilt effect and full-card click navigation
      document.querySelectorAll('.perfume-card').forEach(card => {
        const core = card.querySelector('.card-core');
        const mediaImg = card.querySelector('.card-media img');
        const link = card.querySelector('a');

        function handleMove(e){
          const rect = card.getBoundingClientRect();
          const x = (e.clientX - rect.left) / rect.width; // 0..1
          const y = (e.clientY - rect.top) / rect.height; // 0..1

          const rotateY = (x - 0.5) * 12;
          const rotateX = (0.5 - y) * 8;

          core.style.transform = `translateY(-6px) translateZ(20px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
          if(mediaImg) mediaImg.style.transform = `translateZ(48px) scale(1.03) rotateY(${rotateY/6}deg)`;
        }

        function handleLeave(){
          core.style.transform = '';
          if(mediaImg) mediaImg.style.transform = '';
        }

        card.addEventListener('click', function(e){
          if(link && !e.target.closest('a')){
            window.location = link.href;
          }
        });

        card.addEventListener('mousemove', handleMove);
        card.addEventListener('touchmove', function(ev){ if(ev.touches && ev.touches[0]) handleMove(ev.touches[0]); }, {passive:true});
        card.addEventListener('mouseleave', handleLeave);
        card.addEventListener('touchend', handleLeave);
      });
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
    <title>{{ perfume.name }} — Details</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      :root{--bg-start:#FDEBD0;--bg-end:#F7CAC9}
      body{font-family:'Montserrat',sans-serif;background:#FFF8F5;} 
      .container{padding-top:28px}
      .card{border-radius:14px}
      .perfume-image{max-height:520px; object-fit:contain}
      .brand{font-family:'Playfair Display',serif}
      .detail-stage{perspective:1000px}
      .detail-core{transform-style:preserve-3d; transition:transform .35s}
      .detail-core:hover{transform:translateZ(16px) rotateX(2deg)}
    </style>
  </head>
  <body>
    <div class="container">
      <a href="/" class="btn btn-link mb-3">← Back</a>
      <div class="card detail-card p-3 detail-stage">
        <div class="row g-0 align-items-center">
          <div class="col-md-6 text-center">
            <div class="detail-core">
              {% if perfume.image_exists %}
                <img src="{{ url_for('static', filename='images/' + perfume.image) }}" class="img-fluid rounded perfume-image" alt="{{ perfume.name }}">
              {% else %}
                <div style="height:420px;display:flex;align-items:center;justify-content:center;background:#FFF8F5;border-radius:12px;">
                  <svg width="200" height="280" viewBox="0 0 120 180" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="10" y="40" width="100" height="110" rx="14" fill="#fff" stroke="#f0e6fa"/>
                    <rect x="34" y="18" width="52" height="32" rx="8" fill="#fff" stroke="#f6f0ff"/>
                    <circle cx="60" cy="95" r="26" fill="#f7f3ff" />
                  </svg>
                </div>
              {% endif %}
            </div>
          </div>
          <div class="col-md-6">
            <div class="card-body">
              <h2 class="brand">{{ perfume.code }}</h2>
              <p class="text-muted">Code: <strong>{{ perfume.code }}</strong></p>
              <h5>Inspired by</h5><p>{{ perfume.name }}</p></p>
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

    # Prepare a working copy and normalize
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
    # accept path converter to allow codes with special characters
    match = next((p.copy() for p in PERFUMES if str(p['code']).strip().lower() == code.strip().lower()), None)
    if not match:
        return "Perfume not found", 404
    match['image_exists'] = image_exists(match.get('image', f"{match['code']}.jpg"))
    match['inspired_by'] = match.get('inspired_by', match['name'])
    return render_template_string(DETAIL_TEMPLATE, perfume=match)


if __name__ == '__main__':
    # Create static/images directory if it does not exist so users know where to put files
    os.makedirs(os.path.join('static', 'images'), exist_ok=True)
    app.run(debug=True)
