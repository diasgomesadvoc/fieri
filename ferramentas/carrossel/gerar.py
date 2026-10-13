"""Gera o HTML de um carrossel FIERI a partir de um conteudo.json.

Uso:
    python3 ferramentas/carrossel/gerar.py conteudo/estaticos/<slug>/conteudo.json

Cria slides.html na mesma pasta: pré-visualização estilo Instagram com todos os
slides. Para exportar os PNGs 1080x1350, rode exportar.mjs no HTML gerado.

Marcação nos textos:
    *palavra*      destaque em Bold Italic Canela (assinatura tipográfica da marca)
    ==trecho==     faixa Canela com texto Marfim (faixa de destaque)
    \\n            quebra de linha
"""

import base64
import html
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
MARCA = RAIZ / "marca"

COR = {
    "ebano": "#26150D",
    "raiz": "#3D2219",
    "canela": "#896449",
    "marfim": "#EDE7DB",
    "branco_off": "#FBFAF6",
}

# Layout em 432x540 px CSS; exportado com device scale 2.5 = 1080x1350.
W, H = 432, 540


def data_uri(caminho: Path) -> str:
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".woff": "font/woff",
    }[caminho.suffix.lower()]
    return f"data:{mime};base64,{base64.b64encode(caminho.read_bytes()).decode()}"


def fontes_css() -> str:
    pesos = [
        ("Regular", 400, "normal"),
        ("Italic", 400, "italic"),
        ("Bold", 700, "normal"),
        ("BoldItalic", 700, "italic"),
    ]
    return "\n".join(
        f"@font-face{{font-family:'Carlito';src:url({data_uri(MARCA / 'fontes/web' / f'Carlito-{n}.woff')}) "
        f"format('woff');font-weight:{p};font-style:{s};}}"
        for n, p, s in pesos
    )


def marcar(texto: str) -> str:
    """Escapa o texto e aplica a marcação de destaque."""
    t = html.escape(texto)
    t = re.sub(r"==(.+?)==", r'<span class="faixa">\1</span>', t)
    t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
    return t.replace("\\n", "<br>").replace("\n", "<br>")


class Assets:
    def __init__(self):
        self._cache = {}

    def get(self, rel: str) -> str:
        if rel not in self._cache:
            self._cache[rel] = data_uri(RAIZ / rel)
        return self._cache[rel]


def tema(fundo: str) -> str:
    return "escuro" if fundo in ("ebano", "raiz", "foto") else "claro"


def fundo_html(s: dict, a: Assets) -> str:
    f = s.get("fundo", "marfim")
    if f == "foto":
        foto = a.get(s["foto"])
        pos = s.get("foto_posicao", "center")
        return (
            f'<img class="bg" src="{foto}" style="object-position:{pos}">'
            f'<div class="veu"></div>'
        )
    if f in ("marfim", "ebano") and s.get("ondas", True):
        return f'<img class="bg" src="{a.get(f"marca/fundos/fundo-{f}-ondas-4x5.jpg")}">'
    return ""


