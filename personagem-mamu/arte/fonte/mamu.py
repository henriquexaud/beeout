"""
Mamu v2 — construção do personagem em SVG.

Cada vista (frente, 3/4, perfil, costas) é desenhada numa célula de 400x480
com o chão em y=452. As poses são variações da vista de frente/3/4 passando
um dicionário de opções (olhos, sobrancelhas, boca, braços, tromba, props).

Estilo: formas chapadas, sem contorno, poucas cores. Tudo que é "membro"
(tromba, braços, presas, rabo, mechas de cabelo) é um traço afinado ao longo
de uma curva — ver geom.taper().
"""
import itertools

from geom import taper, stroke, f

# Paleta (derivada da arte v1, com acréscimo de olheira/barriga)
C = dict(
    body='#C4521C',     # laranja do corpo
    shade='#A8441A',    # sombra do corpo
    belly='#D2652B',    # barriga (um tom acima, só pra destacar o volume)
    brown='#6B2C15',    # tromba, braços, cabelo, sobrancelhas
    brown_d='#4A1D0D',  # rugas da tromba, separação entre braços
    ear_in='#93391A',   # interior da orelha
    cream='#F6DCB8',    # presas e unhas
    eye='#FBF5EC',      # branco do olho
    pupil='#1B110C',
    olheira='#7E3035',  # olheiras (puxado pro roxo de propósito)
    line='#3E180B',     # pálpebra e boca
)

# Quando True, as camadas viram <g id="..."> (útil pra importar no Figma/AE/Rive).
# Fica False nas pranchas, que repetem o personagem várias vezes.
NAMED_LAYERS = False

_uid = itertools.count()


def uid(p):
    return f'{p}{next(_uid)}'


def L(name, content):
    """Agrupa uma camada nomeada."""
    if NAMED_LAYERS:
        return f'<g id="{name}">{content}</g>'
    return f'<g data-layer="{name}">{content}</g>'


# ---------------------------------------------------------------- olhos

def eye(cx, cy, rx=21, ry=19, lid=0.5, tilt=0.0, pdx=0, pdy=4, pr=8.5, side=1,
        bags=True, closed=False, red=False):
    """
    lid    0 = aberto .. 1 = fechado (pálpebra pesada é ~0.47)
    tilt   inclinação da pálpebra; positivo = canto interno mais baixo (bravo),
           negativo = canto interno mais alto (cansado/triste)
    pdx/y  deslocamento da pupila
    side   -1 olho esquerdo (da tela), +1 direito
    closed False | 'relaxed' (∪) | 'tight' (∩, irritado)
    red    olho vermelho de madrugada
    """
    g = ''
    if bags and closed:
        g += (f'<path d="M{f(cx-rx)},{f(cy+8)} Q{f(cx)},{f(cy+ry+10)} {f(cx+rx)},{f(cy+8)} '
              f'Q{f(cx)},{f(cy+ry)} {f(cx-rx)},{f(cy+8)}Z" fill="{C["olheira"]}"/>')
    elif bags:
        g += (f'<path d="M{f(cx-rx-4)},{f(cy-2)} Q{f(cx-rx-2)},{f(cy+ry+11)} {f(cx)},{f(cy+ry+11)} '
              f'Q{f(cx+rx+2)},{f(cy+ry+11)} {f(cx+rx+4)},{f(cy-2)}Z" fill="{C["olheira"]}"/>')
        g += stroke([(cx - rx * 0.6, cy + ry + 18), (cx, cy + ry + 22), (cx + rx * 0.6, cy + ry + 18)],
                    3, C['olheira'], ' opacity="0.8"')
    if closed:
        if closed == 'tight':
            g += stroke([(cx - rx, cy + 7), (cx, cy + 1), (cx + rx, cy + 7)], 4.8, C['line'])
        else:
            g += stroke([(cx - rx, cy + 2), (cx, cy + 7), (cx + rx, cy + 2)], 4.8, C['line'])
        return g
    cid = uid('e')
    g += f'<clipPath id="{cid}"><ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}"/></clipPath>'
    g += f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="{"#F7DCD3" if red else C["eye"]}"/>'
    if red:
        g += (f'<g clip-path="url(#{cid})" opacity=".85" stroke="#D6402F" stroke-width="2.2" fill="none" stroke-linecap="round">'
              f'<path d="M{f(cx-rx)},{f(cy+4)} q8,-1 12,-5 M{f(cx-rx)},{f(cy+10)} q7,0 10,3 '
              f'M{f(cx+rx)},{f(cy+4)} q-8,-1 -12,-5 M{f(cx+rx)},{f(cy+10)} q-7,0 -10,3"/></g>')
    g += f'<circle cx="{f(cx+pdx)}" cy="{f(cy+pdy)}" r="{f(pr)}" fill="{C["pupil"]}" clip-path="url(#{cid})"/>'
    g += f'<circle cx="{f(cx+pdx+2.5)}" cy="{f(cy+pdy-2.5)}" r="2.2" fill="#fff" clip-path="url(#{cid})"/>'
    # pálpebra: reta y = y0 + s*(x - cx), preenchida com a cor do corpo
    y0 = cy - ry + lid * 2 * ry
    s = tilt * (-side)
    xa, xb = cx - rx - 4, cx + rx + 4
    ya, yb = y0 + s * (xa - cx), y0 + s * (xb - cx)
    cid2 = uid('l')
    g += f'<clipPath id="{cid2}"><ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx+1.6)}" ry="{f(ry+1.6)}"/></clipPath>'
    g += (f'<path d="M{f(xa)},{f(cy-ry-30)} L{f(xb)},{f(cy-ry-30)} L{f(xb)},{f(yb)} L{f(xa)},{f(ya)}Z" '
          f'fill="{C["body"]}" clip-path="url(#{cid2})"/>')
    g += stroke([(xa + 3, ya + s * 3), (xb - 3, yb - s * 3)], 4.2, C['line'])
    return g


