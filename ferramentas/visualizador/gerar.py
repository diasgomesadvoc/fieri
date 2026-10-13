"""Gera a plataforma de visualização dos carrosséis (estilo perfil do Instagram).

Uso:
    python3 ferramentas/visualizador/gerar.py [--artifact PASTA]

Lê conteudo/estaticos/*/conteudo.json e os PNGs em conteudo/estaticos/*/png/ e escreve:
  - visualizador/index.html           página completa, para abrir no navegador ou no GitHub Pages
  - visualizador/midia/<slug>/*.jpg   versões leves dos slides para exibição

Com --artifact PASTA, escreve também PASTA/pagina.html (sem o esqueleto <html>, no formato
que o Artifact publica) e PASTA/arquivos.json (mapa de arquivos para publicar junto).
"""

import json
import sys
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parents[1].parent
CONTEUDO = RAIZ / "conteudo" / "estaticos"
SAIDA = RAIZ / "visualizador"
TEMPLATE = Path(__file__).with_name("template.html")
REPO_URL = "https://github.com/diasgomesadvoc/fieri/tree/claude/fieri-github-setup-pm7eo5/conteudo/estaticos"

PERFIL = {
    "usuario": "fierigestao",
    "nome": "FIERI",
    "categoria": "Educação",
    "bio": [
        "Inteligência aplicada à gestão de escritórios.",
        "Ebooks, cursos e skills de IA para quem era técnico e virou gestor.",
        "Perceber para transformar.",
    ],
    "site": "fierigestao.com.br",
}


def carregar():
    carrosseis = []
    for cj in sorted(CONTEUDO.glob("*/conteudo.json")):
        pasta = cj.parent
        pngs = sorted((pasta / "png").glob("slide-*.png"))
        if not pngs:
            continue
        dados = json.loads(cj.read_text(encoding="utf-8"))
        slug = pasta.name
        destino = SAIDA / "midia" / slug
        destino.mkdir(parents=True, exist_ok=True)
        slides = []
        for p in pngs:
            jpg = destino / (p.stem + ".jpg")
            if not jpg.exists() or jpg.stat().st_mtime < p.stat().st_mtime:
                Image.open(p).convert("RGB").save(jpg, quality=86, optimize=True, progressive=True)
            slides.append({"nome": p.stem, "jpg": jpg, "png": p})
        carrosseis.append(
            {
                "slug": slug,
                "titulo": dados.get("titulo", slug),
                "ordem": dados.get("ordem_publicacao", len(carrosseis) + 1),
                "status": dados.get("status", "Para aprovação"),
                "objetivo": dados.get("objetivo", ""),
                "legenda": dados.get("legenda", ""),
                "slides": slides,
            }
        )
    carrosseis.sort(key=lambda c: c["ordem"])
    return carrosseis


def manifesto(carrosseis, base_jpg, base_png):
    """Monta o JSON da página com os caminhos relativos ao local onde ela é servida."""
    return {
        "perfil": PERFIL,
        "repo": REPO_URL,
        "avatar": f"{base_jpg}perfil.png",
        "carrosseis": [
            {
                **{k: c[k] for k in ("slug", "titulo", "ordem", "status", "objetivo", "legenda")},
                "slides": [
                    {
                        "nome": s["nome"],
                        "img": f"{base_jpg}midia/{c['slug']}/{s['jpg'].name}",
                        "png": f"{base_png}{c['slug']}/png/{s['png'].name}",
                    }
                    for s in c["slides"]
                ],
            }
            for c in carrosseis
        ],
    }


def pagina(dados, completa: bool) -> str:
    corpo = TEMPLATE.read_text(encoding="utf-8").replace(
        "/*__DADOS__*/null", json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
    )
    if not completa:
        return corpo
    return (
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        "<style>body{margin:0}[hidden]{display:none!important}img{max-width:100%}</style>"
        f"</head><body>{corpo}</body></html>"
    )


def main():
    carrosseis = carregar()
    SAIDA.mkdir(exist_ok=True)
    avatar = RAIZ / "marca/perfil/perfil-ebano.png"
    (SAIDA / "perfil.png").write_bytes(avatar.read_bytes())

    local = manifesto(carrosseis, "", "../conteudo/estaticos/")
    (SAIDA / "index.html").write_text(pagina(local, True), encoding="utf-8")
    print(SAIDA / "index.html", f"({len(carrosseis)} carrosséis)")

    if "--artifact" in sys.argv:
        pasta = Path(sys.argv[sys.argv.index("--artifact") + 1]).resolve()
        pasta.mkdir(parents=True, exist_ok=True)
        pub = manifesto(carrosseis, "", "png/")
        (pasta / "pagina.html").write_text(pagina(pub, False), encoding="utf-8")
        arquivos = {"perfil.png": str(avatar)}
        for c in carrosseis:
            for s in c["slides"]:
                arquivos[f"midia/{c['slug']}/{s['jpg'].name}"] = str(s["jpg"])
                arquivos[f"png/{c['slug']}/png/{s['png'].name}"] = str(s["png"])
        (pasta / "arquivos.json").write_text(json.dumps(arquivos, indent=1), encoding="utf-8")
        print(pasta / "pagina.html", f"({len(arquivos)} arquivos)")


if __name__ == "__main__":
    main()
