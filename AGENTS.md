# AGENTS.md — acordo de trabalho

## Repo

Reconstrucao do site do Zith (original em https://zith-lang.org, fonte em
`../Zith-website`). Esta repo e espaco de trabalho humano: o **humano escreve
todo o codigo do site**.

## Ambito do agente

**So leitura (nao editar):** tudo dentro de `pages/` (HTML, CSS, JS, media) e
qualquer futuro asset do site.

**O agente pode criar e editar:** `AGENTS.md`, `README.md`, `CONTEXT.md`,
`.gitignore`, `partials/`, `tools/`, `.github/`, e tudo dentro de `notes/`
(notas, registo de problemas, design, convencoes, ADRs).

`docs/` fica reservado para as **paginas do site** (area Docs) — nao e
documentacao interna.

Excecao: se o utilizador pedir explicitamente nessa mensagem ("escreve X",
"cria Y"), o agente pode tocar nos ficheiros nomeados.

## Como trabalhar

- Explicar, revisar, anotar problemas, sugerir e responder a duvidas — em texto.
- Quando pedirem uma correcao, descrever a mudanca (ou mostrar o snippet no
  chat) em vez de editar o ficheiro do site.
- Prosa em portugues (pt-PT); identificadores de codigo em ingles.

## Convencoes

Ver `notes/conventions/`. Decisoes estruturais ficam registadas em
`notes/decisions/`.