def brow(x1, y1, x2, y2, w=11, mid=-2):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + mid
    return stroke([(x1, y1), (mx, my), (x2, y2)], w, C['brown'])


MOUTHS = {
    # boca fica à direita da tromba (o lado que aparece)
    'frown': lambda: stroke([(220, 252), (231, 248), (241, 255)], 4.4, C['line']),
    'smirk': lambda: stroke([(220, 251), (231, 254), (241, 247)], 4.4, C['line']),
    'flat': lambda: stroke([(220, 251), (240, 252)], 4.4, C['line']),
    'smile': lambda: stroke([(220, 248), (231, 255), (242, 249)], 4.4, C['line']),
    'o': lambda: f'<ellipse cx="232" cy="252" rx="6" ry="7" fill="{C["line"]}"/>',
    'yell': lambda: f'<path d="M220,246 Q232,240 244,248 Q240,262 228,260 Q221,256 220,246Z" fill="{C["line"]}"/>',
    'none': lambda: '',
}


# ---------------------------------------------------------------- peças

def nails(x, y, n=3, w=13, gap=4):
    g = ''
    tot = n * w + (n - 1) * gap
    sx = x - tot / 2
    for i in range(n):
        cx = sx + i * (w + gap) + w / 2
        g += f'<path d="M{f(cx-w/2)},{f(y)} A{f(w/2)},{f(w/2*0.9)} 0 0 1 {f(cx+w/2)},{f(y)}Z" fill="{C["cream"]}"/>'
    return g


def tusk(pts, w=(24, 18, 10, 3.5)):
    return taper(pts, list(w), C['cream'], cap0=False)


def tail(pts, w=(16, 9, 4)):
    return taper(pts, list(w), C['brown'])


def strands(lst, dx=0):
    return ''.join(taper([(x + dx, y) for x, y in pts], w, C['brown']) for pts, w in lst)


HAIR_FRONT = [
    ([(182, 112), (162, 92), (138, 84)], [30, 3]),
    ([(194, 108), (188, 78), (170, 58)], [32, 3]),
    ([(208, 108), (212, 74), (226, 54)], [32, 3]),
    ([(220, 112), (244, 92), (268, 90)], [28, 3]),
    ([(200, 114), (186, 126), (166, 132)], [26, 3]),   # franja caída na testa
    ([(216, 96), (236, 72), (256, 68)], [9, 2]),       # fio rebelde
]


