#!/usr/bin/env python3
"""
Render a pack of shareable cards from a JSON spec.

Usage:
    python3 render_cards.py SPEC.json OUT_DIR [--html-only]

Prints exactly one JSON object on stdout and exits with:
    0  status "ok"             PNGs written (plus cards.zip for 2+ cards, cards.pdf when make_pdf)
    2  status "html_fallback"  no usable Playwright, Pillow or browser; OUT_DIR/cards.html written
                               (exit 0 with reason "html_requested" when --html-only was passed)
    1  status "error"          bad spec or arguments; nothing rendered

Spec (see references/design-presets.md and references/aspect-ratios.md):
{
  "aspect": "square" | "vertical" | "stories" | a platform name ("linkedin", "instagram", "tiktok", ...),
  "make_pdf": false,          # true for a LinkedIn carousel with 2+ cards: one PDF page per card
  "title": "optional page title for cards.html (never an ID)",
  "design": {
    "preset": "black" | "white" | "aurora" | "grainy" | "custom",   # default black
    "hue": 228,               # aurora: snapped to the nearest of 6 tuned hues; grainy: any hue tints the smoke
    "card_bg": "#1a3a8f",     # custom: solid hex or a CSS linear-/radial-gradient(...)
    "framed": false,          # custom: true = rounded card on a black frame (like aurora)
    "text_color": "#ffffff", "text_dim_color": "...", "accent_color": "...",   # optional overrides
    "font_path": "/abs/path/Brand.woff2",   # optional custom font file (.woff2 .woff .ttf .otf), embedded
    "font_family": "Georgia", # optional installed font name; used only if installed where this runs
    "logo": "restream",       # adds the bundled Restream mark; there is no logo by default
    "logo_path": "/abs/path/logo.png"       # your own logo file instead
  },
  "cards": [
    {"type": "quote" | "takeaway" | "conclusion" | "qa",
     "headline": "Statement, quote or question (under 18 words)",
     "answer": "Q&A only (under 40 words)",
     "eyebrow": "optional small label, off unless the user asks"}
  ]
}

Nothing is fetched from the network: Inter (SIL OFL 1.1) is bundled in assets/fonts and embedded.
Card text is HTML-escaped; it is rendered as text, never as markup.

Dependencies: Python 3.9+. PNG/PDF output needs Playwright (pip package) and Pillow, plus a
Chromium-based browser. Browser order: $RESTREAM_CARDS_BROWSER (a path) -> Playwright's own
Chromium -> /opt/pw-browsers/chromium -> system Chrome, Chromium or Edge (macOS, Linux, Windows).
This script never installs anything. The HTML fallback needs none of these.
"""
import base64
import colorsys
import html
import io
import json
import math
import mimetypes
import os
import random
import re
import shutil
import sys
import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(SKILL_DIR, "assets")
TEMPLATE_PATH = os.path.join(ASSETS_DIR, "card_template.html")
STAGE_PATH = os.path.join(ASSETS_DIR, "card_stage.html")
FONT_DIR = os.path.join(ASSETS_DIR, "fonts")
INTER_FILES = {400: "inter-400.woff", 600: "inter-600.woff", 700: "inter-700.woff"}
BUNDLED_FAMILY = "Inter Card"   # a private name, so a locally installed Inter never swaps in
DEFAULT_LOGO_WHITE = os.path.join(ASSETS_DIR, "restream-logo-outline-white.svg")

# Captured at 2x device scale, then downsampled to the target size: crisp text at the
# same delivered resolution. Never capture at 1x.
SUPERSAMPLE = 2
WIDTH = 1080
FRAMED_SAFE_MARGIN = 76      # aurora, custom framed
FULLBLEED_SAFE_MARGIN = 70   # black, white, grainy, custom full-bleed

ASPECTS = {
    "square": {"height": 1080},
    "vertical": {"height": 1350},
    # Stories/Reels/TikTok/Shorts: 250 px top and bottom are a platform constraint
    # (UI overlays), measured from the canvas edge. Bigger bottom-left logo there.
    "stories": {"height": 1920, "safe_top": 250, "safe_bottom": 250, "platform_constrained_vertical": True,
                "logo_height": 76, "logo_align": "left", "answer_gap": 120},
}

PLATFORM_ALIASES = {
    "square": "square", "default": "square", "1:1": "square",
    "vertical": "vertical", "4:5": "vertical", "portrait": "vertical", "feed": "vertical",
    "x": "vertical", "twitter": "vertical", "linkedin": "vertical",
    "instagram": "vertical", "instagram_feed": "vertical", "instagram feed": "vertical",
    "facebook": "vertical", "facebook_feed": "vertical", "facebook feed": "vertical",
    "stories": "stories", "story": "stories", "9:16": "stories",
    "instagram_stories": "stories", "instagram stories": "stories",
    "facebook_stories": "stories", "facebook stories": "stories", "reels": "stories",
    "tiktok": "stories", "shorts": "stories", "youtube_shorts": "stories", "youtube shorts": "stories",
}

FOOTER_HEIGHT = 52
ANSWER_GAP_DEFAULT = 60
HEADLINE_START_PX = 110      # quote / takeaway headline
QA_QUESTION_START_PX = 62    # Q&A question (the quiet line)
ANSWER_START_PX = 84         # Q&A answer (the payload); floors 44 / 40 live in card_template.html
HEADLINE_WORD_LIMIT = 18     # headline must be under this many words
ANSWER_WORD_LIMIT = 40       # answer must be under this many words
MAX_CARDS = 20

