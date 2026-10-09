"""Helpers de geometria: curvas Catmull-Rom e traços afinados (tapered)."""
import math

def catmull(pts, n=24):
    """Catmull-Rom spline through pts -> dense list of points."""
    if len(pts) < 2:
        return pts
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(pts[-1])
    return out

def _width(ws, t):
    if isinstance(ws, (int, float)):
        return ws
    if len(ws) == 1:
        return ws[0]
    seg = t * (len(ws) - 1)
    i = min(int(seg), len(ws) - 2)
    f = seg - i
    return ws[i] * (1 - f) + ws[i + 1] * f

def f(v):
    return f"{v:.1f}".rstrip('0').rstrip('.')

def taper(pts, ws, fill, cap=True, extra='', cap0=None):
    """Filled tapered stroke along a Catmull-Rom centerline. ws: width or list of widths along length."""
    c = catmull(pts)
    # cumulative length for t
    L = [0.0]
    for i in range(1, len(c)):
        L.append(L[-1] + math.dist(c[i - 1], c[i]))
    tot = L[-1] or 1
    left, right = [], []
    for i, p in enumerate(c):
        a = c[max(i - 1, 0)]
        b = c[min(i + 1, len(c) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        w = _width(ws, L[i] / tot) / 2
        left.append((p[0] + nx * w, p[1] + ny * w))
        right.append((p[0] - nx * w, p[1] - ny * w))
    poly = left + right[::-1]
    d = 'M' + ' L'.join(f"{f(x)},{f(y)}" for x, y in poly) + 'Z'
    s = f'<path d="{d}" fill="{fill}"{extra}/>'
    if cap:
        w0 = _width(ws, 0) / 2
        w1 = _width(ws, 1) / 2
        if cap0 is not False:
            s += f'<circle cx="{f(c[0][0])}" cy="{f(c[0][1])}" r="{f(w0)}" fill="{fill}"{extra}/>'
        s += f'<circle cx="{f(c[-1][0])}" cy="{f(c[-1][1])}" r="{f(w1)}" fill="{fill}"{extra}/>'
    return s

def stroke(pts, w, color, extra=''):
    c = catmull(pts, 12)
    d = 'M' + ' L'.join(f"{f(x)},{f(y)}" for x, y in c)
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{f(w)}" stroke-linecap="round" stroke-linejoin="round"{extra}/>'
