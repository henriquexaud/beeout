"""Poses de personalidade. Cada pose = (título, fala, svg)."""
from mamu import C, front, three_q
from props import cigarette, phone, delivery_bag, remote, sweat, headband, moon, note

ARM_L = [(106, 258), (88, 294), (82, 330), (90, 358)]  # braço esquerdo caído (padrão)


def so_hoje(smoke_on=True):
    return front(dict(
        eyes={'both': dict(lid=0.56, tilt=0.04, pdx=6, pdy=5)},
        brow_l=(128, 150, 182, 156), brow_r=(218, 150, 272, 138), mouth='flat',
        arms={'l': ARM_L, 'r': [(292, 268), (330, 300), (330, 262), (310, 238)]},
        arms_w={'l': [26, 34, 44], 'r': [26, 32, 40]},
        props=cigarette(304, 238, ang=-128, L=46, smoke_on=smoke_on),
    ))


POSES = {
    'so-hoje': ('Só hoje', '“Esse é o último. Desse maço.”', so_hoje()),

    'segunda': ('Segunda eu começo', '“Conheço essa frase. Usei por algumas eras geológicas.”', front(dict(
        eyes={'both': dict(lid=0.42, tilt=-0.12, pdx=0, pdy=4)},
        brow_l=(128, 146, 182, 134), brow_r=(218, 134, 272, 146), mouth='smirk',
        arms={'l': [(108, 270), (74, 290), (52, 268), (46, 240)],
              'r': [(292, 270), (326, 290), (348, 268), (354, 240)]},
    ))),

    'pausa-tela': ('Faz uma pausa da tela', '“Larga esse celular.” (3h47 da manhã, no celular)', front(dict(
        eyes={'both': dict(lid=0.5, tilt=0.05, pdx=4, pdy=10, red=True)},
        brow_l=(128, 150, 182, 154), brow_r=(218, 154, 272, 150), mouth='flat',
        arms={'l': ARM_L, 'r': [(294, 262), (316, 300), (296, 326), (268, 322)]},
        props=phone(256, 304, ang=-14) + f'<circle cx="276" cy="318" r="13" fill="{C["brown"]}"/>' + moon(352, 58),
    ))),

    'comida-de-verdade': ('Comida de verdade', '“Come comida de verdade.” *empurra o delivery pra fora do quadro*', front(dict(
        eyes={'both': dict(lid=0.34, tilt=-0.05, pdx=-7, pdy=-3)},
        brow_l=(128, 140, 182, 140), brow_r=(218, 140, 272, 140), mouth='o',
        arms={'l': ARM_L, 'r': [(294, 270), (326, 320), (350, 380), (366, 408)]},
        props_mid=delivery_bag(392, 450, ang=4),
        props=note(304, 238) + note(326, 206, .75),
    ))),

    'se-mexer': ('Você precisa se mexer', '“Movimento é tudo.” *tromba busca o controle*', front(dict(
        eyes={'both': dict(lid=0.5, tilt=0.06, pdx=9, pdy=10)},
        brow_l=(128, 150, 182, 155), brow_r=(218, 155, 272, 150), mouth='flat',
        trunk=[(200, 192), (202, 236), (214, 282), (250, 318), (300, 340), (340, 372), (360, 404)],
        trunk_w=[44, 36, 28, 22, 18], trunk_front=True,
        arms={'l': [(106, 262), (98, 300), (122, 330), (156, 334)],
              'r': [(294, 258), (312, 294), (318, 330), (310, 358)]},
        props_mid=remote(368, 428, ang=-64),
    ))),

    'conheco-essa-desculpa': ('Conheço essa desculpa', '“Eu sei onde essa desculpa termina.”', front(dict(
        eyes={'both': dict(lid=0.55, tilt=0.0, pdx=0, pdy=4)},
        brow_l=(128, 152, 182, 154), brow_r=(218, 140, 272, 130), mouth='flat',
        trunk=[(200, 192), (200, 232), (198, 270), (196, 296), (200, 314), (212, 318)],
        trunk_w=[44, 38, 31, 26, 22], trunk_front=True,
        arms={'l': [(108, 270), (122, 318), (186, 334), (262, 318)],
              'r': [(292, 270), (280, 306), (226, 318), (146, 310)]},
        arms_cross=True,
    ))),

    'caminhada': ('Caminhada resmungando', '“Tô indo. Tô reclamando, mas tô indo.”', three_q(dict(
        walk=True,
        eyes={'both': dict(closed='tight')},
        brow_l=(152, 150, 206, 160), brow_r=(256, 158, 296, 148),
        arms={'l': [(108, 262), (84, 290), (70, 320), (66, 346)],
              'r': [(300, 266), (322, 296), (336, 320), (344, 342)]},
        props_head=headband(214, 176, 90, 120, 140),
        props=sweat(324, 118, 1.0, 20) + sweat(116, 138, .8, -20),
    ))),

    'orgulho-disfarcado': ('Orgulho disfarçado', '“Tá. Foi bom. Não se acostuma.”', front(dict(
        eyes={'both': dict(lid=0.38, tilt=-0.08, pdx=-8, pdy=-4)},
        brow_l=(128, 144, 182, 140), brow_r=(218, 140, 272, 144), mouth='smile', blush=True,
        arms={'l': ARM_L, 'r': [(294, 266), (334, 250), (330, 196), (304, 168)]},
    ))),
}