CARD_TYPES = {"quote": "quote", "takeaway": "takeaway", "conclusion": "takeaway",
              "qa": "qa", "q&a": "qa", "q_and_a": "qa"}

AURORA_VARIANTS = {
    # hue: (gradient angle, glow x, glow y, dark x, dark y, accent x, accent y)
    228: (105, 8, 38, -15, -10, -10, -15),    # Blue
    268: (35, 46, 10, 10, -60, -30, 30),      # Violet
    172: (200, -8, 50, -15, 60, 20, -40),     # Teal
    28: (320, 30, -6, 10, -10, -10, 60),      # Amber
    322: (60, -6, 58, -20, 40, 40, -20),      # Magenta
    148: (150, 40, 30, -18, 20, -20, 10),     # Forest
}

GRAINY_DEEP = "#060608"
GRAINY_LIGHT_X_RANGE = (0.2, 0.8)
GRAINY_LIGHT_Y_RANGE = (0.3, 0.75)
GRAINY_GRAIN_SIGMA = 0.045 * 255   # film grain std-dev, added after the 2x -> 1x downsample

GRAINY_BG_CSS = """
  .smoke-canvas, .smoke-img { position:absolute; inset:0; width:100%; height:100%; z-index:1; display:block; }
"""

# Placeholders use @@NAME@@ and plain .replace(): the GLSL is full of { } braces.
# Shader grain stays 0 on purpose: noise baked in before the Lanczos downsample turns
# into a soft mottle. Real grain is added afterwards in Python (apply_film_grain).
# After drawing, the WebGL canvas is swapped for an <img> and its context released,
# so a page with many cards never runs out of WebGL contexts and prints correctly.
GRAINY_SCRIPT_TEMPLATE = """
  <canvas class="smoke-canvas"></canvas>
  <script>
    (function(){
      var canvas = document.currentScript.parentNode.querySelector('canvas.smoke-canvas');
      var S = { deep:"@@DEEP@@", mid:"@@MID@@", glow:"@@GLOW@@", lightX:@@LIGHT_X@@, lightY:@@LIGHT_Y@@,
        spread:0.62, intensity:1.10, horizon:0.55, lift:0.045, scale:0.72, warp:0.00, contrast:2.85,
        detail:0.20, grain:0, grainSize:2, weave:0.000, weaveSize:5.5, vignette:0.12, seed:@@SEED@@ };
      var VERT = "attribute vec2 aPos; void main(){ gl_Position = vec4(aPos, 0.0, 1.0); }";
      var FRAG = [
"precision highp float;",
"uniform vec2 uRes; uniform float uTime; uniform float uSeed;",
"uniform vec3 uDeep; uniform vec3 uMid; uniform vec3 uGlow; uniform vec2 uLight;",
"uniform float uSpread; uniform float uIntensity; uniform float uHorizon; uniform float uScale;",
"uniform float uWarp; uniform float uContrast; uniform float uDetail; uniform float uLift;",
"uniform float uGrain; uniform float uGrainSize; uniform float uWeave; uniform float uWeaveSize; uniform float uVignette;",
"vec3 mod289(vec3 x){ return x - floor(x * (1.0/289.0)) * 289.0; }",
"vec4 mod289(vec4 x){ return x - floor(x * (1.0/289.0)) * 289.0; }",
"vec4 permute(vec4 x){ return mod289(((x*34.0)+1.0)*x); }",
"vec4 taylorInvSqrt(vec4 r){ return 1.79284291400159 - 0.85373472095314 * r; }",
"float snoise(vec3 v){",
"  const vec2 C = vec2(1.0/6.0, 1.0/3.0); const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);",
"  vec3 i = floor(v + dot(v, C.yyy)); vec3 x0 = v - i + dot(i, C.xxx);",
"  vec3 g = step(x0.yzx, x0.xyz); vec3 l = 1.0 - g;",
"  vec3 i1 = min(g.xyz, l.zxy); vec3 i2 = max(g.xyz, l.zxy);",
"  vec3 x1 = x0 - i1 + C.xxx; vec3 x2 = x0 - i2 + C.yyy; vec3 x3 = x0 - D.yyy;",
"  i = mod289(i);",
"  vec4 p = permute(permute(permute(i.z + vec4(0.0, i1.z, i2.z, 1.0)) + i.y + vec4(0.0, i1.y, i2.y, 1.0)) + i.x + vec4(0.0, i1.x, i2.x, 1.0));",
"  float n_ = 0.142857142857; vec3 ns = n_ * D.wyz - D.xzx;",
"  vec4 j = p - 49.0 * floor(p * ns.z * ns.z);",
"  vec4 x_ = floor(j * ns.z); vec4 y_ = floor(j - 7.0 * x_);",
"  vec4 x = x_ * ns.x + ns.yyyy; vec4 y = y_ * ns.x + ns.yyyy; vec4 h = 1.0 - abs(x) - abs(y);",
"  vec4 b0 = vec4(x.xy, y.xy); vec4 b1 = vec4(x.zw, y.zw);",
"  vec4 s0 = floor(b0)*2.0 + 1.0; vec4 s1 = floor(b1)*2.0 + 1.0; vec4 sh = -step(h, vec4(0.0));",
"  vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy; vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww;",
"  vec3 p0 = vec3(a0.xy, h.x); vec3 p1 = vec3(a0.zw, h.y); vec3 p2 = vec3(a1.xy, h.z); vec3 p3 = vec3(a1.zw, h.w);",
"  vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3)));",
"  p0 *= norm.x; p1 *= norm.y; p2 *= norm.z; p3 *= norm.w;",
"  vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0); m = m * m;",
"  return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));",
"}",
"mat2 rot(float a){ float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }",
"float fbm(vec3 p){ float amp = 0.5, sum = 0.0, tot = 0.0;",
"  for(int i = 0; i < 5; i++){ sum += amp * snoise(p); tot += amp; p.xy = rot(0.62) * p.xy * 2.0; p.z = p.z * 1.09 + 3.1; amp *= uDetail; }",
"  return sum / tot; }",
"float hash21(vec2 p){ p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }",
"void main(){",
"  vec2 uv = gl_FragCoord.xy / uRes; float aspect = uRes.x / uRes.y;",
"  vec2 p = (gl_FragCoord.xy - 0.5 * uRes) / uRes.y;",
"  vec3 base = vec3(p * uScale, uTime * 0.14 + uSeed);",
"  vec2 q = vec2(fbm(base), fbm(base + vec3(3.1, 7.7, 1.3)));",
"  vec2 r = vec2(fbm(base + uWarp * vec3(q, 0.0) + vec3(1.7, 9.2, 0.0)), fbm(base + uWarp * vec3(q, 0.0) + vec3(8.3, 2.8, 0.0)));",
"  float f = fbm(base + uWarp * vec3(r, 0.0)) * 0.5 + 0.5;",
"  float dens = smoothstep(0.14, 0.92, f); dens = pow(clamp(dens, 0.0, 1.0), uContrast);",
"  vec2 lpos = (uLight - 0.5) * vec2(aspect, 1.0); float d = length(p - lpos);",
"  float glow = exp(-(d * d) / max(uSpread * uSpread, 1e-4));",
"  float bw = 0.018 + 0.10 * uSpread; float hy = (p.y - lpos.y) + (f - 0.5) * 0.14;",
"  float band = exp(-(hy * hy) / (bw * bw)); band *= smoothstep(1.2, 0.15, abs(p.x - lpos.x));",
"  float light = glow * uIntensity + band * uHorizon; float shade = mix(0.10, 1.0, dens);",
"  float v = max(light * shade, 0.0);",
"  vec3 col = uDeep; col = mix(col, uMid, 1.0 - exp(-v * 1.7)); col = mix(col, uGlow, 1.0 - exp(-pow(v, 2.3) * 0.85));",
"  col += uLift * (0.35 + 0.65 * dens);",
"  float vig = 1.0 - uVignette * pow(clamp(length(uv - 0.5) * 1.42, 0.0, 1.0), 2.1); col *= clamp(vig, 0.0, 1.0);",
"  vec2 g = gl_FragCoord.xy / max(uWeaveSize, 1.0); float w = sin(g.x * 3.14159265) * sin(g.y * 3.14159265); col *= 1.0 + w * uWeave;",
"  vec2 gc = floor(gl_FragCoord.xy / max(uGrainSize, 1.0));",
"  float gr = hash21(gc + floor(uTime * 24.0) * vec2(13.71, 7.37) + uSeed);",
"  col += (gr - 0.5) * uGrain * (0.55 + 0.45 * (1.0 - dens));",
"  col += (hash21(gl_FragCoord.xy * 1.37 + uSeed) - 0.5) / 255.0;",
"  gl_FragColor = vec4(clamp(col, 0.0, 1.0), 1.0);",
"}"].join("\\n");
      function hexToRgb(hex){ var n = parseInt(hex.replace("#", ""), 16); return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255]; }
      function compile(gl, type, src){ var sh = gl.createShader(type); gl.shaderSource(sh, src); gl.compileShader(sh);
        if(!gl.getShaderParameter(sh, gl.COMPILE_STATUS)){ throw new Error(gl.getShaderInfoLog(sh)); } return sh; }
      try {
        var gl = canvas.getContext("webgl", { antialias:false, alpha:false, depth:false, stencil:false, preserveDrawingBuffer:true });
        if(!gl){ return; }   // no WebGL: the card's flat dark background shows instead
        var prog = gl.createProgram();
        gl.attachShader(prog, compile(gl, gl.VERTEX_SHADER, VERT));
        gl.attachShader(prog, compile(gl, gl.FRAGMENT_SHADER, FRAG));
        gl.linkProgram(prog); gl.useProgram(prog);
        var buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1,3,-1,-1,3]), gl.STATIC_DRAW);
        var aPos = gl.getAttribLocation(prog, "aPos"); gl.enableVertexAttribArray(aPos);
        gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);
        var FLOATS = ["spread","intensity","horizon","lift","scale","warp","contrast","detail","grain","grainSize","weave","weaveSize","vignette","seed"];
        var dpr = Math.min(window.devicePixelRatio || 1, 2);
        var w = Math.max(1, Math.round((canvas.clientWidth || 1) * dpr));
        var h = Math.max(1, Math.round((canvas.clientHeight || 1) * dpr));
        canvas.width = w; canvas.height = h; gl.viewport(0, 0, w, h);
        gl.uniform2f(gl.getUniformLocation(prog, "uRes"), w, h);
        gl.uniform1f(gl.getUniformLocation(prog, "uTime"), 0);
        gl.uniform2f(gl.getUniformLocation(prog, "uLight"), S.lightX, S.lightY);
        gl.uniform3fv(gl.getUniformLocation(prog, "uDeep"), hexToRgb(S.deep));
        gl.uniform3fv(gl.getUniformLocation(prog, "uMid"), hexToRgb(S.mid));
        gl.uniform3fv(gl.getUniformLocation(prog, "uGlow"), hexToRgb(S.glow));
        FLOATS.forEach(function(k){ gl.uniform1f(gl.getUniformLocation(prog, "u" + k[0].toUpperCase() + k.slice(1)), S[k]); });
        gl.drawArrays(gl.TRIANGLES, 0, 3);
        var img = document.createElement("img");
        img.className = "smoke-img"; img.alt = "";
        img.src = canvas.toDataURL("image/png");
        canvas.parentNode.replaceChild(img, canvas);
        var lose = gl.getExtension("WEBGL_lose_context"); if (lose) lose.loseContext();
      } catch (e) { /* keep the flat background */ }
    })();
  </script>
"""

