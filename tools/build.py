#!/usr/bin/env python3
"""Build estatico do site Zith: expande <!-- include:... --> e copia assets.

Sem dependencias externas.

Uso:
    python3 tools/build.py                 # src = pages/, out = _site/
    python3 tools/build.py --src . --out _site

Paginas-fonte podem declarar meta no topo (opcional):

    <!--
    title: Zith — Systems Programming
    active: home
    -->

Includes:

    <!-- include:header active="home" -->
    <!-- include:footer -->

Dentro de um parcial:
    {{active:home}}   -> "is-active" se a pagina ativa for "home", senao ""
    {{title}}         -> valor de meta "title"
"""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

INCLUDE = re.compile(r"<!--\s*include:\s*([\w-]+)\s*(.*?)-->", re.S)
ARG = re.compile(r'([\w-]+)\s*=\s*"([^"]*)"')
FRONT_MATTER = re.compile(r"\A\s*<!--\s*\n(.*?)\n\s*-->\s*\n", re.S)
KV = re.compile(r"^\s*([\w-]+)\s*:\s*(.*?)\s*$", re.M)
ACTIVE = re.compile(r"\{\{\s*active:([\w-]+)\s*\}\}")
VAR = re.compile(r"\{\{\s*([\w-]+)\s*\}\}")
LEADING_COMMENT = re.compile(r"\A\s*<!--.*?-->\s*", re.S)

# Nunca publicados: ferramentas, parciais e notas internas.
SKIP_DIRS = {
    ".git", ".github", ".vscode", ".agents", ".codex", ".idea",
    "tools", "partials", "notes", "_site", "node_modules", "__pycache__",
}
SKIP_FILES = {".gitignore", ".DS_Store", "Thumbs.db"}
SKIP_SUFFIXES = {".md"}


def parse_meta(text: str) -> tuple[dict[str, str], str]:
    """Separa o bloco de meta do topo; devolve (meta, corpo)."""
    match = FRONT_MATTER.match(text)
    if not match:
        return {}, text
    meta = {k: v for k, v in KV.findall(match.group(1))}
    return meta, text[match.end():]


def render(text: str, partials: Path, meta: dict[str, str]) -> str:
    """Expande includes (recursivamente) e placeholders."""

    def expand(match: re.Match) -> str:
        name = match.group(1)
        args = dict(ARG.findall(match.group(2)))
        values = {**meta, **args}
        path = partials / f"{name}.html"
        if not path.is_file():
            raise SystemExit(f"build: include '{name}' nao encontrado em {path}")
        partial = path.read_text(encoding="utf-8")
        partial = LEADING_COMMENT.sub("", partial)  # comentario-doc do parcial
        partial = ACTIVE.sub(
            lambda a: "is-active" if a.group(1) == values.get("active", "") else "",
            partial,
        )
        return VAR.sub(lambda v: values.get(v.group(1), v.group(0)), partial)

    while INCLUDE.search(text):
        text = INCLUDE.sub(expand, text)
    # Placeholders da propria pagina (ex.: {{title}} no <head>).
    return VAR.sub(lambda v: meta.get(v.group(1), v.group(0)), text)


def build(src: Path, out: Path, partials: Path) -> int:
    if not partials.is_dir():
        raise SystemExit(f"build: falta a pasta de parciais: {partials}")
    if out.exists():
        shutil.rmtree(out)

    pages = 0
    for path in sorted(src.rglob("*")):
        rel = path.relative_to(src)
        if rel.parts and (rel.parts[0] in SKIP_DIRS or any(p in SKIP_DIRS for p in rel.parts[:-1])):
            continue
        dst = out / rel
        if path.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue
        if path.name in SKIP_FILES or path.suffix.lower() in SKIP_SUFFIXES:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() == ".html":
            meta, body = parse_meta(path.read_text(encoding="utf-8"))
            dst.write_text(render(body, partials, meta), encoding="utf-8")
            pages += 1
        else:
            shutil.copy2(path, dst)
    return pages


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Build estatico do site Zith.")
    parser.add_argument("--src", type=Path, default=root / "pages", help="raiz das paginas-fonte")
    parser.add_argument("--out", type=Path, default=root / "_site", help="destino do build")
    parser.add_argument("--partials", type=Path, default=root / "partials", help="pasta dos parciais")
    args = parser.parse_args()
    pages = build(args.src.resolve(), args.out.resolve(), args.partials.resolve())
    print(f"build: {pages} pagina(s) HTML -> {args.out}")


if __name__ == "__main__":
    main()
