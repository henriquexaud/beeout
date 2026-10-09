# Mamu: guia visual (v2)

![Mamu v2](../arte/mamu-v2.png)

A v2 é a arte original com três acréscimos: barriga mais saliente, olheiras e mau humor mais explícito. O formato (folha com 8 poses, fundo transparente), o traço, as cores e as proporções são os da v1.

![v1 vs v2](../arte/mamu-v1-vs-v2.png)

## O que mudou da v1 para a v2

| Mudança | Como foi feita |
|---|---|
| **Barriga mais saliente** | O corpo ganhou volume na parte de baixo, aparecendo por trás dos braços e por cima das pernas. Tem uma sombra da barriga caindo nas pernas e um umbigo. No perfil, a barriga avança à frente do corpo; de costas, aparece dos lados. |
| **Olheiras** | Meia-lua escura, puxada para o roxo, embaixo de cada olho, em todas as poses. Na pose da mão na cara, ela fica sob o olho fechado. |
| **Mau humor mais explícito** | Pálpebra mais baixa e inclinada para dentro (o canto perto da tromba desce mais), sobrancelhas mais grossas e anguladas para baixo, boca virada para baixo no lugar do sorriso de canto. Na pose da mão na cara, o olho fechado deixou de ser um sorriso (∪) e virou um traço cansado. |

Também foram removidos os pontinhos soltos que sobraram do recorte do fundo.

## Poses da folha

| # | Pose | Uso sugerido |
|---|---|---|
| 1 | Frente | Padrão, idle |
| 2 | 3/4 | Falas, reações |
| 3 | Perfil | Entrada e saída de cena; mostra bem a barriga |
| 4 | Costas | "Você voltou" (ele vira devagar) |
| 5 | Andando | Caminhada resmungando |
| 6 | Acenando | Cumprimento a contragosto |
| 7 | Dando de ombros | "Segunda eu começo" |
| 8 | Mão na cara | "Eu sei. Eu sei." |

## Paleta

As cores são as da arte original, mais a da olheira.

| Uso | Hex |
|---|---|
| Corpo | `#C6531E` |
| Sombra do corpo | `#AC4216` |
| Tromba, braços, cabelo, sobrancelhas | `#703018` |
| Presas e unhas | `#FCE2C2` |
| Branco do olho | `#FAFAFA` |
| Pupila | `#1A1C20` |
| **Olheira** | `#823232` |

## Regras

- Olheira sempre, até nas poses mais leves.
- Pálpebra pesada e sobrancelha baixa são o padrão do rosto. Olho bem aberto só como piada (pego no flagra).
- Sorriso, quando houver, é pequeno e de canto.
- A barriga aparece em todas as vistas, sem exagero: é "barriguinha", não caricatura.

## Arquivos

| Arquivo | O que é |
|---|---|
| `arte/mamu-v2.png` | Folha v2 com as 8 poses (1536×1024, fundo transparente) |
| `arte/mamu-v1-vs-v2.png` | Comparação lado a lado |
| `arte/referencia/mamu-v1-original.png` | Arte original (v1) |
| `arte/fonte/editar.py` | Script que gera a v2 a partir da v1 |

Para ajustar algo (altura da pálpebra, tamanho da olheira, volume da barriga), mude os parâmetros em `arte/fonte/editar.py` e rode:

```bash
pip install pillow numpy opencv-python-headless
python3 personagem-mamu/arte/fonte/editar.py
```
