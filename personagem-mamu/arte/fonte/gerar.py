"""
Gera todas as artes do Mamu v2.

    cd personagem-mamu/arte/fonte
    python3 gerar.py          # SVGs + PNGs (PNG precisa de node + playwright)

Saídas:
    arte/mamu-v2-frente.svg|png        personagem isolado, fundo transparente, camadas nomeadas
    arte/mamu-v2-turnaround.svg|png    frente, 3/4, perfil, costas
    arte/mamu-v2-poses.svg|png         poses de personalidade
    arte/mamu-v2-expressoes.svg|png    expressões (cabeça)
    arte/mamu-v1-vs-v2.png             comparação com a arte original
    motion/M00-idle/mamu-idle.svg      loop animado (respiração, piscada, fumaça)
"""
import os
import shutil
import subprocess
import textwrap

import mamu
from mamu import C, front, three_q, side, back, ground, uid
from props import smoke, cigarette, FONT
from poses import POSES
from expressoes import EXPRESSOES

HERE = os.path.dirname(os.path.abspath(__file__))
ARTE = os.path.dirname(HERE)
RAIZ = os.path.dirname(ARTE)
BG = '#F6EFE4'
INK = '#4A1D0D'
INK2 = '#8A5A44'


def svg_doc(w, h, body, bg=BG):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
    if bg:
        s += f'<rect width="{w}" height="{h}" fill="{bg}"/>'
    return s + body + '</svg>'


def text(x, y, s, size=16, weight=400, color=INK, anchor='middle', italic=False):
    st = ' font-style="italic"' if italic else ''
    s = s.replace('&', '&amp;').replace('<', '&lt;')
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}"{st}>{s}</text>')


def header(title, subtitle, w):
    return (text(48, 66, 'MAMU', 40, 800, INK, 'start')
            + f'<rect x="196" y="39" width="44" height="30" rx="15" fill="#F5B700"/>'
            + text(218, 60, 'v2', 16, 800, INK)
            + text(256, 64, title, 24, 700, INK, 'start')
            + text(48, 102, subtitle, 17, 400, INK2, 'start'))


