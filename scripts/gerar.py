#!/usr/bin/env python3
"""Gera o site de uma filial: núcleo comum + dados, textos e arquivos da filial → dist/<slug>/.

Uso:
    python3 scripts/gerar.py petropolis
    python3 scripts/gerar.py --todas

Veio de pagina/scripts/gerar_site_petropolis.py (repositório _cruzvermelhapetropolis), que gerou o
site de Petrópolis publicado em 27/10/2026. Daqui sai o mesmo site, byte a byte, a partir de
filiais/petropolis/.

O que cada parte guarda:
  nucleo/                     o que é igual em todas: estilo, script do menu, favicon, aviso de cookies,
                              bloco de medição, Princípios Fundamentais, rodapé, cabeçalho.
  filiais/<slug>/filial.json  dados do cartão CNPJ, contatos, menu, páginas (título, descrição,
                              faixa do topo) e, se houver, a medição (Google Analytics, Pixel).
  filiais/<slug>/paginas/     o miolo de cada página, em HTML, com marcações {{…}} (abaixo).
  filiais/<slug>/estaticos/   copiado como está para a raiz do site: fotos, logo, favicon, .htaccess.
  filiais/<slug>/fotos.json   cada foto (em estaticos/assets/fotos/) com tamanho, alt, legenda, autor
                              e licença; alimenta as legendas e a página de créditos.

Marcações dentro de paginas/*.html:
  {{f campo}}             dado da filial com escape de HTML (nome, curto, cnpj, rua, bairro, cidade,
                          uf, cep, email, cnpj_desde…); {{fb campo}} sem escape
  {{foto chave classe carregar}}   <img> de uma foto do fotos.json (classe "-" = vazia;
                          carregar = lazy ou eager)
  {{legenda chave}}       <figcaption> com o crédito da foto; {{legenda_texto chave}} só o texto
  {{icone nome}}          ícone em SVG (lista em ICONES)
  {{tels separador}}      telefones com link; separador: ponto ( · ), ou ( ou ), br (<br>)
  {{mapa}} {{endereco}}   link do Google Maps e endereço numa linha
  {{whatsapp_link}}       https://wa.me/55… do campo "whatsapp" da filial
  {{chips}} {{principios}} {{creditos}}   blocos prontos do núcleo

Marcação desconhecida, campo que falta ou foto que não existe derrubam a geração.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
import urllib.parse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
NUCLEO = RAIZ / "nucleo"
FILIAIS = RAIZ / "filiais"
DIST = RAIZ / "dist"


class ErroDeGeracao(Exception):
    pass


def esc(s: str) -> str:
    return html.escape(s, quote=True)


ICONES = {
    "mao": '<path d="M12 21s-7-4.4-9.3-9A5.5 5.5 0 0 1 12 6a5.5 5.5 0 0 1 9.3 6c-2.3 4.6-9.3 9-9.3 9z"/>',
    "pessoas": '<circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><circle cx="17" cy="9" r="2.6"/><path d="M15.5 14.2A5 5 0 0 1 21 19"/>',
    "predio": '<path d="M4 21V8l8-5 8 5v13"/><path d="M9 21v-6h6v6"/><path d="M4 21h16"/>',
    "chuva": '<path d="M7 15a5 5 0 1 1 1.6-9.7A6 6 0 0 1 20 9a4 4 0 0 1-1 7.9"/><path d="M9 18l-1 3M13 18l-1 3M17 18l-1 3"/>',
    "telefone": '<path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2z"/>',
    "email": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "local": '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "mochila": '<rect x="5" y="7" width="14" height="14" rx="3"/><path d="M9 7V5a3 3 0 0 1 6 0v2M9 13h6"/>',
    "sms": '<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M10 18h4"/>',
    "conversa": '<path d="M4 19l1.6-4.2A7.5 7.5 0 1 1 9 18.4z"/>',
}

PRINCIPIOS = [
    ("Humanidade", "Prevenir e aliviar o sofrimento humano em todas as circunstâncias, proteger a vida e a saúde e fazer respeitar a pessoa humana, favorecendo a compreensão mútua, a amizade, a cooperação e uma paz duradoura entre os povos."),
    ("Imparcialidade", "Não fazer distinção de nacionalidade, raça, religião, condição social ou opinião política. Atender as pessoas apenas na medida das suas necessidades, dando prioridade aos casos mais urgentes."),
    ("Neutralidade", "Para manter a confiança de todos, não tomar partido nas hostilidades nem nas controvérsias de ordem política, racial, religiosa ou ideológica."),
    ("Independência", "Auxiliar os poderes públicos nas atividades humanitárias, sujeita às leis do país, mas conservando sempre a autonomia que permite agir de acordo com os Princípios."),
    ("Voluntariado", "Ser uma instituição de socorro voluntária e desinteressada, sem qualquer busca de lucro."),
    ("Unidade", "Só pode existir uma Sociedade da Cruz Vermelha ou do Crescente Vermelho em cada país, aberta a todos e com ação humanitária em todo o território."),
    ("Universalidade", "O Movimento é universal: todas as Sociedades Nacionais têm os mesmos direitos e o dever de se ajudar mutuamente."),
]


def icone(nome: str) -> str:
    if nome not in ICONES:
        raise ErroDeGeracao(f'ícone desconhecido "{nome}"')
    return (
        '<svg class="icone" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" '
        f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONES[nome]}</svg>'
    )


class Filial:
    """Os dados de uma filial e os pedaços de HTML que dependem deles."""

    def __init__(self, slug: str):
        self.slug = slug
        self.pasta = FILIAIS / slug
        self.dados = json.loads((self.pasta / "filial.json").read_text(encoding="utf-8"))
        if self.dados.get("slug") != slug:
            raise ErroDeGeracao(f'filiais/{slug}/filial.json diz slug "{self.dados.get("slug")}"')
        self.f = self.dados["filial"]
        self.origem = "https://" + self.dados["dominio"]
        self.fotos = json.loads((self.pasta / "fotos.json").read_text(encoding="utf-8"))
        self.tel = {t: "+55" + "".join(c for c in t if c.isdigit()) for t in self.f["telefones"]}
        self.endereco = f'{self.f["rua"]} · {self.f["bairro"]} · {self.f["cidade"]}/{self.f["uf"]} · CEP {self.f["cep"]}'
        consulta = f'{self.f["rua"]}, {self.f["bairro"]}, {self.f["cidade"]} - {self.f["uf"]}, {self.f["cep"]}'
        self.mapa = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote_plus(consulta)
        self.menu = [(m["href"], m["rotulo"]) for m in self.dados["menu"]]
        self.medicao = self.dados.get("medicao")

    # ------------------------------------------------------------------ pedaços
    def foto(self, chave: str, classe: str = "", carregar: str = "lazy") -> str:
        if chave not in self.fotos:
            raise ErroDeGeracao(f'foto "{chave}" não está no fotos.json')
        f = self.fotos[chave]
        return (
            f'<img class="{classe}" src="/assets/fotos/{f["arquivo"]}" width="{f["largura"]}" height="{f["altura"]}" '
            f'alt="{esc(f["alt"])}" loading="{carregar}" decoding="async">'
        )

    def legenda(self, chave: str) -> str:
        f = self.fotos[chave]
        return f'<figcaption>{esc(f["legenda"])} <a href="/creditos/">Foto: {esc(f["autor"])}, {esc(f["licenca"])}</a></figcaption>'

    def tels(self, separador: str) -> str:
        return separador.join(f'<a href="tel:{self.tel[t]}">{t}</a>' for t in self.f["telefones"])

    def chips(self) -> str:
        return "".join(f'<li><a href="/principios-fundamentais/#{p[0].lower()}">{p[0]}</a></li>' for p in PRINCIPIOS)

    def principios(self) -> str:
        return "".join(
            f'<article class="principio" id="{n.lower()}"><span class="numero">{i}</span><div><h2>{n}</h2><p>{t}</p></div></article>'
            for i, (n, t) in enumerate(PRINCIPIOS, 1)
        )

    def creditos(self) -> str:
        return "".join(
            f'<li><b>{esc(f["legenda"])}</b> — {esc(f["autor"])}, <a href="{esc(f["licenca_url"])}" rel="noopener" target="_blank">{esc(f["licenca"])}</a>, via <a href="{esc(f["origem"])}" rel="noopener" target="_blank">Wikimedia Commons</a>{", recortada e reduzida" if f.get("editada") else ""}.</li>'
            for f in self.fotos.values()
        )

    # ------------------------------------------------------------------ marcações
    SEPARADORES = {"ponto": " · ", "ou": " ou ", "br": "<br>"}

    def renderizar(self, modelo: str, onde: str) -> str:
        def troca(m: re.Match) -> str:
            partes = m.group(1).split()
            nome, args = partes[0], partes[1:]
            try:
                if nome == "f":
                    return esc(str(self.f[args[0]]))
                if nome == "fb":
                    return str(self.f[args[0]])
                if nome == "foto":
                    chave = args[0]
                    classe = "" if len(args) < 2 or args[1] == "-" else args[1]
                    carregar = args[2] if len(args) > 2 else "lazy"
                    return self.foto(chave, classe, carregar)
                if nome == "legenda":
                    return self.legenda(args[0])
                if nome == "legenda_texto":
                    return esc(self.fotos[args[0]]["legenda"])
                if nome == "icone":
                    return icone(args[0])
                if nome == "tels":
                    return self.tels(self.SEPARADORES[args[0]])
                if nome == "whatsapp_link" and not args:
                    return "https://wa.me/55" + "".join(c for c in self.f["whatsapp"] if c.isdigit())
                if nome == "mapa" and not args:
                    return self.mapa
                if nome == "endereco" and not args:
                    return esc(self.endereco)
                if nome in ("chips", "principios", "creditos") and not args:
                    return getattr(self, nome)()
            except (KeyError, IndexError) as e:
                raise ErroDeGeracao(f'{onde}: marcação "{m.group(0)}" sem valor ({e})') from None
            raise ErroDeGeracao(f'{onde}: marcação desconhecida "{m.group(0)}"')

        return re.sub(r"\{\{([^{}]+)\}\}", troca, modelo)

    # ------------------------------------------------------------------ moldura
    def cabecalho(self, atual: str) -> str:
        itens = "".join(
            f'<a href="{href}"{" aria-current=\"page\"" if href == atual else ""}>{rotulo}</a>' for href, rotulo in self.menu
        )
        logo = self.dados["logo"]
        return f"""<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<header class="topo">
  <div class="wrap topo-linha">
    <a class="marca" href="/" aria-label="{esc(self.f['curto'])}: início">
      <img src="{logo['arquivo']}" width="{logo['largura']}" height="{logo['altura']}" alt="{esc(logo['alt'])}">
    </a>
    <button class="menu-botao" type="button" aria-expanded="false" aria-controls="menu">Menu</button>
    <nav id="menu" class="menu" aria-label="Menu principal">{itens}<a class="botao botao-vermelho" href="/doe/">Doe</a></nav>
  </div>