def rodape(i: int, total: int, t: str, a: Assets) -> str:
    logo = a.get(
        "marca/logos/fieri-horizontal-branco-off.png"
        if t == "escuro"
        else "marca/logos/fieri-horizontal-raiz.png"
    )
    pct = (i + 1) / total * 100
    seta = (
        ""
        if i == total - 1
        else '<svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M9 6l6 6-6 6" '
        'stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )
    return (
        f'<div class="rodape"><img class="logo-rodape" src="{logo}" alt="FIERI">'
        f'<span class="contador">{i + 1}/{total}{seta}</span></div>'
        f'<div class="progresso"><div style="width:{pct:.2f}%"></div></div>'
    )


def rotulo(s: dict) -> str:
    return f'<div class="rotulo">{marcar(s["rotulo"])}</div>' if s.get("rotulo") else ""


def slide_capa(s, a):
    sub = f'<p class="subtitulo">{marcar(s["subtitulo"])}</p>' if s.get("subtitulo") else ""
    pre = f'<p class="pretitulo">{marcar(s["pretitulo"])}</p>' if s.get("pretitulo") else ""
    caixa = " caixa" if s.get("caixa") else ""
    return (
        f'<div class="conteudo capa pos-{s.get("posicao", "base")}{caixa}"><div class="bloco">'
        f'{rotulo(s)}{pre}<h1>{marcar(s["titulo"])}</h1>{sub}</div></div>'
    )


def slide_texto(s, a):
    corpo = "".join(f"<p>{marcar(p)}</p>" for p in s.get("corpo", []))
    return (
        f'<div class="conteudo texto pos-{s.get("posicao", "meio")}">{rotulo(s)}'
        f'<h2>{marcar(s["titulo"])}</h2><div class="corpo">{corpo}</div></div>'
    )


def slide_lista(s, a):
    itens = "".join(
        f'<li><span class="num">{i:02d}</span><div><strong>{marcar(it["titulo"])}</strong>'
        + (f'<span>{marcar(it["texto"])}</span>' if it.get("texto") else "")
        + "</div></li>"
        for i, it in enumerate(s["itens"], 1)
    )
    titulo = f'<h2>{marcar(s["titulo"])}</h2>' if s.get("titulo") else ""
    return f'<div class="conteudo lista pos-{s.get("posicao", "meio")}">{rotulo(s)}{titulo}<ol>{itens}</ol></div>'


def slide_frase(s, a):
    apoio = f'<p class="apoio">{marcar(s["apoio"])}</p>' if s.get("apoio") else ""
    return (
        f'<div class="conteudo frase pos-{s.get("posicao", "meio")}">{rotulo(s)}'
        f'<blockquote>{marcar(s["texto"])}</blockquote>{apoio}</div>'
    )


def slide_cta(s, a):
    t = tema(s.get("fundo", "marfim"))
    simbolo = a.get(
        "marca/simbolo/simbolo-marfim.png" if t == "escuro" else "marca/simbolo/simbolo-raiz.png"
    )
    texto = f'<p class="cta-texto">{marcar(s["texto"])}</p>' if s.get("texto") else ""
    acao = f'<div class="cta-acao">{marcar(s["acao"])}</div>' if s.get("acao") else ""
    return (
        f'<div class="conteudo cta"><img class="simbolo" src="{simbolo}" alt="">'
        f'<h2>{marcar(s["titulo"])}</h2>{texto}{acao}'
        f'<p class="assinatura">@fierigestao · fierigestao.com.br</p></div>'
    )


TIPOS = {
    "capa": slide_capa,
    "texto": slide_texto,
    "lista": slide_lista,
    "frase": slide_frase,
    "cta": slide_cta,
}

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#d9d4cc;font-family:'Carlito','Lato',sans-serif;-webkit-font-smoothing:antialiased;
  display:flex;flex-direction:column;align-items:center;gap:28px;padding:32px 12px}
h1,h2,blockquote{font-weight:700;letter-spacing:-0.4px}
em{font-style:italic;font-weight:700;color:var(--destaque)}

