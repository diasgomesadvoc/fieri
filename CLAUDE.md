# Fieri — instruções para o Claude

Projeto para criar conteúdo estático (posts, carrosséis, stories) e editar vídeos (Reels) para o Instagram.

## Antes de criar qualquer conteúdo, leia
1. `marca/identidade-visual.md` — cores, fontes, logo e tom de voz. Seguir sempre.
2. `referencias/estudo.md` — padrões aprendidos com as referências.

## Regras rápidas da marca FIERI (detalhes em `marca/identidade-visual.md`)
- Cores: Ébano #26150D · Raiz #3D2219 · **Canela #896449 (destaque)** · Marfim #EDE7DB · Branco Off #FBFAF6. Nada de azul ou cinza frio.
- Fonte: Carlito (= Lato). Títulos em Bold; palavra-chave em *Bold Italic* Canela.
- Logo: usar os PNGs de `marca/logos/` inteiros, sem esticar nem recolorir. Nunca digitar "FIERI" no lugar da logo.
- Ondas: só nos cantos, tom sobre tom, nunca inteiras.
- Tom de voz: sereno, próximo, prático, provocativo (sem arrogância e sem urgência).
- Público: donos de escritórios (advocacia, contabilidade, arquitetura) que viraram gestores.
- Perfil: @fierigestao · fierigestao.com.br

## Pastas
- `marca/` — identidade visual: `manual/`, `logos/`, `simbolo/`, `perfil/`, `fundos/`, `imagens/`, `mockups/`, `fontes/`, `paleta/`
- `referencias/` — materiais de referência enviados pelo usuário
- `conteudo/` — peças produzidas (estáticos e vídeos)

## Como produzir um carrossel
1. Escreva `conteudo/estaticos/<NN-slug>/conteudo.json` (tipos de slide e marcação em `ferramentas/carrossel/gerar.py`).
2. `python3 ferramentas/carrossel/gerar.py conteudo/estaticos/<NN-slug>/conteudo.json` → `slides.html`
3. `node ferramentas/carrossel/exportar.mjs conteudo/estaticos/<NN-slug>/slides.html` → `png/slide-XX.png` (1080x1350)
4. `python3 ferramentas/visualizador/gerar.py --artifact <pasta>` e republique a plataforma.

Plataforma de visualização (Estúdio FIERI): https://claude.ai/artifact/7JPVQmffeudBDSGoRrCNcw
Para atualizar de outra sessão, publique `<pasta>/pagina.html` passando essa URL em `url` e os arquivos de `<pasta>/arquivos.json` em `files`.

## Formatos do Instagram
- Post/carrossel: 1080x1350 (4:5) ou 1080x1080
- Stories/Reels: 1080x1920 (9:16)

Idioma do conteúdo: português do Brasil.