def ground(cx=200, y=452, rx=130):
    return f'<ellipse cx="{cx}" cy="{y+2}" rx="{rx}" ry="12" fill="#000" opacity=".08"/>'


# ---------------------------------------------------------------- vistas

def front(o=None):
    """
    Vista de frente. Opções principais:
      eyes={'both'|'l'|'r': {...eye()}}, brow_l/brow_r=(x1,y1,x2,y2),
      mouth=chave de MOUTHS, blush=True,
      arms={'l': [...], 'r': [...]}, arms_w, arms_cross=True,
      trunk=[...], trunk_w=[...], trunk_front=True (tromba na frente dos braços),
      props_mid (entre corpo e braços), props (por cima de tudo), after_eyes.
    """
    o = dict(o or {})
    G = 452
    eyes = o.get('eyes', {})

    lgid = uid('lg')
    legs = f'<rect x="128" y="372" width="62" height="{G-372}" rx="22"/><rect x="210" y="372" width="62" height="{G-372}" rx="22"/>'
    pernas = f'<clipPath id="{lgid}">{legs}</clipPath><g fill="{C["body"]}">{legs}</g>'
    pernas += f'<ellipse cx="200" cy="404" rx="112" ry="16" fill="{C["shade"]}" clip-path="url(#{lgid})"/>'  # sombra da barriga
    pernas += nails(159, G) + nails(241, G)

    orelhas = ''
    for s in (-1, 1):  # orelhas caídas, atrás da cabeça
        ex = 200 + s * 90
        orelhas += (f'<g transform="rotate({s*-24} {f(ex)} 186)"><ellipse cx="{f(ex)}" cy="186" rx="33" ry="38" fill="{C["body"]}"/>'
                    f'<ellipse cx="{f(ex+s*5)}" cy="190" rx="20" ry="25" fill="{C["ear_in"]}"/></g>')

    bid = uid('b')
    body = '<ellipse cx="200" cy="306" rx="126" ry="100"/><circle cx="200" cy="176" r="92"/>'
    corpo = f'<clipPath id="{bid}">{body}</clipPath><g fill="{C["body"]}">{body}</g>'
    barriga = f'<g clip-path="url(#{bid})">'
    barriga += f'<ellipse cx="200" cy="344" rx="100" ry="68" fill="{C["shade"]}" opacity=".5"/>'
    barriga += f'<ellipse cx="200" cy="338" rx="96" ry="66" fill="{C["belly"]}"/>'
    barriga += f'<circle cx="200" cy="188" r="92" fill="{C["shade"]}" opacity=".5"/>'  # sombra do queixo
    barriga += '</g>'
    barriga += stroke([(193, 372), (200, 376), (207, 372)], 3.6, C['shade'])  # umbigo
    cabeca = f'<circle cx="200" cy="176" r="92" fill="{C["body"]}"/>'

    base = dict(lid=0.47, tilt=0.13, pdx=5, pdy=6, rx=24, ry=22, pr=10)
    le = dict(base); le.update(eyes.get('both', {})); le.update(eyes.get('l', {}))
    re_ = dict(base); re_.update(eyes.get('both', {})); re_.update(eyes.get('r', {}))
    olhos = eye(155, 176, side=-1, **le) + eye(245, 176, side=1, **re_)
    sobr = brow(*o.get('brow_l', (128, 146, 182, 155))) + brow(*o.get('brow_r', (218, 154, 272, 142)))
    presas = ''.join(tusk([(200 + s * 14, 260), (200 + s * 44, 280), (200 + s * 68, 270), (200 + s * 80, 248)]) for s in (-1, 1))
    boca = MOUTHS[o.get('mouth', 'frown')]()
    if o.get('blush'):
        boca += ''.join(f'<ellipse cx="{x}" cy="236" rx="17" ry="8" fill="#E0412F" opacity=".55"/>' for x in (142, 258))

    trunk = o.get('trunk', [(200, 192), (200, 232), (197, 278), (190, 318), (192, 350), (210, 360), (222, 344), (212, 330), (203, 338)])
    tromba = taper(trunk, o.get('trunk_w', [44, 38, 31, 25, 20, 16]), C['brown'])
    tromba += ''.join(stroke([(184, y), (200, y + 3), (216, y)], 2.6, C['brown_d'], ' opacity=".55"') for y in (222, 236))

    arms = o.get('arms', {
        'l': [(106, 258), (88, 294), (82, 330), (90, 358)],
        'r': [(294, 258), (312, 294), (318, 330), (310, 358)],
    })
    arms_w = o.get('arms_w', {'l': [26, 34, 44], 'r': [26, 34, 44]})
    bracos = ''
    for k in ('l', 'r'):
        if k == 'r' and o.get('arms_cross'):
            bracos += taper([(x, y + 5) for x, y in arms[k]], [w + 4 for w in arms_w[k]], C['brown_d'])
        bracos += taper(arms[k], arms_w[k], C['brown'])

    g = L('pernas', pernas) + L('orelhas', orelhas) + L('corpo', corpo + barriga + cabeca)
    g += L('cabelo', strands(HAIR_FRONT, o.get('hair_dx', 0)))
    g += L('olhos', olhos) + o.get('after_eyes', '') + L('sobrancelhas', sobr)
    g += L('presas', presas) + L('boca', boca)
    g += o.get('props_mid', '')
    g += (L('bracos', bracos) + L('tromba', tromba)) if o.get('trunk_front') else (L('tromba', tromba) + L('bracos', bracos))
    g += o.get('props', '')
    return g


