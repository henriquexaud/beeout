"""Expressões (só cabeça), para referência de animação facial."""
from mamu import front
from props import qmark

EXPRESSOES = {
    'padrao': ('Mau humor de fábrica', front()),
    'side-eye': ('Side-eye sarcástico', front(dict(
        eyes={'both': dict(lid=0.5, tilt=0.1, pdx=12, pdy=5)},
        brow_l=(128, 150, 182, 157), brow_r=(218, 146, 272, 128), mouth='smirk'))),
    'cetico': ('“Sei…”', front(dict(
        eyes={'l': dict(lid=0.62, tilt=0.12, pdx=2, pdy=6), 'r': dict(lid=0.3, tilt=-0.05, pdx=2, pdy=5)},
        brow_l=(128, 156, 182, 160), brow_r=(218, 136, 272, 122), mouth='flat'))),
    'exausto': ('Madrugada (olho vermelho)', front(dict(
        eyes={'both': dict(lid=0.66, tilt=-0.18, pdx=0, pdy=7, red=True)},
        brow_l=(128, 156, 182, 146), brow_r=(218, 146, 272, 156), mouth='flat'))),
    'irritado': ('Irritado de verdade', front(dict(
        eyes={'both': dict(closed='tight')},
        brow_l=(130, 140, 184, 162), brow_r=(216, 162, 270, 140), mouth='yell'))),
    'orgulho-disfarcado': ('Orgulho disfarçado', front(dict(
        eyes={'both': dict(lid=0.38, tilt=-0.08, pdx=-9, pdy=-4)},
        brow_l=(128, 144, 182, 140), brow_r=(218, 140, 272, 144), mouth='smile', blush=True))),
    'nao-entendo': ('“Dessa parte eu não entendo”', front(dict(
        eyes={'l': dict(lid=0.3, tilt=0, pdx=-4, pdy=-6), 'r': dict(lid=0.5, tilt=0.15, pdx=-4, pdy=-6)},
        brow_l=(128, 132, 182, 128), brow_r=(218, 156, 272, 150), mouth='flat',
        props=qmark(300, 104)))),
    'pego-no-flagra': ('Pego no flagra', front(dict(
        eyes={'both': dict(lid=0.02, tilt=0, pdx=0, pdy=0, pr=7)},
        brow_l=(130, 128, 182, 124), brow_r=(218, 124, 270, 128), mouth='o'))),
}
