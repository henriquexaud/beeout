"""
Gera o motion "caminhada resmungando" em SVG a partir da pose 'andando' da folha v2.

A pose é vetorizada (mesmas formas e cores da arte) e separada em partes
— rabo, perna de trás, perna da frente e corpo — que são animadas
com SMIL (<animateTransform>/<animate>), então o SVG anima sozinho,
dentro ou fora do HTML.

    pip install pillow numpy opencv-python-headless
    python3 build.py      # arte/mamu-v2.png -> ../mamu-caminhando.html
"""
import itertools
import os
import sys

import cv2
import numpy as np

from seg import load, parts, poly_mask, NAMES, PAL, X0, Y0

S = 4  # resolução interna da vetorização
_ids = itertools.count()


def hexc(c):
    return '#%02X%02X%02X' % tuple(c)


def vec(mask, thr=0.5, min_area=2.0):
    """Máscara (0..1) -> path SVG suave nas coordenadas do recorte."""
    h, w = mask.shape
    up = cv2.resize(mask.astype(np.float32), (w * S, h * S), interpolation=cv2.INTER_LINEAR)
    up = cv2.GaussianBlur(up, (0, 0), S * 0.45)
    cs, _ = cv2.findContours((up > thr).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        if cv2.contourArea(c) < min_area * S * S:
            continue
        c = cv2.approxPolyDP(c, S * 0.28, True)[:, 0, :]
        pts = ' '.join(f'{(x + .5) / S:.1f},{(y + .5) / S:.1f}' for x, y in c)
        out.append(f'M{pts}Z')
    return ''.join(out)


def crop_pts(pts):
    return ' '.join(f'{x - X0},{y - Y0}' for x, y in pts)


ORDER = ['shade', 'shade2', 'brown', 'cream2', 'cream', 'olheira']


def layer(alpha, label, region, base_region=None, skip=(), ext=''):
    """Silhueta na cor do corpo + manchas de cada cor, recortadas pela silhueta."""
    base_region = region if base_region is None else base_region
    base = vec(alpha * base_region)
    cid = f'parte{next(_ids)}'
    g = f'<clipPath id="{cid}"><path d="{base}"/></clipPath>{ext}'
    g += f'<path d="{base}" fill="{hexc(PAL["body"])}"/>'
    g += f'<g clip-path="url(#{cid})">'
    for k in ORDER:
        if k in skip:
            continue
        m = (label == NAMES.index(k)) & region & (alpha > 0.3)
        if m.sum() < 3:
            continue
        g += f'<path d="{vec(m.astype(np.float32), 0.42)}" fill="{hexc(PAL[k])}"/>'
    return g + '</g>'


def eyes(alpha, label, h, w):
    """Olhos como grupos próprios: branco, pupila (que revira) e pálpebra (que pisca)."""
    out = []
    for i, (bx0, by0, bx1, by1) in enumerate([(183, 624, 235, 662), (254, 633, 298, 668)]):
        box = poly_mask(h, w, [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)])
        white = (label == NAMES.index('white')) & box & (alpha > 0.3)
        pupil = (label == NAMES.index('pupil')) & box & (alpha > 0.3)
        union = vec((white | pupil).astype(np.float32), 0.42)
        union_big = vec((white | pupil).astype(np.float32), 0.12)
        pup = vec(pupil.astype(np.float32), 0.45)
        ys, xs = np.nonzero(white | pupil)
        top, bot, left, right = ys.min() - 2, ys.max() + 3, xs.min() - 3, xs.max() + 3
        ly = ys.min() + (ys.max() - ys.min()) * 0.55
        cid = f'olho{i}'
        out.append(
            f'<clipPath id="{cid}"><path d="{union}"/></clipPath>'
            f'<clipPath id="{cid}b"><path d="{union_big}"/></clipPath>'
            f'<path d="{union}" fill="{hexc(PAL["white"])}"/>'
            f'<g clip-path="url(#{cid})">'
            f'<path d="{pup}" fill="{hexc(PAL["pupil"])}">'
            # revira os olhos (sobe e some sob a pálpebra), junto com a bufada
            f'<animateTransform attributeName="transform" type="translate" dur="7.5s" repeatCount="indefinite" '
            f'values="0 0;0 0;-3 -10;-3 -10;0 0;0 0" keyTimes="0;.62;.66;.78;.83;1"/></path></g>'
            # piscada pesada: a pálpebra desce e aparece o traço do olho fechado
            f'<g clip-path="url(#{cid}b)"><rect x="{left}" y="{top}" width="{right - left}" height="0" fill="{hexc(PAL["body"])}">'
            f'<animate attributeName="height" dur="4.3s" repeatCount="indefinite" '
            f'values="0;0;{bot - top};{bot - top};0" keyTimes="0;.9;.94;.96;1"/></rect></g>'
            f'<path d="M{left + 3},{ly:.1f} Q{(left + right) / 2:.1f},{ly + 5:.1f} {right - 3},{ly:.1f}" fill="none" '
            f'stroke="#3E180B" stroke-width="3.2" stroke-linecap="round" opacity="0">'
            f'<animate attributeName="opacity" dur="4.3s" repeatCount="indefinite" values="0;0;1;1;0;0" keyTimes="0;.935;.94;.96;.965;1"/></path>')
    return ''.join(out)