def three_q(o=None):
    """Vista 3/4 virada para a direita da tela. walk=True põe as pernas em passo."""
    o = dict(o or {})
    G = 452
    eyes = o.get('eyes', {})
    g = tail([(132, 372), (106, 382), (88, 400), (86, 416)], (22, 13, 3))
    if o.get('walk'):
        g += f'<g transform="rotate(14 260 372)"><rect x="232" y="372" width="58" height="{G-376}" rx="22" fill="{C["shade"]}"/></g>'
        g += f'<g transform="rotate(-16 152 380)"><rect x="120" y="372" width="64" height="{G-384}" rx="22" fill="{C["body"]}"/>{nails(152, G-12)}</g>'
        g += f'<g transform="rotate(14 260 372)"><rect x="222" y="372" width="58" height="{G-376}" rx="22" fill="{C["body"]}"/>{nails(251, G-4, 2)}</g>'
    else:
        lgid = uid('lg')
        legs = f'<rect x="120" y="372" width="64" height="{G-372}" rx="22"/><rect x="222" y="372" width="58" height="{G-372}" rx="22"/>'
        g += f'<rect x="232" y="372" width="58" height="{G-372}" rx="22" fill="{C["shade"]}"/>'
        g += f'<clipPath id="{lgid}">{legs}</clipPath><g fill="{C["body"]}">{legs}</g>'
        g += f'<ellipse cx="214" cy="404" rx="118" ry="16" fill="{C["shade"]}" clip-path="url(#{lgid})"/>'
        g += nails(152, G) + nails(253, G, 2)
    arms = o.get('arms', {
        'l': [(108, 262), (92, 298), (88, 334), (96, 360)],
        'r': [(300, 266), (316, 300), (318, 334), (310, 358)],
    })
    arms_w = o.get('arms_w', {'l': [26, 34, 44], 'r': [24, 32, 40]})
    g += taper(arms['r'], arms_w['r'], C['brown'])  # braço de trás
    bid = uid('b')
    body = '<ellipse cx="200" cy="306" rx="124" ry="100"/><circle cx="214" cy="176" r="90"/>'
    g += f'<clipPath id="{bid}">{body}</clipPath>'
    g += f'<g transform="rotate(22 296 186)"><ellipse cx="296" cy="186" rx="24" ry="34" fill="{C["shade"]}"/></g>'
    g += (f'<g transform="rotate(-26 128 188)"><ellipse cx="128" cy="188" rx="35" ry="40" fill="{C["body"]}"/>'
          f'<ellipse cx="122" cy="192" rx="22" ry="27" fill="{C["ear_in"]}"/></g>')
    g += f'<g fill="{C["body"]}">{body}</g>'
    g += f'<g clip-path="url(#{bid})">'
    g += f'<ellipse cx="228" cy="344" rx="94" ry="68" fill="{C["shade"]}" opacity=".5"/>'
    g += f'<ellipse cx="230" cy="338" rx="88" ry="66" fill="{C["belly"]}"/>'
    g += f'<circle cx="214" cy="188" r="90" fill="{C["shade"]}" opacity=".5"/>'
    g += '</g>'
    g += f'<circle cx="214" cy="176" r="90" fill="{C["body"]}"/>'
    g += stroke([(228, 372), (235, 376), (242, 371)], 3.6, C['shade'])
    g += strands(HAIR_FRONT, o.get('hair_dx', 20))
    g += o.get('props_head', '')
    base = dict(lid=0.47, tilt=0.13, pdx=6, pdy=6, ry=22, pr=10)
    le = dict(base, rx=24); le.update(eyes.get('both', {})); le.update(eyes.get('l', {}))
    re_ = dict(base, rx=17, pr=9); re_.update(eyes.get('both', {})); re_.update(eyes.get('r', {}))
    g += eye(180, 176, side=-1, **le) + eye(276, 174, side=1, **re_)
    g += brow(*o.get('brow_l', (152, 146, 206, 155)))
    g += brow(*o.get('brow_r', (256, 152, 296, 142)), w=10)
    g += tusk([(244, 260), (270, 278), (290, 270), (300, 250)], [20, 15, 8, 3])  # presa de trás
    mouth = o.get('mouth', 'frown')
    g += {'frown': stroke([(256, 250), (266, 247), (275, 254)], 4.2, C['line']),
          'smirk': stroke([(256, 250), (266, 253), (275, 245)], 4.2, C['line'])}.get(mouth, '')
    g += tusk([(228, 260), (196, 282), (170, 272), (158, 250)])  # presa da frente (atrás da tromba)
    trunk = o.get('trunk', [(230, 192), (232, 236), (232, 280), (228, 320), (232, 350), (250, 358), (260, 342), (250, 330), (242, 338)])
    g += taper(trunk, o.get('trunk_w', [44, 38, 31, 25, 20, 16]), C['brown'])
    g += ''.join(stroke([(214, y), (231, y + 3), (247, y)], 2.6, C['brown_d'], ' opacity=".55"') for y in (222, 236))
    g += taper(arms['l'], arms_w['l'], C['brown'])
    g += o.get('props', '')
    return g


