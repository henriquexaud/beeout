"""
Mamu v2 = arte original (v1) + olheiras e mau humor mais explícito.

Edita a própria imagem da v1, pintando por cima só o necessário, para manter
formato, traço e cores idênticos. Também limpa os pontinhos soltos do recorte.

    pip install pillow numpy opencv-python-headless
    python3 editar.py            # referencia/mamu-v1-original.png -> mamu-v2.png

As coordenadas de cada pose estão em main(); os parâmetros de pálpebra
e olheira ficam em eye().
"""
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

SS = 4  # supersampling para bordas suaves

BODY = (198, 83, 30)
BROWN = (104, 40, 16)
LINE = (112, 40, 16)
LID_LINE = (60, 24, 12)
PUPIL = (26, 28, 32)
WHITE = (250, 250, 250)
OLHEIRA = (124, 46, 52)


class Canvas:
    def __init__(self, path):
        self.a = np.array(Image.open(path).convert('RGBA')).astype(np.float32)
        self.H, self.W = self.a.shape[:2]

    # ------------------------------------------------------------ máscaras
    def mask(self, bbox, fn):
        """Desenha com fn(draw, T) em supersampling e devolve (x0, y0, máscara 0..1)."""
        x0, y0, x1, y1 = [int(round(v)) for v in bbox]
        x0, y0 = max(x0, 0), max(y0, 0)
        x1, y1 = min(x1, self.W), min(y1, self.H)
        im = Image.new('L', ((x1 - x0) * SS, (y1 - y0) * SS), 0)
        d = ImageDraw.Draw(im)

        def T(pts):
            return [((x - x0) * SS, (y - y0) * SS) for x, y in pts]
        fn(d, T)
        im = im.resize((x1 - x0, y1 - y0), Image.BOX)
        return x0, y0, np.asarray(im, np.float32) / 255.0

    # ------------------------------------------------------------ classes de cor
    def classes(self, x0, y0, m):
        h, w = m.shape
        p = self.a[y0:y0 + h, x0:x0 + w]
        r, g, b = p[..., 0], p[..., 1], p[..., 2]
        white = (r > 215) & (g > 215) & (b > 215)
        cream = (r > 215) & (g > 150) & (b > 100) & ~white
        pupil = (r < 75) & (g < 75) & (b < 75)
        brown = (r < 145) & (g < 75) & (b < 55) & ~pupil
        orange = ~white & ~cream & ~pupil & ~brown
        return dict(white=white, cream=cream, pupil=pupil, brown=brown, orange=orange)

    # ------------------------------------------------------------ pintura
    def paint(self, mk, color, opacity=1.0, only=None):
        x0, y0, m = mk
        h, w = m.shape
        m = m * opacity
        if only is not None:
            cl = self.classes(x0, y0, m)
            sel = np.zeros_like(m, dtype=bool)
            for k in only:
                sel |= cl[k]
            m = m * sel
        p = self.a[y0:y0 + h, x0:x0 + w]
        c = np.array(color, np.float32)
        p[..., :3] = p[..., :3] * (1 - m[..., None]) + c * m[..., None]

    def save(self, path):
        Image.fromarray(np.clip(self.a, 0, 255).round().astype(np.uint8), 'RGBA').save(path)


# ------------------------------------------------------------ geometria

def catmull(pts, n=16):
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    out.append(tuple(pts[-1]))
    return out