GALLERY_CSS = """
  body { background: #141414; color: #ececec; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
         padding: 24px 16px 48px; }
  .intro { max-width: 640px; margin: 0 auto 28px; font-size: 16px; line-height: 1.55; }
  .intro h1 { font-size: 22px; font-weight: 650; margin-bottom: 8px; }
  .intro p { margin-top: 8px; color: #bdbdbd; }
  .frame { margin: 0 auto 24px; overflow: hidden; border-radius: 6px; }
  .frame .stage { transform-origin: 0 0; }
  @page { size: __WIDTH__px __HEIGHT__px; margin: 0; }
  @media print {
    body { background: none; padding: 0; }
    .intro { display: none; }
    .frame { width: auto !important; height: auto !important; margin: 0; border-radius: 0;
             break-after: page; page-break-after: always; }
    .frame:last-of-type { break-after: auto; page-break-after: auto; }
    .frame .stage { transform: none !important; }
  }
"""

GALLERY_SCALE_JS = """
<script>
  (function () {
    var W = __WIDTH__, H = __HEIGHT__;
    function layout() {
      var s = Math.min(0.5, (window.innerWidth - 32) / W);
      document.querySelectorAll('.frame').forEach(function (f) {
        f.style.width = Math.round(W * s) + 'px'; f.style.height = Math.round(H * s) + 'px';
        f.firstElementChild.style.transform = 'scale(' + s + ')';
      });
    }
    layout(); window.addEventListener('resize', layout);
  })();
</script>
"""

