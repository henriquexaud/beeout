# M06: Caminhada resmungando

| | |
|---|---|
| **Status** | Protótipo: [`mamu-caminhando.html`](mamu-caminhando.html) (abra no navegador) |
| **Gatilho no app** | Caminhada ou atividade registrada |
| **Duração** | Ciclo de caminhada de 1,5 s em loop + final de ~2 s (o final ainda não está no protótipo) |
| **Loop** | ciclo sim, final não |
| **Formato** | SVG animado (SMIL) dentro de um HTML simples |
| **Poses** | 5 (andando), da [folha v2](../../arte/mamu-v2.png) |

## Ideia em uma frase

Ele resolve caminhar, reclama o caminho inteiro e vai mesmo assim. No fim, admite que preferia o sofá, mas está satisfeito.

## O que já está no protótipo

O Mamu é a pose 5 da folha v2 vetorizada, com as mesmas formas e cores, separada em rabo, perna de trás, perna da frente e corpo.

| Elemento | Animação |
|---|---|
| Pernas | Passo pesado e alternado: o pé apoiado escorrega para trás e o outro sobe e volta |
| Corpo | Afunda a cada passo e balança de um lado para o outro (gingado de quem não quer ir) |
| Rabo | Abana atrasado em relação ao passo |
| Olhos | Piscada pesada; de tempos em tempos revira os olhos |
| Bufada | Fumacinha saindo da cabeça junto com o revirar de olhos |
| Suor | Gota escorrendo pela testa |
| Falas | "Tô indo." · "Reclamando, mas tô indo." · "Quem inventou caminhada?" · "Preferia o sofá." |
| Cenário | Chão, nuvens e uma placa passando: "SOFÁ 0,2 km" para trás, "PARQUE 3 km" para frente |

O botão pausa e retoma a animação. Com "reduzir movimento" ativado no sistema, a página abre pausada.

## Roteiro

| Tempo | O que acontece | Fala / legenda |
|---|---|---|
| ciclo | Walk cycle pesado, com gotas de suor | resmungos ("quem inventou ladeira") |
| final 0.0 s | Para, ofegante, mãos na barriga | |
| final 0.8 s | | "Preferia o sofá." |
| final 1.6 s | Meio sorriso escondido pela tromba | |

## Notas de animação

- O ciclo tem passo curto, a barriga balança a cada passo e a tromba vai junto, como um pêndulo.
- No protótipo os braços e a tromba ainda balançam junto com o corpo. Separar essas partes exige redesenhar o trecho do corpo que fica escondido atrás delas.

## Gerar de novo

O HTML é gerado a partir de `arte/mamu-v2.png`:

```bash
pip install pillow numpy opencv-python-headless
python3 personagem-mamu/motion/M06-caminhada-resmungando/fonte/build.py
```

Os tempos, as falas e o cenário ficam em `fonte/build.py`.

## Pendências

- [ ] Final: para, ofegante, "Preferia o sofá.", meio sorriso
- [ ] Tromba e braço balançando separados do corpo