def puff(x, y, delay, dx):
    """Bufada de irritação saindo da cabeça."""
    return (f'<g opacity="0" transform="translate({x} {y})">'
            f'<g fill="#FFFFFF" stroke="#CDBBA3" stroke-width="1.5"><circle r="13"/><circle cx="{13 * dx}" cy="-9" r="10"/><circle cx="{-9 * dx}" cy="-13" r="9"/></g>'
            f'<animate attributeName="opacity" dur="7.5s" begin="{delay}s" repeatCount="indefinite" values="0;0;1;0;0" keyTimes="0;.66;.7;.84;1"/>'
            f'<animateTransform attributeName="transform" type="translate" additive="sum" dur="7.5s" begin="{delay}s" repeatCount="indefinite" '
            f'values="0 0;0 0;{4 * dx} -6;{14 * dx} -30;{14 * dx} -30" keyTimes="0;.66;.7;.84;1"/>'
            f'</g>')


def build(src, dst):
    rgb, alpha, label = load(src)
    h, w = alpha.shape
    P = parts(alpha, label)
    torso_region = (alpha > 0.02) & ~P['tail'] & ~P['back_leg'] & ~P['front_leg']
    torso = layer(alpha, label, torso_region, skip=('white', 'pupil'))
    tail = layer(alpha, label, P['tail'],
                 ext=f'<polygon points="{crop_pts([(116, 846), (132, 846), (152, 860), (132, 876), (116, 872)])}" fill="{hexc(PAL["brown"])}"/>')
    back_leg = layer(alpha, label, P['back_leg_draw'],
                     ext=f'<polygon points="{crop_pts([(112, 872), (192, 902), (200, 858), (120, 842)])}" fill="{hexc(PAL["shade"])}"/>')
    front_leg = layer(alpha, label, P['front_leg_draw'],
                      ext=f'<polygon points="{crop_pts([(186, 904), (275, 868), (302, 868), (292, 832), (200, 846)])}" fill="{hexc(PAL["body"])}"/>')
    olhos = eyes(alpha, label, h, w)

    def pivot(x, y):
        return x - X0, y - Y0

    T = 1.5  # um ciclo = dois passos, devagar e sem vontade
    hb = pivot(150, 865)
    hf = pivot(232, 868)
    tb = pivot(130, 858)

    def rot(px, py, values, key, dur=T, begin=0):
        vals = ';'.join(f'{v} {px} {py}' for v in values)
        return (f'<animateTransform attributeName="transform" type="rotate" dur="{dur}s" begin="{begin}s" repeatCount="indefinite" '
                f'values="{vals}" keyTimes="{key}" calcMode="spline" keySplines="{";".join([".45 0 .55 1"] * (len(values) - 1))}"/>')

    def lift(values, key):
        return (f'<animateTransform attributeName="transform" type="translate" dur="{T}s" repeatCount="indefinite" '
                f'values="{values}" keyTimes="{key}"/>')

    mamu = f'''
      <g id="rabo">{rot(*tb, [-10, 12, -10], "0;.5;1", T, -.2)}{tail}</g>
      <g id="perna-tras">{rot(*hb, [0, -11, -22, 0], "0;.25;.5;1")}
        <g>{lift("0 0;0 -11;0 0;0 0", "0;.25;.5;1")}{back_leg}</g></g>
      <g id="perna-frente">{rot(*hf, [0, 22, 11, 0], "0;.5;.75;1")}
        <g>{lift("0 0;0 0;0 -11;0 0", "0;.5;.75;1")}{front_leg}</g></g>
      <g id="corpo">
        <animateTransform attributeName="transform" type="translate" dur="{T}s" repeatCount="indefinite"
          values="0 4;0 -2;0 4;0 -2;0 4" keyTimes="0;.25;.5;.75;1" calcMode="spline"
          keySplines=".4 0 .6 1;.4 0 .6 1;.4 0 .6 1;.4 0 .6 1"/>
        {torso}
        {olhos}
        {puff(70, 66, 0, -1)}{puff(304, 76, 0.05, 1)}
        <path d="M0,-12 C5,-3 8,2 8,6 a8,8 0 0 1 -16,0 C-8,2 -5,-3 0,-12Z" fill="#8ED0F2" opacity="0">
          <animate attributeName="opacity" dur="6s" begin="1.2s" repeatCount="indefinite" values="0;1;1;0;0" keyTimes="0;.05;.3;.4;1"/>
          <animateTransform attributeName="transform" type="translate" dur="6s" begin="1.2s" repeatCount="indefinite"
            values="296 92;296 92;303 128;305 136;305 136" keyTimes="0;.05;.3;.4;1"/>
        </path>
      </g>'''

    poeira = ''
    for x, y, b in ((262, 446, 0), (160, 442, T / 2)):
        poeira += (f'<g transform="translate({x} {y})"><g fill="#E3D4B9">'
                   f'<circle cx="-10" r="6"/><circle cx="2" cy="-3" r="8"/><circle cx="14" r="5"/>'
                   f'<animateTransform attributeName="transform" type="translate" dur="{T}s" begin="{b}s" repeatCount="indefinite" values="0 0;-26 -4" keyTimes="0;1"/></g>'
                   f'<animate attributeName="opacity" dur="{T}s" begin="{b}s" repeatCount="indefinite" values=".9;0;0" keyTimes="0;.45;1"/></g>')

    falas = ['Tô indo.', 'Reclamando, mas tô indo.', 'Quem inventou caminhada?', 'Preferia o sofá.']
    balao = ''
    for i, t in enumerate(falas):
        wbox = 34 + len(t) * 11.2
        balao += (f'<g opacity="0"><animate attributeName="opacity" dur="22s" begin="{1 + i * 5.5}s" repeatCount="indefinite" '
                  f'values="0;1;1;0;0" keyTimes="0;.02;.15;.17;1"/>'
                  f'<rect x="600" y="58" width="{wbox:.0f}" height="52" rx="26" fill="#FFFFFF"/>'
                  f'<path d="M620,104 L596,134 L640,108Z" fill="#FFFFFF"/>'
                  f'<text x="{600 + wbox / 2:.0f}" y="91" text-anchor="middle">{t}</text></g>')

    chao = ''
    for k in range(2):
        ox = k * 960
        for x, kind in ((40, 't'), (150, 'p'), (230, 't'), (390, 'p'), (470, 't'), (610, 'p'), (700, 't'), (820, 'p'), (900, 't')):
            if kind == 't':
                chao += (f'<path d="M{ox + x},562 l-6,-12 M{ox + x + 4},562 l1,-15 M{ox + x + 8},562 l7,-11" '
                         f'stroke="#A8A06A" stroke-width="3" stroke-linecap="round" fill="none"/>')
            else:
                chao += f'<ellipse cx="{ox + x}" cy="{570 + (x % 3) * 6}" rx="7" ry="4" fill="#DCCBAA"/>'

    svg = f'''<svg viewBox="0 0 960 620" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="t d">
  <title id="t">Mamu caminhando de má vontade</title>
  <desc id="d">O mamute Mamu caminha devagar, revira os olhos, bufa e reclama enquanto o chão passa.</desc>
  <style>text{{font:600 21px Inter, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;fill:#4A1D0D}}</style>
  <rect width="960" height="620" fill="#F6EFE4"/>
  <g fill="#FFFFFF" opacity=".75">
    <g><ellipse cx="160" cy="90" rx="46" ry="16"/><ellipse cx="186" cy="80" rx="28" ry="16"/>
      <animateTransform attributeName="transform" type="translate" dur="60s" repeatCount="indefinite" values="200 0;-400 0"/></g>
    <g><ellipse cx="760" cy="150" rx="40" ry="13"/><ellipse cx="782" cy="142" rx="22" ry="12"/>
      <animateTransform attributeName="transform" type="translate" dur="60s" repeatCount="indefinite" values="300 0;-900 0"/></g>
  </g>
  <path d="M0,470 Q160,420 320,465 T640,455 T960,462 V560 H0Z" fill="#EFE4D1"/>
  <rect y="545" width="960" height="75" fill="#EADCC4"/>
  <rect y="545" width="960" height="3" fill="#D9C6A5"/>
  <g>{chao}
    <animateTransform attributeName="transform" type="translate" dur="21s" repeatCount="indefinite" values="0 0;-960 0"/></g>
  <g>
    <g transform="translate(1000 0)">
      <rect x="-5" y="430" width="10" height="118" fill="#8A5A3A"/>
      <path d="M-92,438 H40 V472 H-92 L-108,455Z" fill="#F3E6CC"/>
      <path d="M-40,482 H92 L108,499 L92,516 H-40Z" fill="#F3E6CC"/>
      <text x="-28" y="462" text-anchor="middle" style="font-size:16px">SOFÁ 0,2 km</text>
      <text x="30" y="506" text-anchor="middle" style="font-size:16px">PARQUE 3 km</text>
    </g>
    <animateTransform attributeName="transform" type="translate" dur="28s" repeatCount="indefinite" values="0 0;-1250 0"/>
  </g>
  <g transform="translate(250 111)">
    <ellipse cx="200" cy="442" rx="120" ry="9" fill="#000" opacity=".08"/>
    {poeira}
    <g>
      <animateTransform attributeName="transform" type="rotate" dur="{T}s" repeatCount="indefinite"
        values="-1.4 200 440;1.4 200 440;-1.4 200 440" keyTimes="0;.5;1" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>
      {mamu}
    </g>
  </g>
  {balao}
</svg>'''

    html = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mamu caminhando</title>