def side(o=None):
    """Perfil virado para a direita; postura ereta com a barriga projetada pra frente."""
    o = dict(o or {})
    G = 452
    g = tail([(110, 330), (88, 342), (72, 362), (70, 380)], (24, 15, 3))
    g += f'<rect x="150" y="372" width="58" height="{G-372}" rx="22" fill="{C["shade"]}"/>'
    lgid = uid('lg')
    legs = f'<rect x="196" y="372" width="64" height="{G-372}" rx="22"/>'
    g += f'<clipPath id="{lgid}">{legs}</clipPath><g fill="{C["body"]}">{legs}</g>'
    g += f'<ellipse cx="250" cy="402" rx="80" ry="18" fill="{C["shade"]}" clip-path="url(#{lgid})"/>'
    g += nails(240, G, 2)
    bid = uid('b')
    body = ('<ellipse cx="190" cy="304" rx="96" ry="104"/>'
            '<ellipse cx="246" cy="334" rx="96" ry="78"/>'
            '<circle cx="222" cy="176" r="86"/>')
    g += f'<clipPath id="{bid}">{body}</clipPath><g fill="{C["body"]}">{body}</g>'
    g += f'<g clip-path="url(#{bid})">'
    g += f'<ellipse cx="262" cy="342" rx="84" ry="74" fill="{C["shade"]}" opacity=".5"/>'
    g += f'<ellipse cx="270" cy="336" rx="74" ry="70" fill="{C["belly"]}"/>'
    g += f'<circle cx="222" cy="188" r="86" fill="{C["shade"]}" opacity=".5"/>'
    g += '</g>'
    g += f'<circle cx="222" cy="176" r="86" fill="{C["body"]}"/>'
    g += strands([
        ([(214, 104), (188, 86), (160, 86)], [30, 3]),
        ([(224, 98), (214, 70), (192, 54)], [30, 3]),
        ([(236, 100), (242, 70), (258, 54)], [28, 3]),
        ([(246, 106), (268, 98), (284, 108)], [22, 3]),
        ([(228, 94), (238, 64), (258, 48)], [8, 2]),
    ])
    g += (f'<g transform="rotate(18 176 200)"><ellipse cx="176" cy="200" rx="30" ry="42" fill="{C["shade"]}"/>'
          f'<ellipse cx="178" cy="204" rx="19" ry="29" fill="{C["ear_in"]}"/></g>')
    e = dict(lid=0.47, tilt=0.0, pdx=7, pdy=6, rx=16, ry=21, pr=9.5)
    e.update(o.get('eyes', {}).get('both', {}))
    g += eye(258, 170, side=1, **e)
    g += brow(*o.get('brow', (232, 142, 280, 148)), mid=-3)
    g += stroke([(272, 252), (282, 248), (292, 254)], 4.2, C['line'])
    trunk = o.get('trunk', [(294, 196), (306, 226), (310, 260), (318, 290), (334, 318), (346, 340), (336, 356), (322, 350), (326, 338)])
    g += taper(trunk, [42, 34, 28, 22, 18, 14], C['brown'])
    g += ''.join(stroke([(282, y + 2), (296, y + 2), (310, y - 4)], 2.6, C['brown_d'], ' opacity=".55"') for y in (212, 228))
    g += tusk([(290, 258), (310, 280), (334, 274), (348, 252)])
    g += taper(o.get('arm', [(196, 262), (190, 300), (194, 336), (206, 362)]), [28, 36, 44], C['brown'])
    g += o.get('props', '')
    return g


