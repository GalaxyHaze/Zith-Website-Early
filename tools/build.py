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
import random
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
BUBBLE_SPAN = re.compile(r"\{\{\s*bubbles\s*\}\}")

# Nunca publicados: ferramentas, parciais e notas internas.
SKIP_DIRS = {
    ".git", ".github", ".vscode", ".agents", ".codex", ".idea",
    "tools", "partials", "notes", "_site", "node_modules", "__pycache__",
}
SKIP_FILES = {".gitignore", ".DS_Store", "Thumbs.db"}
SKIP_SUFFIXES = {".md"}

# Bolhas da landing: geradas no build, com PRNG semeado para o resultado ser
# reproduzivel (o mesmo input -> o mesmo HTML; sem isto, cada build sujaria o
# git diff). O CSS anima-as quando nao ha JS; o JS assume-as quando ha.
BUBBLE_DEFAULTS = {
    "count": "14",
    "min-size": "16",
    "max-size": "90",
    "min-duration": "6",
    "max-duration": "14",
    "max-delay": "6",
}
BUBBLE_SEED = 20261008


def parse_meta(text: str) -> tuple[dict[str, str], str]:
    """Separa o bloco de meta do topo; devolve (meta, corpo)."""
    match = FRONT_MATTER.match(text)
    if not match:
        return {}, text
    meta = {k: v for k, v in KV.findall(match.group(1))}
    return meta, text[match.end():]


def render(
    text: str,
    partials: Path,
    meta: dict[str, str],
    seed: int = BUBBLE_SEED,
    baseurl: str = "",
) -> str:
    """Expande includes (recursivamente) e placeholders."""
    page_values = {**meta, "baseurl": baseurl}

    def render_bubbles(values: dict[str, str]) -> str:
        """Gera o markup das bolhas com posicoes/tamanhos fixos por build.

        Cada bolha leva os valores como custom properties inline, para o CSS
        as animar (fallback) e o JS as poder ler (quando existe).
        """
        def num(key: str) -> float:
            raw = values.get(key, BUBBLE_DEFAULTS[key])
            try:
                return float(raw)
            except ValueError:
                raise SystemExit(f"build: valor invalido para '{key}': {raw!r}")

        count = int(num("count"))
        min_size, max_size = num("min-size"), num("max-size")
        min_dur, max_dur = num("min-duration"), num("max-duration")
        max_delay = num("max-delay")

        # Semente: o include pode sobrepor (`seed="123"`), senao usa a do build.
        raw_seed = values.get("seed")
        if raw_seed is None:
            bubble_seed = seed
        else:
            try:
                bubble_seed = int(raw_seed)
            except ValueError:
                raise SystemExit(f"build: semente invalida em include:bubbles: {raw_seed!r}")

        rng = random.Random(bubble_seed)
        lines = []
        for _ in range(count):
            size = round(rng.uniform(min_size, max_size))
            left = round(rng.uniform(0, 100), 2)
            top = round(rng.uniform(0, 100), 2)
            duration = round(rng.uniform(min_dur, max_dur), 2)
            delay = round(rng.uniform(0, max_delay), 2)
            lines.append(
                "        <div class=\"bubble\" style=\""
                f"--bubble-size:{size}px;"
                f"--bubble-left:{left}%;"
                f"--bubble-top:{top}%;"
                f"--bubble-duration:{duration}s;"
                f"--bubble-delay:{delay}s"
                '"></div>'
            )
        return "\n".join(lines)

    def expand(match: re.Match) -> str:
        name = match.group(1)
        args = dict(ARG.findall(match.group(2)))
        values = {**page_values, **args}
        path = partials / f"{name}.html"
        if not path.is_file():
            raise SystemExit(f"build: include '{name}' nao encontrado em {path}")
        partial = path.read_text(encoding="utf-8")
        partial = LEADING_COMMENT.sub("", partial)  # comentario-doc do parcial
        if name == "bubbles":
            partial = BUBBLE_SPAN.sub(lambda m: render_bubbles(values), partial)
        partial = ACTIVE.sub(
            lambda a: "is-active" if a.group(1) == values.get("active", "") else "",
            partial,
        )
        return VAR.sub(lambda v: values.get(v.group(1), v.group(0)), partial)

    while INCLUDE.search(text):
        text = INCLUDE.sub(expand, text)
    # Placeholders da propria pagina (ex.: {{title}} no <head>).
    return VAR.sub(lambda v: page_values.get(v.group(1), v.group(0)), text)


def build(
    src: Path,
    out: Path,
    partials: Path,
    seed: int = BUBBLE_SEED,
    baseurl: str = "",
) -> int:
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
            dst.write_text(render(body, partials, meta, seed, baseurl), encoding="utf-8")
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
    parser.add_argument(
        "--seed",
        type=int,
        default=BUBBLE_SEED,
        help=f"semente do sorteio das bolhas (default: {BUBBLE_SEED})",
    )
    parser.add_argument(
        "--baseurl",
        default="",
        help="prefixo do URL do site, por exemplo /Zith-Website-Early",
    )
    args = parser.parse_args()
    pages = build(
        args.src.resolve(),
        args.out.resolve(),
        args.partials.resolve(),
        args.seed,
        args.baseurl.rstrip("/"),
    )
    print(f"build: {pages} pagina(s) HTML -> {args.out} (seed={args.seed})")


if __name__ == "__main__":
    main()