def prancha(items, cols, title, subtitle, cw=400, ch=480, cap=96, top=136, crop=None):
    """items: [(rótulo, legenda, svg)]. crop=(x, y) recorta a célula 400x480 a partir desse ponto."""
    rows = (len(items) + cols - 1) // cols
    W, H = cols * cw, top + rows * (ch + cap) + 24
    body = header(title, subtitle, W)
    for i, (label, sub, inner) in enumerate(items):
        x, y = (i % cols) * cw, top + (i // cols) * (ch + cap)
        cid = uid('cell')
        dx, dy = crop or (0, 0)
        body += (f'<g transform="translate({x} {y})"><clipPath id="{cid}"><rect width="{cw}" height="{ch}"/></clipPath>'
                 f'<g clip-path="url(#{cid})"><g transform="translate({-dx} {-dy})">{"" if crop else ground()}{inner}</g></g>')
        body += text(cw / 2, ch + 30, label, 19, 700)
        for j, line in enumerate(textwrap.wrap(sub, 42 if cw >= 400 else 30)):
            body += text(cw / 2, ch + 56 + j * 21, line, 15, 400, INK2, italic=True)
        body += '</g>'
    return svg_doc(W, H, body)


def idle_svg():
    """Loop de idle: respira, pisca e fuma. Usa a pose 'Só hoje'."""
    blink = ''
    for cx in (155, 245):
        blink += f'<ellipse cx="{cx}" cy="176" rx="25.6" ry="23.6" fill="{C["body"]}"/>'
        blink += (f'<path d="M{cx-24},178 Q{cx},186 {cx+24},178" fill="none" stroke="{C["line"]}" '
                  f'stroke-width="4.8" stroke-linecap="round"/>')
    inner = front(dict(
        eyes={'both': dict(lid=0.56, tilt=0.04, pdx=6, pdy=5)},
        brow_l=(128, 150, 182, 156), brow_r=(218, 150, 272, 138), mouth='flat',
        arms={'l': [(106, 258), (88, 294), (82, 330), (90, 358)], 'r': [(292, 268), (330, 300), (330, 262), (310, 238)]},
        arms_w={'l': [26, 34, 44], 'r': [26, 32, 40]},
        after_eyes=f'<g class="piscada">{blink}</g>',
        props=cigarette(304, 238, ang=-128, L=46, smoke_on=False),
    ))
    tip = (276, 202)  # ponta acesa do cigarro
    fum = smoke(tip[0], tip[1] - 6, 70, 'fumaca f1') + smoke(tip[0], tip[1] - 6, 70, 'fumaca f2')
    css = """
    .mamu { transform-origin: 200px 452px; animation: respira 3.6s ease-in-out infinite; }
    .piscada { opacity: 0; animation: pisca 5.2s steps(1, end) infinite; }
    .fumaca { opacity: 0; transform-box: fill-box; transform-origin: 50% 100%; animation: sobe 3.2s ease-out infinite; }
    .f2 { animation-delay: 1.6s; }
    .brasa { animation: brasa 3.2s ease-in-out infinite; }
    @keyframes respira { 0%, 100% { transform: scale(1, 1); } 45% { transform: scale(1.012, 1.024); } }
    @keyframes pisca { 0% { opacity: 0; } 90% { opacity: 1; } 93% { opacity: 0; } 96% { opacity: 1; } 98% { opacity: 0; } }
    @keyframes sobe { 0% { opacity: 0; transform: translateY(14px) scaleY(.6); } 25% { opacity: 1; }
                      100% { opacity: 0; transform: translateY(-30px) scaleY(1.1); } }
    @keyframes brasa { 0%, 100% { fill: #F0662C; } 50% { fill: #FFB347; } }
    @media (prefers-reduced-motion: reduce) { .mamu, .piscada, .fumaca, .brasa { animation: none; } .fumaca { opacity: .6; } }
    """
    body = f'<style>{css}</style>{ground()}<g class="mamu">{inner}</g>{fum}'
    return svg_doc(400, 480, body)


def comparar(saida):
    """v1 (recorte da arte original) ao lado da v2, mesma altura."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print('  (PIL ausente: pulando comparação)')
        return
    orig = Image.open(os.path.join(ARTE, 'referencia', 'mamu-v1-original.png')).convert('RGBA').crop((38, 43, 391, 481))
    nova = Image.open(os.path.join(ARTE, 'mamu-v2-frente.png')).convert('RGBA')
    nova = nova.crop(nova.getbbox())
    h = 760
    orig = orig.resize((round(orig.width * h / orig.height), h), Image.LANCZOS)
    nova = nova.resize((round(nova.width * h / nova.height), h), Image.LANCZOS)
    W, H = 1600, 1000
    img = Image.new('RGBA', (W, H), BG)
    img.alpha_composite(orig, (400 - orig.width // 2, 110))
    img.alpha_composite(nova, (1200 - nova.width // 2, 110))
    d = ImageDraw.Draw(img)
    def fonte(padrao, tamanho):
        try:
            caminho = subprocess.run(['fc-match', '-f', '%{file}', padrao], capture_output=True, text=True).stdout
            return ImageFont.truetype(caminho, tamanho)
        except (OSError, FileNotFoundError):
            return ImageFont.load_default()
    bold, reg = fonte('Inter:bold', 34), fonte('Inter', 22)
    for cx, t, s in ((400, 'v1 — original', 'mamute emburrado'),
                     (1200, 'v2 — redesign', 'barriga, olheiras, pálpebra pesada, orelha caída')):
        d.text((cx, 920), t, font=bold, fill=INK, anchor='mm')
        d.text((cx, 962), s, font=reg, fill=INK2, anchor='mm')
    img.convert('RGB').save(saida)


def png(svg_path, scale=1):
    if not shutil.which('node'):
        return
    out = svg_path[:-4] + '.png'
    subprocess.run(['node', os.path.join(HERE, 'render.js'), svg_path, out, str(scale)], check=True)
    print('  ', os.path.relpath(out, RAIZ))


def salvar(path, content, scale=1, render=True):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(content)
    print('  ', os.path.relpath(path, RAIZ))
    if render:
        png(path, scale)


def main():
    # personagem isolado, com camadas nomeadas
    mamu.NAMED_LAYERS = True
    salvar(os.path.join(ARTE, 'mamu-v2-frente.svg'), svg_doc(400, 480, f'<g id="mamu">{front()}</g>', bg=None), scale=2)
    mamu.NAMED_LAYERS = False

    salvar(os.path.join(ARTE, 'mamu-v2-turnaround.svg'), prancha([
        ('Frente', 'pálpebra pesada, olheira, boca torta', front()),
        ('3/4', 'a barriga chega antes dele', three_q()),
        ('Perfil', 'a tromba descansa na barriga', side()),
        ('Costas', 'pneuzinho e rabo', back()),
    ], 4, 'turnaround', 'Barriga projetada · olheiras · pálpebra pesada · orelhas caídas · cabelo de quem não dormiu'))

    salvar(os.path.join(ARTE, 'mamu-v2-poses.svg'), prancha(
        [(t, s, g) for t, s, g in POSES.values()], 4, 'poses de personalidade',
        'O humor vem da contradição: ele dá o conselho certo enquanto faz o contrário.'))

    salvar(os.path.join(ARTE, 'mamu-v2-expressoes.svg'), prancha(
        [(t, '', g) for t, g in EXPRESSOES.values()], 4, 'expressões',
        'Referência facial para animação. Olheira e pálpebra pesada ficam em todas.',
        cw=300, ch=272, cap=44, crop=(50, 22)))

    salvar(os.path.join(RAIZ, 'motion', 'M00-idle', 'mamu-idle.svg'), idle_svg(), render=False)

    if os.path.exists(os.path.join(ARTE, 'mamu-v2-frente.png')):
        comparar(os.path.join(ARTE, 'mamu-v1-vs-v2.png'))
        print('   arte/mamu-v1-vs-v2.png')


if __name__ == '__main__':
    main()
