# CONTEXT — glossario

Vocabulario partilhado. Manter curto e sem ambiguidade.

- **Zith** — linguagem de programacao compilada, tipada estaticamente, para
  sistemas.
- **NRA (Node Resource Analysis)** — analise de compilacao que prova a
  seguranca de memoria / tempos de vida. Substitui o "borrow checker" classico.
- **zithc** — o compilador.
- **zith-lsp** — servidor de linguagem (Language Server Protocol).
- **Helios** — IDE no browser.
- **Playground** — executa Zith no browser (via WebAssembly).
- **Site original** — https://zith-lang.org, fonte em `../Zith-website`.
- **ZWS_Prototype** — esta repo; reconstrucao em curso.
- **Tokens de design** — variaveis CSS (`--*`) que definem cor/tipografia. Fonte
  unica de verdade do tema.

## Mapa do site

Mesmo ambito do antecessor, com interface melhorada. Paginas previstas:

- **Landing** (`index.html`) — entrada / hero.
- **Docs** — guia, referencia, CLI, especificacao (a maior parte do conteudo).
- **Playground** — correr Zith no browser.
- **Helios** — IDE no browser.
- **Galeria** (nova) — showcase de codigo/projetos.
- **Changelog**, **Blog** (dev log), **About**.

Partilham um **header** e um **footer** unicos. Ver
`notes/decisions/0002-partilha-header-footer.md`.

Termos a evitar por serem vagos: "tema", "cor principal", "estilo do site" —
usar nomes concretos de token.
