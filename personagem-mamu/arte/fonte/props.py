"""Objetos de cena do Mamu (cigarro, celular, delivery, controle...)."""
import math

from geom import stroke, f
from mamu import uid

FONT = 'Inter, Helvetica, Arial, sans-serif'


def smoke(x, y, h=70, cls=''):
    c = f' class="{cls}"' if cls else ''
    g = f'<g{c}>'
    g += stroke([(x, y), (x - 6, y - h * .3), (x + 6, y - h * .6), (x - 2, y - h)], 5, '#B9AEA4', ' opacity=".55"')
    g += stroke([(x + 8, y - h * .45), (x + 16, y - h * .7), (x + 10, y - h * .95)], 3.5, '#B9AEA4', ' opacity=".4"')
    return g + '</g>'


def cigarette(x, y, ang=-50, L=46, smoke_on=True):
    """(x, y) = ponta do filtro; ang em graus."""
    g = f'<g transform="translate({f(x)} {f(y)}) rotate({ang})">'
    g += f'<rect x="0" y="-5.5" width="{L}" height="11" rx="2.5" fill="#FBF8F3"/>'
    g += '<rect x="0" y="-5.5" width="14" height="11" rx="2.5" fill="#E0A55A"/>'
    g += f'<rect x="{L-7}" y="-5.5" width="7" height="11" fill="#9A918A"/>'
    g += f'<circle class="brasa" cx="{L}" cy="0" r="5.5" fill="#F0662C"/>'
    g += '</g>'
    if smoke_on:
        a = math.radians(ang)
        g += smoke(x + L * math.cos(a), y + L * math.sin(a) - 8)
    return g


def phone(x, y, ang=-12):
    g = f'<g transform="translate({f(x)} {f(y)}) rotate({ang})">'
    g += '<rect x="-20" y="-34" width="40" height="68" rx="8" fill="#22201F"/>'
    g += '<rect x="-16" y="-29" width="32" height="56" rx="5" fill="#9ED6FF"/>'
    g += '<rect x="-11" y="-22" width="22" height="5" rx="2.5" fill="#fff" opacity=".7"/>'
    g += '<rect x="-11" y="-12" width="16" height="5" rx="2.5" fill="#fff" opacity=".5"/>'
    g += '<rect x="-11" y="-2" width="20" height="14" rx="3" fill="#fff" opacity=".35"/>'
    return g + '</g>'


def delivery_bag(x, y, ang=6):
    g = f'<g transform="translate({f(x)} {f(y)}) rotate({ang})">'
    g += '<path d="M-36,-58 L36,-58 L40,0 L-40,0Z" fill="#D9B07A"/>'
    g += '<path d="M-36,-58 l9,-10 l9,10 l9,-10 l9,10 l9,-10 l9,10 l9,-10 l9,10Z" fill="#C79A61"/>'
    g += '<ellipse cx="-12" cy="-22" rx="11" ry="8" fill="#B8864A" opacity=".7"/>'  # mancha de gordura
    g += '<path d="M8,-40 a10,10 0 1 1 0.1,0" fill="none" stroke="#fff" stroke-width="3" opacity=".75"/>'
    return g + '</g>'


def remote(x, y, ang=-20):
    g = f'<g transform="translate({f(x)} {f(y)}) rotate({ang})">'
    g += '<rect x="-12" y="-36" width="24" height="72" rx="8" fill="#2B2826"/>'
    g += '<circle cx="0" cy="-22" r="5" fill="#E5533B"/>'
    g += ''.join(f'<rect x="-7" y="{-8+i*10}" width="14" height="5" rx="2.5" fill="#6B6560"/>' for i in range(3))
    return g + '</g>'


def sweat(x, y, s=1.0, ang=0):
    return (f'<path transform="translate({f(x)} {f(y)}) rotate({ang}) scale({s})" '
            f'd="M0,-14 C6,-4 9,2 9,6 a9,9 0 0 1 -18,0 C-9,2 -6,-4 0,-14Z" fill="#8ED0F2"/>')


def headband(cx, cy, r, y1=118, y2=136, col='#F5B700'):
    """Faixa de testa — amarelo BeeOut."""
    cid = uid('hb')
    return (f'<clipPath id="{cid}"><circle cx="{cx}" cy="{cy}" r="{r+3}"/></clipPath>'
            f'<g clip-path="url(#{cid})"><path d="M{cx-r-10},{y1+8} Q{cx},{y1-10} {cx+r+10},{y1+8} '
            f'L{cx+r+10},{y2+8} Q{cx},{y2-10} {cx-r-10},{y2+8}Z" fill="{col}"/>'
            f'<path d="M{cx-r-10},{(y1+y2)/2+8} Q{cx},{(y1+y2)/2-10} {cx+r+10},{(y1+y2)/2+8}" '
            f'stroke="#fff" stroke-width="3" fill="none" opacity=".6"/></g>')


def moon(x, y, r=20, bg='#F6EFE4'):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="#E9D9A6"/><circle cx="{x+9}" cy="{y-6}" r="{r-2}" fill="{bg}"/>'


def note(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})" fill="#6B2C15">'
            f'<ellipse cx="0" cy="0" rx="7" ry="5.5" transform="rotate(-20)"/>'
            f'<rect x="5" y="-26" width="3" height="26"/><path d="M8,-26 q10,4 9,14 q-3,-7 -9,-8z"/></g>')


def qmark(x, y):
    return f'<text x="{x}" y="{y}" font-size="54" font-weight="800" font-family="{FONT}" fill="#6B2C15">?</text>'