</header>"""

    def rodape(self) -> str:
        logo = self.dados["logo"]
        extras = [("/doe/", "Doe"), ("/privacidade/", "Privacidade"), ("/creditos/", "Créditos das fotos")]
        links = "".join(f'<li><a href="{h}">{r}</a></li>' for h, r in self.menu + extras)
        if self.medicao:
            links += '<li><a href="/privacidade/#cookies" data-cookies>Preferências de cookies</a></li>'
        whatsapp = ""
        if self.f.get("whatsapp"):
            numero = "55" + "".join(c for c in self.f["whatsapp"] if c.isdigit())
            whatsapp = f'\n      <p>{icone("conversa")} WhatsApp <a href="https://wa.me/{numero}" rel="noopener" target="_blank">{self.f["whatsapp"]}</a></p>'
        return f"""<footer class="rodape">
  <div class="wrap rodape-grade">
    <div>
      <img class="rodape-logo" src="{logo['arquivo']}" width="{logo['largura']}" height="{logo['altura']}" alt="{esc(logo['alt'])}" loading="lazy">
      <p>{esc(self.f['nome'])}<br>CNPJ {self.f['cnpj']}</p>
    </div>
    <div>
      <h2>Fale com a filial</h2>
      <p>{icone('local')} <a href="{self.mapa}" rel="noopener" target="_blank">{esc(self.endereco)}</a></p>
      <p>{icone('telefone')} {self.tels(' · ')}</p>{whatsapp}
      <p>{icone('email')} <a href="mailto:{self.f['email']}">{self.f['email']}</a></p>
    </div>
    <div>
      <h2>Navegue</h2>
      <ul>{links}</ul>
    </div>
  </div>
  <div class="wrap rodape-fim">
    <p>Em emergência: Defesa Civil <a href="tel:199">199</a> · Bombeiros <a href="tel:193">193</a> · SAMU <a href="tel:192">192</a>. A filial não faz atendimento de urgência.</p>
    <p>&copy; 2026 {esc(self.f['nome'])}. Parte do Movimento Internacional da Cruz Vermelha e do Crescente Vermelho.</p>
  </div>