.carrossel{display:flex;flex-direction:column;align-items:center;gap:10px}
.carrossel>header{font:700 15px 'Carlito';color:#26150D;align-self:flex-start}
.trilho{display:flex;gap:12px;flex-wrap:wrap;justify-content:center;max-width:1400px}

.slide{position:relative;width:432px;height:540px;overflow:hidden;flex:none}
.slide.claro{background:#EDE7DB;color:#26150D;--destaque:#896449;--fio:#26150D;--suave:rgba(38,21,13,.55)}
.slide.claro.fundo-branco_off{background:#FBFAF6}
.slide.escuro{background:#26150D;color:#EDE7DB;--destaque:#896449;--fio:#EDE7DB;--suave:rgba(237,231,219,.6)}
.slide.escuro.fundo-raiz{background:#3D2219}
.slide .bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:0}
.slide .veu{position:absolute;inset:0;z-index:1;
  background:linear-gradient(180deg,rgba(38,21,13,.15) 0%,rgba(38,21,13,.35) 40%,rgba(38,21,13,.92) 78%,#26150D 100%)}

.conteudo{position:absolute;inset:0;z-index:2;padding:46px 40px 64px;display:flex;flex-direction:column}
.pos-topo{justify-content:flex-start}.pos-meio{justify-content:center}.pos-base{justify-content:flex-end}

.rotulo{font-size:12px;font-weight:700;padding-top:9px;border-top:1.5px solid var(--fio);margin-bottom:16px;align-self:stretch}

.capa h1{font-size:46px;line-height:1.0}
.capa .pretitulo{font-size:17px;font-weight:700;margin-bottom:10px;line-height:1.2}
.capa .subtitulo{font-size:15px;line-height:1.4;margin-top:18px;color:var(--suave);max-width:330px}
.capa.caixa .bloco{background:#26150D;color:#EDE7DB;padding:26px 24px 24px;margin:0 -8px;--suave:rgba(237,231,219,.7);--fio:#EDE7DB;--destaque:#896449}
.faixa{background:#896449;color:#EDE7DB;padding:0 .14em;-webkit-box-decoration-break:clone;box-decoration-break:clone;font-style:normal}
h1 .faixa,h2 .faixa,blockquote .faixa{line-height:1.12}

h2{font-size:31px;line-height:1.06;margin-bottom:18px}
.texto .corpo p{font-size:16px;line-height:1.45;margin-bottom:12px}
.texto .corpo p:last-child{margin-bottom:0}

.lista h2{font-size:27px;margin-bottom:14px}
.lista ol{list-style:none}
.lista li{display:flex;gap:14px;padding:11px 0;border-top:1px solid color-mix(in srgb,var(--fio) 22%,transparent)}
.lista li:last-child{border-bottom:1px solid color-mix(in srgb,var(--fio) 22%,transparent)}
.lista .num{font-size:19px;font-weight:700;font-style:italic;color:var(--destaque);min-width:26px;line-height:1.1}
.lista strong{display:block;font-size:16px;line-height:1.2}
.lista li span:not(.num){display:block;font-size:13.5px;line-height:1.4;color:var(--suave);margin-top:3px}

.frase blockquote{font-size:34px;line-height:1.08}
.frase .apoio{font-size:16px;line-height:1.45;margin-top:20px;color:var(--suave);max-width:340px}

.cta{align-items:center;justify-content:center;text-align:center}
.cta .simbolo{width:120px;margin-bottom:26px}
.cta h2{font-size:30px;margin-bottom:12px}
.cta .cta-texto{font-size:16px;line-height:1.45;color:var(--suave);max-width:320px}
.cta .cta-acao{margin-top:22px;font-size:14px;font-weight:700;padding:10px 20px;border:1.5px solid var(--fio);border-radius:2px}
.cta .assinatura{position:absolute;bottom:62px;font-size:12px;color:var(--suave)}

.rodape{position:absolute;left:40px;right:40px;bottom:20px;z-index:3;display:flex;align-items:center;justify-content:space-between}
.logo-rodape{height:13px;width:auto;opacity:.9}
.contador{display:flex;align-items:center;gap:2px;font-size:11px;font-weight:700;color:var(--suave)}
.progresso{position:absolute;left:0;right:0;bottom:0;height:3px;z-index:3;background:color-mix(in srgb,var(--fio) 10%,transparent)}
.progresso div{height:100%;background:#896449}
.slide.cta-slide .logo-rodape{visibility:hidden}

.legenda{max-width:880px;background:#FBFAF6;padding:16px 20px;font-size:14px;line-height:1.5;color:#26150D;white-space:pre-wrap;border-radius:4px}
"""


def gerar(caminho_json: Path) -> Path:
    dados = json.loads(caminho_json.read_text(encoding="utf-8"))
    a = Assets()
    blocos = []
    total = len(dados["slides"])
    for i, s in enumerate(dados["slides"]):
        f = s.get("fundo", "marfim")
        t = tema(f)
        extra = " cta-slide" if s["tipo"] == "cta" else ""
        blocos.append(
            f'<div class="slide {t} fundo-{f}{extra}" data-n="{i + 1}">'
            f"{fundo_html(s, a)}{TIPOS[s['tipo']](s, a)}{rodape(i, total, t, a)}</div>"
        )
    legenda = html.escape(dados.get("legenda", ""))
    doc = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(dados.get("titulo", "Carrossel FIERI"))}</title>
<style>{fontes_css()}{CSS}</style></head><body>
<section class="carrossel"><header>{html.escape(dados.get("titulo", ""))}</header>
<div class="trilho">{"".join(blocos)}</div>
{f'<div class="legenda">{legenda}</div>' if legenda else ""}
</section></body></html>"""
    saida = caminho_json.with_name("slides.html")
    saida.write_text(doc, encoding="utf-8")
    return saida


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print(gerar(Path(arg).resolve()))