def taper_poly(pts, ws):
    c = catmull(pts)
    L = [0.0]
    for i in range(1, len(c)):
        L.append(L[-1] + math.dist(c[i - 1], c[i]))
    tot = L[-1] or 1
    left, right = [], []
    for i, p in enumerate(c):
        a, b = c[max(i - 1, 0)], c[min(i + 1, len(c) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        t = L[i] / tot
        seg = t * (len(ws) - 1)
        k = min(int(seg), len(ws) - 2)
        w = (ws[k] * (1 - (seg - k)) + ws[k + 1] * (seg - k)) / 2
        left.append((p[0] - dy / d * w, p[1] + dx / d * w))
        right.append((p[0] + dy / d * w, p[1] - dx / d * w))
    return left + right[::-1]


def bbox_of(pts, pad=6):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


# ------------------------------------------------------------ operações

def stroke(cv, pts, ws, color, opacity=1.0, only=None):
    poly = taper_poly(pts, ws)
    cv.paint(cv.mask(bbox_of(poly), lambda d, T: d.polygon(T(poly), fill=255)), color, opacity, only)


def erase(cv, poly, only=('orange', 'brown', 'pupil')):
    """Cobre com a cor do corpo (apaga sobrancelha/boca antigas)."""
    cv.paint(cv.mask(bbox_of(poly), lambda d, T: d.polygon(T(poly), fill=255)), BODY, 1.0, only)


def eye(cv, box, inner, lid=(0.16, 0.42), pupil_dy=0.3, bag=11, bag_op=0.9):
    """
    box   (x0, y0, x1, y1) do branco do olho
    inner 'l' ou 'r': lado da tromba (canto interno)
    lid   quanto a pálpebra desce no canto externo e no interno (fração da altura)
    """
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    reg = cv.a[y0 - 2:y1 + 2, x0 - 2:x1 + 2]
    r, g, b = reg[..., 0], reg[..., 1], reg[..., 2]
    is_white = (r > 215) & (g > 215) & (b > 215)
    is_pupil = (r < 75) & (g < 75) & (b < 75)
    eye_px = is_white | is_pupil
    cols = np.nonzero(eye_px.any(0))[0]
    tops = {c: np.nonzero(eye_px[:, c])[0].min() for c in cols}
    bots = {c: np.nonzero(eye_px[:, c])[0].max() for c in cols}

    # pupila: centro atual (parte visível) -> redesenha mais baixa.
    # O olho é repintado pelo "quanto o pixel é neutro" (branco/preto vs laranja),
    # o que preserva o antisserrilhado original da borda do olho.
    ys, xs = np.nonzero(is_pupil)
    pcx, pr = xs.mean() + x0 - 2, (xs.max() - xs.min() + 1) / 2
    ptop = ys.min() + y0 - 2
    pcy = ptop + pr * 0.55 + pupil_dy * h
    bx0, by0, bx1, by1 = x0 - 3, y0 - 3, x1 + 3, y1 + 3
    _, _, pm = cv.mask((bx0, by0, bx1, by1), lambda d, T: d.ellipse(T([(pcx - pr, pcy - pr), (pcx + pr, pcy + pr)]), fill=255))
    p = cv.a[by0:by1, bx0:bx1]
    mx, mn = p[..., :3].max(-1), p[..., :3].min(-1)
    sat = (mx - mn) / np.maximum(mx, 1)
    wgt = np.clip((0.75 - sat) / 0.6, 0, 1)
    col = np.array(WHITE, np.float32) * (1 - pm[..., None]) + np.array(PUPIL, np.float32) * pm[..., None]
    p[..., :3] = p[..., :3] * (1 - wgt[..., None]) + col * wgt[..., None]

    # pálpebra: reta do canto externo ao interno, mais baixa que a atual
    c_out, c_in = (cols.min(), cols.max()) if inner == 'r' else (cols.max(), cols.min())
    k_out = int(c_out + (0.12 * w if inner == 'r' else -0.12 * w))
    k_in = int(c_in + (-0.12 * w if inner == 'r' else 0.12 * w))
    y_out = tops[min(cols, key=lambda c: abs(c - k_out))] + y0 - 2 + lid[0] * h
    y_in = tops[min(cols, key=lambda c: abs(c - k_in))] + y0 - 2 + lid[1] * h
    xo, xi = c_out + x0 - 2, c_in + x0 - 2
    sl = (y_in - y_out) / (xi - xo)
    ext = 8
    ax, bx = (xo - ext, xi + ext) if inner == 'r' else (xi - ext, xo + ext)
    ay = y_out + sl * (ax - xo)
    by = y_out + sl * (bx - xo)
    poly = [(ax, y0 - 30), (bx, y0 - 30), (bx, by), (ax, ay)]
    cv.paint(cv.mask((ax, y0 - 30, bx, max(ay, by) + 2), lambda d, T: d.polygon(T(poly), fill=255)),
             BODY, 1.0, ('white', 'pupil', 'orange', 'cream'))
    band = [(ax, y0 - 8), (bx, y0 - 8), (bx, min(by, y0 + 4)), (ax, min(ay, y0 + 4))]
    cv.paint(cv.mask((ax, y0 - 8, bx, y0 + 5), lambda d, T: d.polygon(T(band), fill=255)),
             BODY, 1.0, ('brown', 'pupil', 'orange', 'cream', 'white'))

    # olheira: meia-lua colada embaixo do olho
    if bag:
        lo, hi = cols.min(), cols.max()
        upper, lower = [], []
        for c in range(lo, hi + 1):
            cc = min(cols, key=lambda q: abs(q - c))
            t = (c - lo) / max(hi - lo, 1)
            yb = bots[cc] + y0 - 2
            upper.append((c + x0 - 2, yb - 4))
            lower.append((c + x0 - 2, yb + 1 + bag * math.sin(math.pi * t) ** 0.6))
        poly = upper + lower[::-1]
        cv.paint(cv.mask(bbox_of(poly), lambda d, T: d.polygon(T(poly), fill=255)), OLHEIRA, bag_op, ('orange',))
    return (xo, y_out), (xi, y_in)


def brow(cv, outer, inner, ws=(4, 9, 10)):
    stroke(cv, [outer, ((outer[0] + inner[0]) / 2, (outer[1] + inner[1]) / 2 - 2), inner], list(ws), BROWN)


def clean_speckles(cv):
    al = (cv.a[..., 3] > 20).astype(np.uint8)
    keep = cv2.dilate(al, np.ones((7, 7), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(keep)
    big = np.zeros_like(keep)
    for i in range(1, n):
        if st[i][4] > 5000:
            big[lab == i] = 1
    cv.a[..., 3] *= big


# ------------------------------------------------------------ as 8 poses

def main(src, dst):
    cv = Canvas(src)
    clean_speckles(cv)

    # 1. frente ---------------------------------------------------------
    erase(cv, [(158, 138), (208, 138), (208, 158), (158, 158)])
    erase(cv, [(228, 145), (280, 145), (280, 165), (228, 165)])
    erase(cv, [(250, 210), (276, 210), (276, 228), (250, 228)], only=('orange', 'brown'))
    (lo, li) = eye(cv, (158, 165, 203, 193), 'r')
    (ro, ri) = eye(cv, (234, 165, 277, 193), 'l')
    brow(cv, (158, lo[1] - 16), (207, li[1] - 9))
    brow(cv, (276, ro[1] - 16), (229, ri[1] - 9))
    stroke(cv, [(253, 219), (262, 214), (273, 222)], [2.5, 4, 2.5], LINE)

    # 2. três quartos -----------------------------------------------------
    erase(cv, [(560, 120), (614, 120), (614, 151), (560, 151)])
    erase(cv, [(628, 146), (686, 146), (686, 165), (628, 165)])
    (lo, li) = eye(cv, (562, 160, 606, 190), 'r')
    (ro, ri) = eye(cv, (636, 169, 673, 196), 'l')
    brow(cv, (560, lo[1] - 18), (609, li[1] - 9))
    brow(cv, (680, ro[1] - 15), (636, ri[1] - 8), (4, 8, 9))

    # 3. perfil -------------------------------------------------------------
    erase(cv, [(988, 114), (1042, 114), (1042, 144), (988, 144)])
    erase(cv, [(1030, 204), (1050, 204), (1050, 216), (1030, 216)], only=('orange',))
    (eo, ei) = eye(cv, (1003, 151, 1039, 182), 'r')
    brow(cv, (999, eo[1] - 18), (1040, ei[1] - 9))
    stroke(cv, [(1031, 214), (1039, 208), (1049, 212)], [2.5, 4, 2.5], LINE)

    # 4. costas: sem rosto, fica como na v1

    # 5. andando -------------------------------------------------------------
    erase(cv, [(182, 594), (238, 594), (238, 622), (182, 622)])
    erase(cv, [(250, 615), (296, 615), (296, 640), (250, 640)])
    erase(cv, [(196, 682), (214, 682), (214, 694), (196, 694)], only=('orange',))
    (lo, li) = eye(cv, (187, 629, 230, 657), 'r')
    (ro, ri) = eye(cv, (259, 638, 293, 663), 'l')
    brow(cv, (190, lo[1] - 18), (234, li[1] - 9))
    brow(cv, (296, ro[1] - 14), (262, ri[1] - 8), (4, 8, 9))
    stroke(cv, [(196, 690), (204, 684), (213, 689)], [2.5, 4, 2.5], LINE)

    # 6. acenando -----------------------------------------------------------
    erase(cv, [(552, 586), (598, 586), (598, 614), (552, 614)])
    erase(cv, [(614, 584), (654, 584), (654, 610), (614, 610)])
    erase(cv, [(560, 659), (600, 659), (600, 678), (560, 678)], only=('orange', 'brown'))
    (lo, li) = eye(cv, (560, 621, 601, 650), 'r')
    (ro, ri) = eye(cv, (627, 606, 660, 631), 'l')
    brow(cv, (556, lo[1] - 17), (604, li[1] - 9))
    brow(cv, (662, ro[1] - 13), (630, ri[1] - 8), (4, 8, 9))
    stroke(cv, [(566, 672), (582, 664), (598, 671)], [2.5, 4, 2.5], LINE)

    # 7. dando de ombros ----------------------------------------------------
    erase(cv, [(916, 606), (978, 606), (978, 638), (916, 638)])
    erase(cv, [(990, 612), (1034, 612), (1034, 638), (990, 638)])
    erase(cv, [(930, 683), (962, 683), (962, 700), (930, 700)], only=('orange', 'brown'))
    (lo, li) = eye(cv, (932, 643, 973, 670), 'r')
    (ro, ri) = eye(cv, (1002, 637, 1039, 663), 'l')
    brow(cv, (926, lo[1] - 17), (976, li[1] - 9))
    brow(cv, (1042, ro[1] - 14), (1003, ri[1] - 8), (4, 8, 9))
    stroke(cv, [(935, 696), (946, 689), (957, 695)], [2.5, 4, 2.5], LINE)

    # 8. facepalm -----------------------------------------------------------
    erase(cv, [(1312, 620), (1366, 620), (1366, 644), (1312, 644)])
    erase(cv, [(1312, 656), (1362, 656), (1362, 682), (1312, 682)], only=('orange', 'brown', 'pupil'))
    bag = catmull([(1317, 668), (1337, 670), (1358, 666)], 8) + catmull([(1356, 669), (1337, 681), (1319, 671)], 8)
    cv.paint(cv.mask(bbox_of(bag), lambda d, T: d.polygon(T(bag), fill=255)), OLHEIRA, 0.9, ('orange',))
    stroke(cv, [(1316, 668), (1337, 670), (1359, 665)], [3, 5, 3], LID_LINE)
    brow(cv, (1316, 637), (1362, 650))

    cv.save(dst)


if __name__ == '__main__':
    arte = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(arte, 'referencia', 'mamu-v1-original.png')
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(arte, 'mamu-v2.png')
    main(src, dst)