</footer>"""

    def organizacao(self) -> dict:
        cep = "".join(c for c in self.f["cep"] if c.isdigit())
        return {
            "@context": "https://schema.org",
            "@type": "NGO",
            "@id": self.origem + "/#organizacao",
            "name": self.f["nome"],
            "alternateName": self.f["curto"],
            "url": self.origem + "/",
            "logo": self.origem + self.dados["logo_organizacao"],
            "email": self.f["email"],
            "telephone": [self.tel[t] for t in self.f["telefones"]],
            "taxID": self.f["cnpj"],
            "address": {
                "@type": "PostalAddress",
                "streetAddress": self.f["rua"],
                "addressLocality": self.f["cidade"],
                "addressRegion": self.f["uf"],
                "postalCode": f"{cep[:5]}-{cep[5:]}",
                "addressCountry": "BR",
            },
            "parentOrganization": {"@type": "NGO", "name": "Cruz Vermelha Brasileira"},
        }

    def medicao_head(self) -> str:
        if not self.medicao:
            return ""
        bloco = (NUCLEO / "medicao.html").read_text(encoding="utf-8")
        bloco = (bloco.replace("__GA__", self.medicao["google_analytics"])
                 .replace("__PIXEL__", self.medicao["pixel_meta"])
                 .replace("__PREFIXO__", self.medicao["prefixo"]))
        verificacao = self.medicao.get("facebook_verificacao")
        meta = f'  <meta name="facebook-domain-verification" content="{verificacao}">\n' if verificacao else ""
        return meta + bloco

    def topo_de_pagina(self, topo: dict) -> str:
        return f"""<section class="faixa-foto">
  {self.foto(topo["foto"], "faixa-foto-img", "eager")}
  <div class="wrap faixa-foto-texto">
    <p class="eyebrow">{esc(topo["eyebrow"])}</p>
    <h1>{esc(topo["titulo"])}</h1>
    <p>{topo["texto"]}</p>
  </div>