def back(o=None):
    """Costas: sem rosto, mostra o pneuzinho dos lados e o rabo."""
    G = 452
    g = ''
    legs = f'<rect x="128" y="372" width="62" height="{G-372}" rx="22"/><rect x="210" y="372" width="62" height="{G-372}" rx="22"/>'
    g += f'<g fill="{C["body"]}">{legs}</g>'
    g += f'<rect x="128" y="372" width="62" height="34" fill="{C["shade"]}"/><rect x="210" y="372" width="62" height="34" fill="{C["shade"]}"/>'
    for s in (-1, 1):
        ex = 200 + s * 90
        g += f'<g transform="rotate({s*-24} {f(ex)} 186)"><ellipse cx="{f(ex)}" cy="186" rx="33" ry="38" fill="{C["shade"]}"/></g>'
    for pts in ([(106, 258), (88, 294), (82, 330), (90, 358)], [(294, 258), (312, 294), (318, 330), (310, 358)]):
        g += taper(pts, [26, 34, 44], C['brown'])
    body = '<ellipse cx="200" cy="306" rx="126" ry="100"/><circle cx="200" cy="176" r="92"/>'
    bid = uid('b')
    g += f'<clipPath id="{bid}">{body}</clipPath><g fill="{C["body"]}">{body}</g>'
    g += f'<g clip-path="url(#{bid})"><circle cx="200" cy="188" r="92" fill="{C["shade"]}" opacity=".35"/>'
    g += stroke([(100, 360), (118, 372), (136, 376)], 4, C['shade'], ' opacity=".7"')
    g += stroke([(300, 360), (282, 372), (264, 376)], 4, C['shade'], ' opacity=".7"')
    g += '</g>'
    g += f'<circle cx="200" cy="176" r="92" fill="{C["body"]}"/>'
    g += strands([
        ([(200, 108), (182, 80), (160, 62)], [30, 3]),
        ([(206, 104), (214, 72), (232, 56)], [30, 3]),
        ([(190, 112), (164, 98), (140, 96)], [26, 3]),
        ([(212, 112), (238, 100), (262, 104)], [26, 3]),
    ])
    g += tail([(200, 346), (202, 372), (214, 390), (230, 394)], (22, 14, 3))
    return g
