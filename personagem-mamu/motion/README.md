# Motion do Mamu

Aqui ficam as ideias e as animações do Mamu. Cada motion tem uma pasta própria `Mxx-nome/`, com um `README.md` (a ficha) e os arquivos que forem surgindo (animatic, projeto, export).

**Para criar um motion novo:** copie [`_modelo.md`](_modelo.md) para `Mxx-nome/README.md`, preencha e adicione uma linha na tabela abaixo.

## Índice

| # | Motion | Gatilho no app | Status |
|---|---|---|---|
| [M00](M00-idle/) | Idle: "Só hoje" | App aberto, Mamu parado | Protótipo (SVG animado) |
| [M01](M01-segunda-eu-comeco/) | Segunda eu começo | Usuário adia a meta | Ideia |
| [M02](M02-pausa-da-tela/) | Faz uma pausa da tela | Tempo de tela alto | Ideia |
| [M03](M03-comida-de-verdade/) | Comida de verdade | Registro de delivery | Ideia |
| [M04](M04-se-mexer/) | Você precisa se mexer | Dia sem movimento | Ideia |
| [M05](M05-vai-dormir/) | Vai dormir | Uso de madrugada | Ideia |
| [M06](M06-caminhada-resmungando/) | Caminhada resmungando | Atividade concluída | Ideia |
| [M07](M07-voce-voltou/) | Você voltou | Retorno depois de sumir ou recair | Ideia |
| [M08](M08-orgulho-disfarcado/) | Orgulho disfarçado | Marco de sequência | Ideia |
| [M09](M09-dessa-parte-eu-nao-entendo/) | Dessa parte eu não entendo | Tema sensível | Ideia |

**Status:** Ideia → Roteiro → Animatic → Animação → Final

## Como o Mamu se move

Princípios tirados da [personalidade](../conceito/personalidade.md). Valem para qualquer motion.

1. **Lento para começar, rápido para desistir.** Antecipação longa e arrastada, ação curta, assentamento pesado.
2. **O olhar vem antes da fala.** Segure o side-eye por meio segundo antes da linha. Às vezes o olhar *é* a fala.
3. **Peso acima de tudo.** Pouco squash and stretch. Ele é pesado e está cansado: a barriga tem follow-through (balança 2 ou 3 quadros depois que o corpo para).
4. **A tromba é a mão preguiçosa.** Faz o que o corpo não quer levantar para fazer. É a ação secundária preferida.
5. **Piscada lenta.** A pálpebra já é pesada; fechar e abrir leva o dobro do normal.
6. **Orelhas reagem primeiro.** Ele finge que não está ouvindo, mas a orelha levanta.
7. **Comédia em três tempos:** conselho → contradição → percepção. Na percepção, prefira um olhar para a câmera a uma fala.
8. **Sem glamour no cigarro.** A fumaça é cinza e preguiçosa; nada de fumaça estilosa.

## Base técnica (sugestão)

- **Arte base:** [`arte/mamu-v2-frente.svg`](../arte/mamu-v2-frente.svg), com as camadas já nomeadas (`pernas`, `orelhas`, `corpo`, `cabelo`, `olhos`, `sobrancelhas`, `presas`, `boca`, `tromba`, `bracos`). Poses e expressões novas podem ser geradas em [`arte/fonte/`](../arte/fonte/).
- **Formatos:** Lottie ou Rive para o app (leve, vetorial, interativo); MP4 ou GIF para redes e apresentações.
- **Quadro:** 400×480 (5:6) para o app; 1080×1350 para feed.
- **Ritmo:** 24 fps dá a sensação de cartoon. A maioria dos motions de reação deve ficar entre 3 e 6 segundos.