</section>"""

    def pagina(self, pg: dict, versao_css: str, versao_js: str) -> tuple[Path, str]:
        caminho = pg["caminho"]
        url = self.origem + caminho
        og = self.origem + "/assets/fotos/" + self.fotos[pg.get("foto_social", "hero")]["arquivo"]
        ld = json.dumps(self.organizacao(), ensure_ascii=False, separators=(",", ":"))
        miolo = (self.pasta / "paginas" / pg["arquivo"]).read_text(encoding="utf-8")
        corpo = self.renderizar(miolo, f'paginas/{pg["arquivo"]}').rstrip("\n")
        if pg.get("topo"):
            corpo = self.topo_de_pagina(pg["topo"]) + corpo
        extra_css = f'\n  <link rel="stylesheet" href="/assets/complementos.css?v={versao(NUCLEO / "assets" / "complementos.css")}">' if pg.get("complementos") else ""
        doc = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(pg['titulo'])}</title>
  <meta name="description" content="{esc(pg['descricao'])}">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="pt_BR">
  <meta property="og:site_name" content="{esc(self.f['curto'])}">
  <meta property="og:title" content="{esc(pg['titulo'])}">
  <meta property="og:description" content="{esc(pg['descricao'])}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{og}">
  <meta name="theme-color" content="#cc0000">
  <link rel="icon" href="/favicon.ico">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
  <link rel="stylesheet" href="/assets/site.css?v={versao_css}">{extra_css}
  <script type="application/ld+json">{ld}</script>
{self.medicao_head()}</head>
<body>
{self.cabecalho(caminho)}
<main id="conteudo">
{corpo}
</main>
{self.rodape()}
<script src="/assets/site.js?v={versao_js}" defer></script>
{'<script src="/consentimento.js?v=' + versao(NUCLEO / 'consentimento.js') + '" defer></script>' + chr(10) if self.medicao else ''}</body>
</html>
"""
        if caminho == "/":
            destino = "index.html"
        elif caminho.endswith(".html"):
            destino = caminho.lstrip("/")
        else:
            destino = caminho.strip("/") + "/index.html"
        return Path(destino), doc

    def sitemap(self) -> str:
        data = self.dados["atualizado_em"]
        urls = "".join(
            f"  <url><loc>{self.origem}{pg['caminho']}</loc><lastmod>{data}</lastmod></url>\n"
            for pg in self.dados["paginas"] if pg.get("no_sitemap", True)
        )
        return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'