GALLERY_INTRO = """
<div class="intro">
  <h1>Your cards (__COUNT__)</h1>
  <p><strong>Save as PDF</strong> (one card per page, the format LinkedIn carousels need): press Ctrl+P
  (Cmd+P on a Mac), choose <em>Save as PDF</em>, set margins to <em>None</em>, and turn on
  <em>Background graphics</em> if the backgrounds come out white.</p>
  <p><strong>Need PNG images?</strong> Upload that PDF to Canva and download each page as PNG,
  or take a screenshot of each card.</p>
</div>
"""

UNSAFE_CSS = re.compile(r"[<>{};\\]|url\s*\(|@import|expression\s*\(", re.IGNORECASE)


class SpecError(ValueError):
    pass


def emit(obj, code):
    print(json.dumps(obj, ensure_ascii=False))
    sys.exit(code)


def safe_css(value, field):
    value = str(value).strip()
    if not value or UNSAFE_CSS.search(value):
        raise SpecError(f"design.{field} must be a plain CSS color or gradient (got an unsupported value)")
    return value


def b64_file(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def resolve_aspect(name):
    key = PLATFORM_ALIASES.get(str(name or "square").strip().lower())
    if key is None:
        raise SpecError(f"Unknown aspect or platform '{name}'. Ask the user whether it should be "
                        "square (1:1), vertical (4:5) or stories (9:16).")
    return key, ASPECTS[key]


def nearest_aurora_variant(hue):
    hue = float(hue) % 360
    best = min(AURORA_VARIANTS, key=lambda h: min(abs(h - hue), 360 - abs(h - hue)))
    return best, AURORA_VARIANTS[best]


def grainy_colors_for_hue(hue):
    """No hue -> neutral cool-grey smoke. A hue -> the same low-saturation treatment rotated."""
    if hue is None:
        return "#2a2c33", "#c9cdd6"
    h = (float(hue) % 360) / 360.0
    to_hex = lambda rgb: "#%02x%02x%02x" % tuple(round(c * 255) for c in rgb)
    return to_hex(colorsys.hls_to_rgb(h, 0.19, 0.14)), to_hex(colorsys.hls_to_rgb(h, 0.82, 0.12))


def hex_brightness(value):
    m = re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", value.strip())
    if not m:
        return None
    hx = m.group(1)
    if len(hx) == 3:
        hx = "".join(c * 2 for c in hx)
    r, g, b = (int(hx[i:i + 2], 16) for i in (0, 2, 4))
    return (r * 299 + g * 587 + b * 114) / 1000


def font_css(design):
    faces = []
    for weight, fn in INTER_FILES.items():
        faces.append("@font-face { font-family: '%s'; src: url(data:font/woff;base64,%s) format('woff'); "
                     "font-weight: %d; font-style: normal; font-display: block; }"
                     % (BUNDLED_FAMILY, b64_file(os.path.join(FONT_DIR, fn)), weight))
    stack = "'%s', sans-serif" % BUNDLED_FAMILY
    load_family = "'%s'" % BUNDLED_FAMILY
    font_path = design.get("font_path")
    font_family = str(design.get("font_family") or "").strip()
    if font_path:
        if not os.path.isfile(font_path):
            raise SpecError(f"font_path does not exist: {os.path.basename(str(font_path))}")
        ext = os.path.splitext(font_path)[1].lower()
        fmt = {".woff2": ("font/woff2", "woff2"), ".woff": ("font/woff", "woff"),
               ".ttf": ("font/ttf", "truetype"), ".otf": ("font/otf", "opentype")}.get(ext)
        if not fmt:
            raise SpecError("font_path must be a .woff2, .woff, .ttf or .otf file")
        faces.append("@font-face { font-family: 'Card Custom'; src: url(data:%s;base64,%s) format('%s'); "
                     "font-weight: 100 900; font-style: normal; font-display: block; }"
                     % (fmt[0], b64_file(font_path), fmt[1]))
        stack = "'Card Custom', '%s', sans-serif" % BUNDLED_FAMILY
        load_family = "'Card Custom'"
    elif font_family and font_family.lower() != "inter":
        name = re.sub(r"[^A-Za-z0-9 \-_]", "", font_family)[:60]
        if name:
            stack = "'%s', '%s', sans-serif" % (name, BUNDLED_FAMILY)
    return "\n  ".join(faces), stack, load_family


def resolve_design(design):
    preset = str(design.get("preset", "black")).strip().lower()
    d = {
        "preset": preset, "inset_px": 0, "radius": 0, "shadow": "none", "stage_bg": "#000000",
        "background_layer_css": "", "grainy": None,
    }
    if preset == "black":
        d.update(card_bg="#000000", text_color="#ffffff",
                 text_dim_color="rgba(255,255,255,0.72)", accent_color="rgba(255,255,255,0.55)")
    elif preset == "white":
        d.update(stage_bg="#ffffff", card_bg="#ffffff", text_color="#0a0a0a",
                 text_dim_color="rgba(10,10,10,0.62)", accent_color="rgba(10,10,10,0.55)")
    elif preset == "aurora":
        hue, (angle, glow_x, glow_y, dark_x, dark_y, accent_x, accent_y) = nearest_aurora_variant(design.get("hue", 228))
        hue2 = (hue + 180) % 360
        d.update(
            card_bg="#05060a", text_color="#ffffff",
            text_dim_color="rgba(255,255,255,0.72)", accent_color="rgba(255,255,255,0.6)",
            inset_px=round(WIDTH * 0.035), radius=44,
            shadow="0 40px 100px rgba(0,0,0,0.65), 0 10px 30px rgba(0,0,0,0.5)",
            background_layer_css=f"""
  .color-layer {{ position:absolute; inset:-10%; filter: blur(85px); z-index:1; }}
  .blob-main {{ position:absolute; inset:0; background: linear-gradient({angle}deg,
      hsl({hue}, 55%, 17%) 0%, hsl({hue}, 55%, 30%) 30%, hsl({hue}, 50%, 38%) 50%,
      hsl({hue}, 50%, 17%) 72%, #05060a 100%); }}
  .blob-accent {{ position:absolute; left:{accent_x}%; bottom:{accent_y}%; width:75%; height:60%;
      background: radial-gradient(ellipse at 35% 65%, hsla({hue2}, 45%, 45%, 0.5) 0%, hsla({hue2}, 45%, 40%, 0.25) 40%, transparent 72%); }}
  .blob-dark {{ position:absolute; top:{dark_x}%; right:{dark_y}%; width:70%; height:65%;
      background: radial-gradient(ellipse at 60% 30%, #05060a 0%, rgba(5,6,10,0.8) 42%, transparent 75%); }}
  .glow {{ position:absolute; left:{glow_x}%; top:{glow_y}%; width:46%; height:36%;
      background: radial-gradient(ellipse at 50% 50%, hsla({hue}, 50%, 55%, 0.35) 0%, hsla({hue}, 50%, 45%, 0.14) 45%, transparent 75%); }}
  .grain {{ position:absolute; inset:-10%; opacity:0.3; mix-blend-mode:overlay; z-index:2; }}
""",
            background_layer_html="""
    <div class="color-layer"><div class="blob-main"></div><div class="blob-dark"></div><div class="blob-accent"></div><div class="glow"></div></div>
    <svg class="grain" width="120%" height="120%">
      <filter id="ng"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/>
      <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1 0"/></filter>
      <rect width="100%" height="100%" filter="url(#ng)"/>
    </svg>
""",
        )
    elif preset == "grainy":
        mid_hex, glow_hex = grainy_colors_for_hue(design.get("hue"))
        # One random draw per pack: every card in the pack shares the smoke pattern.
        d.update(
            card_bg="#0a0a0c", text_color="#ffffff",
            text_dim_color="rgba(255,255,255,0.72)", accent_color="rgba(255,255,255,0.6)",
            background_layer_css=GRAINY_BG_CSS,
            background_layer_html=(GRAINY_SCRIPT_TEMPLATE
                                   .replace("@@DEEP@@", GRAINY_DEEP).replace("@@MID@@", mid_hex)
                                   .replace("@@GLOW@@", glow_hex)
                                   .replace("@@LIGHT_X@@", str(round(random.uniform(*GRAINY_LIGHT_X_RANGE), 3)))
                                   .replace("@@LIGHT_Y@@", str(round(random.uniform(*GRAINY_LIGHT_Y_RANGE), 3)))
                                   .replace("@@SEED@@", str(round(random.uniform(3.0, 8.0), 3)))),
            grainy=True,
        )
    elif preset == "custom":
        card_bg = safe_css(design.get("card_bg", "#101010"), "card_bg")
        d.update(card_bg=card_bg, stage_bg="#000000", text_color="#ffffff",
                 text_dim_color="rgba(255,255,255,0.7)", accent_color="rgba(255,255,255,0.55)")
        brightness = hex_brightness(card_bg)
        if brightness is not None and brightness > 128:   # light solid color -> dark text (YIQ)
            d.update(text_color="#0a0a0a", text_dim_color="rgba(10,10,10,0.62)", accent_color="rgba(10,10,10,0.55)")
        if not design.get("framed"):
            d["stage_bg"] = card_bg if brightness is not None else "#000000"
        else:
            d.update(inset_px=round(WIDTH * 0.035), radius=44,
                     shadow="0 40px 100px rgba(0,0,0,0.65), 0 10px 30px rgba(0,0,0,0.5)")
    else:
        raise SpecError(f"Unknown design preset '{preset}'. Use black, white, aurora, grainy or custom.")
    d.setdefault("background_layer_html", "")
    for key in ("text_color", "text_dim_color", "accent_color"):
        if design.get(key):
            d[key] = safe_css(design[key], key)
    return d


def resolve_logo_path(design):
    if str(design.get("logo", "")).lower() == "none":
        return None
    if design.get("logo_path"):
        if not os.path.isfile(design["logo_path"]):
            raise SpecError(f"logo_path does not exist: {os.path.basename(str(design['logo_path']))}")
        return design["logo_path"]
    # No logo by default (testers didn't want a brand mark on their own posts).
    # The bundled Restream mark renders only when asked for: logo: "restream".
    if str(design.get("logo", "")).lower() == "restream":
        return DEFAULT_LOGO_WHITE
    return None


def logo_html(path):
    if not path:
        return ""
    mime = mimetypes.guess_type(path)[0] or "image/png"
    return f'<img class="logo" alt="" src="data:{mime};base64,{b64_file(path)}">'


def text_html(value):
    return html.escape(str(value).strip()).replace("\n", "<br>")


def normalize_cards(cards):
    if not isinstance(cards, list) or not cards:
        raise SpecError("cards must be a non-empty list")
    if len(cards) > MAX_CARDS:
        raise SpecError(f"{len(cards)} cards is more than {MAX_CARDS}; split them into separate packs")
    out, warnings = [], []
    for i, c in enumerate(cards, start=1):
        ctype = CARD_TYPES.get(str(c.get("type", "takeaway")).strip().lower())
        if not ctype:
            raise SpecError(f"card {i}: unknown type '{c.get('type')}' (use quote, takeaway, conclusion or qa)")
        headline = str(c.get("headline", "")).strip()
        answer = str(c.get("answer", "") or "").strip()
        if not headline:
            raise SpecError(f"card {i}: headline is empty")
        if ctype == "qa" and not answer:
            raise SpecError(f"card {i}: a qa card needs an answer")
        if len(headline.split()) >= HEADLINE_WORD_LIMIT:
            warnings.append({"card": i, "field": "headline", "words": len(headline.split()),
                             "limit": f"under {HEADLINE_WORD_LIMIT}"})
        if answer and len(answer.split()) >= ANSWER_WORD_LIMIT:
            warnings.append({"card": i, "field": "answer", "words": len(answer.split()),
                             "limit": f"under {ANSWER_WORD_LIMIT}"})
        out.append({"type": ctype, "headline": headline, "answer": answer if ctype == "qa" else "",
                    "eyebrow": str(c.get("eyebrow", "") or "").strip()})
    return out, warnings


def fill(template, values):
    # Single pass: inserted text is never re-scanned for placeholders.
    return re.sub(r"__([A-Z0-9_]+)__", lambda m: str(values.get(m.group(1), m.group(0))), template)


def page_values(aspect_spec, d, fonts):
    height = aspect_spec["height"]
    inset = d["inset_px"]
    card_w, card_h = WIDTH - 2 * inset, height - 2 * inset
    margin = FRAMED_SAFE_MARGIN if inset > 0 else FULLBLEED_SAFE_MARGIN
    if aspect_spec.get("platform_constrained_vertical"):
        # Measured from the true canvas edge, then the frame inset is taken back out.
        safe_top = max(aspect_spec["safe_top"], inset) - inset
        safe_bottom = max(aspect_spec["safe_bottom"], inset) - inset
    else:
        safe_top = safe_bottom = margin
    logo_h = aspect_spec.get("logo_height", FOOTER_HEIGHT)
    return {
        "WIDTH": WIDTH, "HEIGHT": height,
        "FONT_FACE_CSS": fonts[0], "FONT_FAMILY_STACK": fonts[1], "FONT_LOAD_FAMILY": fonts[2],
        "STAGE_BG": d["stage_bg"], "CARD_BG": d["card_bg"], "INSET_PX": inset,
        "RADIUS": d["radius"], "CARD_SHADOW": d["shadow"],
        "BACKGROUND_LAYER_CSS": d["background_layer_css"],
        "TEXT_COLOR": d["text_color"], "TEXT_DIM_COLOR": d["text_dim_color"], "ACCENT_COLOR": d["accent_color"],
        "SAFE_LEFT": round(margin), "SAFE_TOP": round(safe_top),
        "SAFE_WIDTH": round(card_w - 2 * margin), "SAFE_HEIGHT": round(card_h - safe_top - safe_bottom),
        "FOOTER_HEIGHT": logo_h, "LOGO_HEIGHT": logo_h,
        "FOOTER_JUSTIFY": "flex-start" if aspect_spec.get("logo_align") == "left" else "flex-end",
        "ANSWER_GAP_PX": aspect_spec.get("answer_gap", ANSWER_GAP_DEFAULT),
    }


def stage_html(stage_tpl, d, card, logo):
    is_qa = card["type"] == "qa"
    return fill(stage_tpl, {
        "HEADLINE_START_PX": QA_QUESTION_START_PX if is_qa else HEADLINE_START_PX,
        "ANSWER_START_PX": ANSWER_START_PX,
        "CARD_TYPE_CLASS": "qa" if is_qa else card["type"],
        "BACKGROUND_LAYER_HTML": d["background_layer_html"],
        "EYEBROW_BLOCK": f'<div class="eyebrow">{text_html(card["eyebrow"])}</div>' if card["eyebrow"] else "",
        "HEADLINE": text_html(card["headline"]),
        "ANSWER_BLOCK": f'<div class="answer">{text_html(card["answer"])}</div>' if card["answer"] else "",
        "FOOTER_BLOCK": f'<div class="footer">{logo}</div>' if logo else "",
    })


def single_page(template, values, stage):
    v = dict(values)
    v.update(PAGE_TITLE="Card", PAGE_HEADER="", STAGES=stage,
             PAGE_CSS="html, body { width: %dpx; height: %dpx; overflow: hidden; background: %s; }"
                      % (values["WIDTH"], values["HEIGHT"], values["STAGE_BG"]))
    return fill(template, v)


def gallery_page(template, values, stages, title):
    v = dict(values)
    frames = "\n".join(f'<div class="frame">{s}</div>' for s in stages)
    v.update(PAGE_TITLE=html.escape(title or "Your cards"),
             PAGE_CSS=fill(GALLERY_CSS, values),
             PAGE_HEADER=fill(GALLERY_INTRO, {"COUNT": len(stages)}),
             STAGES=frames + fill(GALLERY_SCALE_JS, values))
    return fill(template, v)


def write_gallery(out_dir, template, values, stages, title):
    path = os.path.join(out_dir, "cards.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(gallery_page(template, values, stages, title))
    return os.path.abspath(path)


def browser_candidates():
    env = os.environ.get("RESTREAM_CARDS_BROWSER")
    if env:
        yield "env RESTREAM_CARDS_BROWSER", env
    yield "playwright-chromium", None
    paths = [
        "/opt/pw-browsers/chromium",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge"):
        found = shutil.which(name)
        if found:
            paths.append(found)
    for base in (os.environ.get("PROGRAMFILES"), os.environ.get("PROGRAMFILES(X86)"), os.environ.get("LOCALAPPDATA")):
        if base:
            paths.append(os.path.join(base, "Google", "Chrome", "Application", "chrome.exe"))
            paths.append(os.path.join(base, "Microsoft", "Edge", "Application", "msedge.exe"))
    seen = set()
    for p in paths:
        if p not in seen and os.path.isfile(p) and os.access(p, os.X_OK):
            seen.add(p)
            yield "system", p


def launch_browser(pw):
    attempts = []
    for label, path in browser_candidates():
        try:
            kwargs = {"headless": True, "timeout": 30000}
            if path:
                kwargs["executable_path"] = path
            return pw.chromium.launch(**kwargs), (label if not path else f"{label}: {path}"), attempts
        except Exception as e:  # noqa: BLE001 - any launch failure means: try the next browser
            first = str(e).strip().splitlines()[0] if str(e).strip() else type(e).__name__
            attempts.append({"browser": label if not path else path, "error": first[:200]})
    return None, None, attempts


def apply_film_grain(im):
    """Monochrome per-pixel gaussian grain on the final-size image (grainy preset only)."""
    from PIL import Image, ImageChops
    noise = Image.effect_noise(im.size, GRAINY_GRAIN_SIGMA).convert("RGB")
    return ImageChops.add(im, noise, scale=1.0, offset=-128)


def render_pngs(out_dir, template, values, stages, aspect_spec, d, make_pdf):
    from PIL import Image
    from playwright.sync_api import sync_playwright
    lanczos = getattr(Image, "Resampling", Image).LANCZOS
    height = aspect_spec["height"]
    png_paths, overflowed, failed = [], [], []
    with sync_playwright() as pw:
        browser, used, attempts = launch_browser(pw)
        if browser is None:
            return None, {"reason": "no_browser", "attempts": attempts}
        try:
            page = browser.new_page(viewport={"width": WIDTH, "height": height}, device_scale_factor=SUPERSAMPLE)
            js_errors = []
            page.on("pageerror", lambda err: js_errors.append(str(err)[:200]))
            for i, stage in enumerate(stages, start=1):
                try:
                    del js_errors[:]
                    page.set_content(single_page(template, values, stage), wait_until="load")
                    try:
                        page.wait_for_function("window.__fitDone === true", timeout=10000)
                    except Exception:
                        raise RuntimeError("layout script did not finish" + (": " + js_errors[0] if js_errors else ""))
                    over = page.evaluate("window.__fitOverflowed")
                    if over and over[0]:
                        overflowed.append(i)
                    raw = page.screenshot(type="png")
                    im = Image.open(io.BytesIO(raw)).convert("RGB").resize((WIDTH, height), lanczos)
                    if d.get("grainy"):
                        im = apply_film_grain(im)
                    path = os.path.abspath(os.path.join(out_dir, f"card_{i:02d}.png"))
                    im.save(path, "PNG", optimize=True)
                    png_paths.append(path)
                except Exception as e:  # noqa: BLE001
                    failed.append({"card": i, "error": (str(e).strip().splitlines() or [type(e).__name__])[0][:200]})
        finally:
            browser.close()
    if not png_paths:
        return None, {"reason": "render_failed", "failed_cards": failed, "browser": used}
    result = {"browser": used, "cards": png_paths, "overflowed_even_at_min_size": overflowed,
              "failed_cards": failed, "zip": None, "pdf": None}
    if len(png_paths) > 1:
        zpath = os.path.abspath(os.path.join(out_dir, "cards.zip"))
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in png_paths:
                zf.write(p, os.path.basename(p))
        result["zip"] = zpath
    if make_pdf and len(png_paths) > 1:
        pdf = os.path.abspath(os.path.join(out_dir, "cards.pdf"))
        pages = [Image.open(p).convert("RGB") for p in png_paths]
        # 300 dpi keeps the pixel size and gives sane page sizes (1080x1350 px = 3.6x4.5 in) instead of
        # the 15x19-inch pages that 72 dpi produced.
        pages[0].save(pdf, "PDF", save_all=True, append_images=pages[1:], resolution=300.0)
        for p in pages:
            p.close()
        result["pdf"] = pdf
    return result, None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    html_only = "--html-only" in sys.argv[1:]
    if len(args) != 2:
        emit({"status": "error", "error": "usage: render_cards.py SPEC.json OUT_DIR [--html-only]"}, 1)
    spec_path, out_dir = args
    try:
        with open(spec_path, encoding="utf-8") as f:
            spec = json.load(f)
        design = spec.get("design") or {}
        aspect_key, aspect_spec = resolve_aspect(spec.get("aspect", "square"))
        cards, warnings = normalize_cards(spec.get("cards"))
        d = resolve_design(design)
        logo = logo_html(resolve_logo_path(design))
        fonts = font_css(design)
        with open(TEMPLATE_PATH, encoding="utf-8") as f:
            template = f.read()
        with open(STAGE_PATH, encoding="utf-8") as f:
            stage_tpl = f.read()
    except (SpecError, ValueError, OSError, TypeError, AttributeError) as e:
        emit({"status": "error", "error": str(e)}, 1)

    os.makedirs(out_dir, exist_ok=True)
    values = page_values(aspect_spec, d, fonts)
    stages = [stage_html(stage_tpl, d, c, logo) for c in cards]
    base = {"aspect": aspect_key, "size": f"{WIDTH}x{aspect_spec['height']}", "preset": d["preset"],
            "count": len(cards), "over_word_limit": warnings,
            "manifest": [{"file": f"card_{i:02d}.png", "type": c["type"], "headline": c["headline"]}
                         for i, c in enumerate(cards, start=1)]}

    def fallback(reason, detail, code=2):
        path = write_gallery(out_dir, template, values, stages, spec.get("title"))
        out = dict(base, status="html_fallback", reason=reason, html=path, detail=detail)
        out["overflowed_even_at_min_size"] = None   # unknown without a browser; check the page
        emit(out, code)

    if html_only:
        fallback("html_requested", None, code=0)
    missing = []
    try:
        import playwright.sync_api  # noqa: F401
    except ImportError:
        missing.append("playwright")
    try:
        import PIL  # noqa: F401
    except ImportError:
        missing.append("pillow")
    if missing:
        fallback("missing_dependency", {"missing": missing})
    try:
        result, problem = render_pngs(out_dir, template, values, stages, aspect_spec, d,
                                      bool(spec.get("make_pdf")))
    except Exception as e:  # noqa: BLE001 - e.g. the Playwright driver itself cannot start
        result, problem = None, {"reason": "playwright_failed",
                                 "error": (str(e).strip().splitlines() or [type(e).__name__])[0][:200]}
    if result is None:
        fallback(problem.pop("reason"), problem)
    emit(dict(base, status="ok", **result), 0)


if __name__ == "__main__":
    main()
