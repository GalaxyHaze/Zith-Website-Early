# ZWS_Prototype

Nova versao do site do Zith (o original vive em https://zith-lang.org; o codigo
de referencia esta em `../Zith-website`).

## Estado

Fase de preparacao. Rascunho em `index.html` + `css/base.css` + `css/bubbles.css`.
Ainda nao e uma copia nem um substituto do site original.

## Pre-visualizar

O site e estatico. Abrir `pages/index.html` no browser ou servir a raiz.

Nota: `pages/index.html` e a **fonte** e contem includes por expandir
(`<!-- include:header -->`). Para ver o resultado final, fazer o build (ver
abaixo) e servir `_site/`.

```bash
python3 tools/build.py
python3 -m http.server 5501 --directory _site
```

O `settings.json` do Live Server aponta para a porta `5501`.

## Documentacao de trabalho

- `CONTEXT.md` — glossario do projeto.
- `notes/problems-old-site.md` — problemas anotados da versao anterior.
- `notes/design/` — paleta e tipografia.
- `notes/conventions/` — boas praticas de HTML/CSS/JS.
- `notes/decisions/` — decisoes registadas (ADRs).

`docs/` esta reservado para as paginas do site (area Docs) — **nao** e
documentacao de trabalho. Esta ultima vive em `notes/`.

## Build

O site tem header/footer partilhados em `partials/`, expandidos por
`tools/build.py` para `_site/` (que nao e versionado).

```bash
python3 tools/build.py
python3 -m http.server 5501 --directory _site
```

As paginas-fonte vivem em `pages/` (com os seus `css/` e `media/`). Os parciais
sao expandidos no build; o resto e copiado tal e qual.

O parcial `bubbles` e especial: o build gera as bolhas com posicoes fixas
(PRNG semeado, resultado reproduzivel) e parametrizaveis no include:

```html
<!-- include:bubbles count="18" min-size="20" max-size="80" -->
```

As posicoes iniciais saem de um PRNG semeado. Para as re-sortear sem editar
codigo:

```bash
python3 tools/build.py --seed 12345     # experimentar
```

Gostando do resultado, fixa-se a semente em `BUBBLE_SEED` (`tools/build.py`).

Sem JS, o CSS anima-as; com JS, o script assume o movimento. Ver
`notes/decisions/0004-bolhas-build-e-fallback.md`.

## Regras

O codigo do site e escrito pelo humano. Ver `AGENTS.md` para o ambito do agente.