def versao(arquivo: Path) -> str:
    return hashlib.sha256(arquivo.read_bytes()).hexdigest()[:10]


def gerar(slug: str) -> Path:
    filial = Filial(slug)
    destino = DIST / slug
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(NUCLEO / "estaticos", destino)
    shutil.copytree(filial.pasta / "estaticos", destino, dirs_exist_ok=True)
    (destino / "assets").mkdir(exist_ok=True)
    for nome in ("site.css", "site.js"):
        shutil.copy2(NUCLEO / "assets" / nome, destino / "assets" / nome)
    if any(pg.get("complementos") for pg in filial.dados["paginas"]):
        shutil.copy2(NUCLEO / "assets" / "complementos.css", destino / "assets" / "complementos.css")
    if filial.medicao:
        js = (NUCLEO / "consentimento.js").read_text(encoding="utf-8").replace("__PREFIXO__", filial.medicao["prefixo"])
        (destino / "consentimento.js").write_text(js, encoding="utf-8")
    versao_css, versao_js = versao(NUCLEO / "assets" / "site.css"), versao(NUCLEO / "assets" / "site.js")
    for pg in filial.dados["paginas"]:
        rel, doc = filial.pagina(pg, versao_css, versao_js)
        (destino / rel).parent.mkdir(parents=True, exist_ok=True)
        (destino / rel).write_text(doc, encoding="utf-8")
    (destino / "sitemap.xml").write_text(filial.sitemap(), encoding="utf-8")
    (destino / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {filial.origem}/sitemap.xml\n", encoding="utf-8")
    conferir_referencias(destino)
    return destino


def conferir_referencias(destino: Path) -> None:
    """Toda imagem, folha de estilo e script citados por uma página precisam estar em dist/."""
    faltando = []
    for pagina in destino.rglob("*.html"):
        for ref in re.findall(r'(?:src|href)="(/(?:assets/|consentimento)[^"?#]*)', pagina.read_text(encoding="utf-8")):
            if not (destino / ref.lstrip("/")).is_file():
                faltando.append(f"{pagina.relative_to(destino)} → {ref}")
    if faltando:
        raise ErroDeGeracao("arquivos citados que não existem:\n  " + "\n  ".join(sorted(set(faltando))))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("slug", nargs="?", help="pasta da filial em filiais/")
    p.add_argument("--todas", action="store_true", help="gera todas as filiais")
    args = p.parse_args()
    if args.todas:
        slugs = sorted(d.name for d in FILIAIS.iterdir() if (d / "filial.json").is_file())
    elif args.slug:
        slugs = [args.slug]
    else:
        p.error("diga a filial (ex.: petropolis) ou use --todas")
    try:
        for slug in slugs:
            print(f"{slug}: gerado em {gerar(slug).relative_to(RAIZ)}/")
    except ErroDeGeracao as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
