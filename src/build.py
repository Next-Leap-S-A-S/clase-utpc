#!/usr/bin/env python3
"""Ensambla index.html a partir de src/.

- template.html   : marcado, estilos y logica (UTF-8, legible)
- asistentes.js   : los asistentes de ejemplo (UTF-8, legible)
- assets/         : tipografias .woff2 y logo, se incrustan en base64

El resultado es un unico archivo ASCII puro: fuera de <script> los caracteres
no ASCII van como entidades HTML (&#NNNN;) y dentro de <script> como \\uXXXX.

Antes de escribir, revisa:
- que cada asistente tenga entre 300 y 600 palabras de instrucciones (R + C + I),
- que la prosa no use guiones largos, punto y coma, signos de exclamacion
  ni las frases y conectores que la guia de redaccion excluye.

Uso:  python3 src/build.py
"""
import base64, pathlib, re, sys

SRC = pathlib.Path(__file__).resolve().parent
ROOT = SRC.parent
OUT = ROOT / "index.html"

MIN_WORDS, MAX_WORDS = 300, 600

BANNED = [
    "—", "–", "!", "¡",
    "no solo", "no sólo", "sino también",
    "sin embargo", "por lo tanto", "en ese sentido", "por ende", "cabe destacar",
    "cabe resaltar", "es importante destacar", "en el mundo actual",
    "cada vez más", "hoy más que nunca", "en la era de",
]


def b64(path):
    return base64.b64encode(path.read_bytes()).decode("ascii")


def font_css():
    faces = [("IBM Plex Mono", 400, "ibmplexmono-400.woff2"),
             ("IBM Plex Mono", 500, "ibmplexmono-500.woff2"),
             ("Inter", 400, "inter-400.woff2"),
             ("Inter", 500, "inter-500.woff2"),
             ("Inter", 600, "inter-600.woff2")]
    out = []
    for fam, w, fn in faces:
        out.append("@font-face{font-family:'%s';font-style:normal;font-weight:%d;font-display:swap;"
                   "src:url(data:font/woff2;base64,%s) format('woff2');}" % (fam, w, b64(SRC / "assets" / fn)))
    return "\n".join(out)


def esc_html(s):
    return "".join(c if ord(c) < 128 else "&#%d;" % ord(c) for c in s)


def esc_js(s):
    out = []
    for c in s:
        o = ord(c)
        if o < 128:
            out.append(c)
        elif o <= 0xFFFF:
            out.append("\\u%04x" % o)
        else:
            o -= 0x10000
            out.append("\\u%04x\\u%04x" % (0xD800 + (o >> 10), 0xDC00 + (o & 0x3FF)))
    return "".join(out)


def asciify(html):
    out, pos = [], 0
    for m in re.finditer(r"<script\b[^>]*>.*?</script>", html, flags=re.S):
        out.append(esc_html(html[pos:m.start()]))
        out.append(esc_js(m.group(0)))
        pos = m.end()
    out.append(esc_html(html[pos:]))
    return "".join(out)


def check_assistants(js):
    """Cuenta palabras por asistente y revisa la prosa de sus campos de texto."""
    problems, report = [], []
    blocks = re.split(r"\n\{\n", js)[1:]
    for b in blocks:
        name = re.search(r'nombre:\s*"([^"]+)"', b).group(1)
        parts = dict(re.findall(r"(rol|contexto|instruccion):\s*`(.*?)`", b, flags=re.S))
        n = sum(len(parts[k].split()) for k in ("rol", "contexto", "instruccion"))
        report.append((name, n))
        if not (MIN_WORDS <= n <= MAX_WORDS):
            problems.append(f"{name}: {n} palabras (rango {MIN_WORDS}-{MAX_WORDS})")
        texts = list(parts.values()) + re.findall(r'"((?:[^"\\]|\\.)*)"', b)
        for t in texts:
            low = t.lower()
            for bad in BANNED:
                if bad in low:
                    problems.append(f"{name}: contiene {bad!r} en: {t[:70]}")
            if ";" in t:
                problems.append(f"{name}: punto y coma en: {t[:70]}")
            if "por verificar" not in parts["instruccion"]:
                pass
        if "(por verificar)" not in parts["instruccion"]:
            problems.append(f"{name}: la instruccion no exige la marca (por verificar)")
    return problems, report


def check_template_prose(tpl):
    """Revisa el texto visible de la plantilla (sin estilos, scripts ni etiquetas)."""
    problems = []
    body = re.sub(r"<style\b.*?</style>", " ", tpl, flags=re.S)
    scripts = re.findall(r"<script\b.*?</script>", body, flags=re.S)
    body = re.sub(r"<script\b.*?</script>", " ", body, flags=re.S)
    body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    body = re.sub(r"<!doctype[^>]*>", " ", body, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", body)
    text = re.sub(r"&[a-zA-Z]+;|&#\d+;", " ", text)
    text = re.sub(r"\{\{[A-Z_]+\}\}", " ", text)
    low = text.lower()
    for bad in BANNED:
        if bad in low:
            i = low.index(bad)
            problems.append(f"plantilla: contiene {bad!r} cerca de: {text[max(0,i-40):i+40].strip()!r}")
    if ";" in text:
        i = text.index(";")
        problems.append(f"plantilla: punto y coma cerca de: {text[max(0,i-40):i+40].strip()!r}")
    # Cadenas de interfaz dentro del script: solo frases y signos excluidos.
    for s in scripts:
        for lit in re.findall(r'"((?:[^"\\\n]|\\.)*)"', s):
            dec = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), lit).lower()
            for bad in BANNED:
                if bad == "!" and (dec.startswith("!") or "!=" in dec):
                    continue
                if bad in dec:
                    problems.append(f"script: contiene {bad!r} en: {lit[:70]}")
    return problems


def main():
    tpl = (SRC / "template.html").read_text(encoding="utf-8")
    js = (SRC / "asistentes.js").read_text(encoding="utf-8").strip()

    problems, report = check_assistants(js)
    problems += check_template_prose(tpl)
    if problems:
        print("revision de redaccion y extension:")
        for p in problems:
            print("  -", p)
        sys.exit(1)

    html = (tpl.replace("{{FONT_CSS}}", font_css())
               .replace("{{LOGO_PNG}}", "data:image/png;base64," + b64(SRC / "assets" / "nextleap-mark.png"))
               .replace("{{ASISTENTES}}", js))
    left = re.findall(r"\{\{[A-Z_]+\}\}", html)
    if left:
        sys.exit(f"placeholders sin resolver: {left}")
    html = asciify(html)
    assert all(ord(c) < 128 for c in html), "quedaron caracteres no ASCII"
    OUT.write_text(html, encoding="ascii")

    total = sum(n for _, n in report)
    print(f"ok: {OUT} ({OUT.stat().st_size:,} bytes, {len(report)} asistentes, {total:,} palabras de instrucciones)")
    for name, n in report:
        print(f"  {n:4d}  {name}")


if __name__ == "__main__":
    main()