<style>
  :root {{ --bg: #F6EFE4; --ink: #4A1D0D; --ink2: #8A5A44; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; min-height: 100vh; display: grid; place-items: center; background: var(--bg);
         font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; color: var(--ink); }}
  main {{ width: min(960px, 100% - 32px); padding: 24px 0; }}
  h1 {{ font-size: 22px; margin: 0 0 4px; }}
  p {{ margin: 0 0 16px; color: var(--ink2); }}
  svg {{ width: 100%; height: auto; display: block; border-radius: 16px; }}
  button {{ margin-top: 12px; font: inherit; font-weight: 600; color: var(--ink); background: #fff;
           border: 1px solid #E2D3BC; border-radius: 999px; padding: 8px 18px; cursor: pointer; }}
</style>
</head>
<body>
<main>
  <h1>Mamu · caminhada resmungando</h1>
  <p>Ele vai. Reclamando, mas vai.</p>
  {svg}
  <button id="play" type="button">Pausar</button>
</main>
<script>
  const svg = document.querySelector('svg');
  const btn = document.getElementById('play');
  const setPaused = (p) => {{ p ? svg.pauseAnimations() : svg.unpauseAnimations(); btn.textContent = p ? 'Continuar' : 'Pausar'; }};
  btn.addEventListener('click', () => setPaused(!svg.animationsPaused()));
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) setPaused(true);
</script>
</body>
</html>
'''
    with open(dst, 'w', encoding='utf-8') as fh:
        fh.write(html)


if __name__ == '__main__':
    aqui = os.path.dirname(os.path.abspath(__file__))
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(aqui, '..', '..', '..', 'arte', 'mamu-v2.png')
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(aqui, '..', 'mamu-caminhando.html')
    build(src, dst)
