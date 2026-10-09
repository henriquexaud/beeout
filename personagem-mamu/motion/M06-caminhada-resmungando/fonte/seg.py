"""Segmenta a pose 'andando' (v2) em partes e classes de cor."""
import numpy as np, cv2
from PIL import Image, ImageDraw

X0, Y0, X1, Y1 = 30, 515, 412, 965
PAL = {
    'body': (198, 83, 30), 'shade': (173, 70, 24), 'shade2': (146, 58, 21),
    'brown': (112, 47, 22), 'cream': (253, 227, 194), 'cream2': (250, 214, 173),
    'white': (250, 250, 250), 'olheira': (131, 52, 50), 'pupil': (27, 28, 32),
}
NAMES = list(PAL)

def load(path):
    a = np.array(Image.open(path).convert('RGBA'))[Y0:Y1, X0:X1].astype(np.float32)
    rgb, alpha = a[..., :3], a[..., 3] / 255.0
    # só os pedaços desta pose (descarta o braço da pose vizinha que entra no recorte)
    n, lab, st, _ = cv2.connectedComponentsWithStats((alpha > 0.01).astype(np.uint8))
    keep = np.zeros(alpha.shape, bool)
    for i in range(1, n):
        if st[i][0] < 340 and st[i][4] > 30:
            keep |= lab == i
    alpha = alpha * keep
    cols = np.array([PAL[k] for k in NAMES], np.float32)
    d = ((rgb[:, :, None, :] - cols[None, None]) ** 2).sum(-1)
    label = d.argmin(-1)
    return rgb, alpha, label

def poly_mask(h, w, pts):
    im = Image.new('L', (w, h), 0)
    ImageDraw.Draw(im).polygon([(x - X0, y - Y0) for x, y in pts], fill=255)
    return np.asarray(im) > 0

def parts(alpha, label):
    h, w = alpha.shape
    solid = alpha > 0.02
    brown = label == NAMES.index('brown')
    # rabo: componente marrom à esquerda, embaixo
    box = poly_mask(h, w, [(30, 830), (130, 830), (130, 885), (30, 885)])
    darkish = (label == NAMES.index('brown')) | (alpha < 0.98)
    tail = cv2.dilate((box & brown).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & solid & box & darkish
    # perna de trás: abaixo da linha de cor (122,873)->(190,902), à esquerda da separação
    back_leg = poly_mask(h, w, [(80, 868), (122, 871), (192, 901), (196, 930), (200, 965), (80, 965)]) & solid & ~tail
    # perna da frente: abaixo de (185,903)->(275,868)->(330,868)
    front_leg = poly_mask(h, w, [(186, 904), (275, 868), (330, 868), (330, 965), (200, 965), (196, 930)]) & solid
    # versões das pernas com sobra para cima (ficam por baixo do corpo e evitam fresta ao girar)
    back_leg_draw = poly_mask(h, w, [(80, 860), (122, 863), (192, 893), (196, 930), (200, 965), (80, 965)]) & solid & ~tail
    front_leg_draw = poly_mask(h, w, [(186, 896), (275, 860), (330, 860), (330, 965), (200, 965), (196, 930)]) & solid
    return dict(tail=tail, back_leg=back_leg, front_leg=front_leg,
                back_leg_draw=back_leg_draw, front_leg_draw=front_leg_draw)
