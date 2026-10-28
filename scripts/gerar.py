#!/usr/bin/env python3
"""Gera o site de uma filial a partir do modelo e do arquivo de dados dela.

Uso:
    python3 scripts/gerar.py itaguai          # gera dist/itaguai/
    python3 scripts/gerar.py --todas          # gera todas as filiais de filiais/

O que entra em dist/<slug>/:
  - os arquivos de texto de modelo/ (.html, .js, .css, .txt, .xml), com as marcações trocadas
    pelos dados de filiais/<slug>/filial.json;
  - os arquivos binários de modelo/assets/ (comuns a todas as filiais), copiados como estão;
  - filiais/<slug>/assets/ (logo, fotos da cidade), por cima dos comuns.

Marcações do modelo (sem dependência externa, de propósito: roda em qualquer Python 3):
  {{cnpj.numero}}            valor do JSON, com escape de HTML (& < > ")
  {{secao_cidade.x|bruto}}   sem escape (o campo já é HTML, como os créditos das fotos)
  {{cidade|url}}             codificado para URL (assunto de mailto, texto do WhatsApp)
  {{#secao_cidade.fotos}} … {{/secao_cidade.fotos}}
                             repete o trecho para cada item da lista; dentro dele, {{.alt}}
                             lê o campo do item.

Marcação que sobrar sem valor, ou campo que não existir no JSON, derruba a geração: um site
publicado com "{{cidade}}" no meio do texto é pior que um site que não foi gerado.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
import urllib.parse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MODELO = RAIZ / 'modelo'
FILIAIS = RAIZ / 'filiais'
DIST = RAIZ / 'dist'

TEXTO = {'.html', '.js', '.css', '.txt', '.xml', '.json', '.svg', '.webmanifest'}
# Arquivos de modelo/assets/ são copiados sem passar pelo motor (fotos, logos, ícones).
SEM_MOTOR = {'assets'}

LACO = re.compile(r'\{\{#([\w.]+)\}\}(.*?)\{\{/\1\}\}', re.S)
CAMPO = re.compile(r'\{\{(\.?[\w.]*)(?:\|(\w+))?\}\}')


class ErroDeModelo(Exception):
    pass


def ler(dados: dict, caminho: str, onde: str):
    valor = dados
    for parte in caminho.split('.'):
        if not isinstance(valor, dict) or parte not in valor:
            raise ErroDeModelo(f'{onde}: o campo "{caminho}" não existe no filial.json')
        valor = valor[parte]
    return valor


def formatar(valor, filtro: str | None, campo: str, onde: str) -> str:
    if isinstance(valor, (dict, list)):
        raise ErroDeModelo(f'{onde}: "{campo}" é uma lista ou objeto, não um texto')
    texto = str(valor)
    if filtro is None:
        return html.escape(texto, quote=True)
    if filtro == 'bruto':
        return texto
    if filtro == 'url':
        return urllib.parse.quote(texto, safe='')
    raise ErroDeModelo(f'{onde}: filtro desconhecido "|{filtro}" em "{campo}"')


def renderizar(modelo: str, dados: dict, onde: str) -> str:
    def laco(m: re.Match) -> str:
        itens = ler(dados, m.group(1), onde)
        if not isinstance(itens, list):
            raise ErroDeModelo(f'{onde}: "{m.group(1)}" precisa ser uma lista para {{{{#…}}}}')
        partes = []
        for item in itens:
            def do_item(c: re.Match) -> str:
                nome, filtro = c.group(1), c.group(2)
                if not nome.startswith('.'):
                    return c.group(0)  # campo de fora do laço: resolvido na passada seguinte
                return formatar(ler(item, nome[1:], onde), filtro, nome, onde)
            partes.append(CAMPO.sub(do_item, m.group(2)))
        return ''.join(partes)

    texto = LACO.sub(laco, modelo)

    def campo(c: re.Match) -> str:
        nome, filtro = c.group(1), c.group(2)
        if nome.startswith('.') or not nome:
            raise ErroDeModelo(f'{onde}: "{c.group(0)}" fora de um laço')
        return formatar(ler(dados, nome, onde), filtro, nome, onde)

    texto = CAMPO.sub(campo, texto)
    sobra = re.search(r'\{\{[^}]*\}\}', texto)
    if sobra:
        raise ErroDeModelo(f'{onde}: marcação sem valor: {sobra.group(0)}')
    return texto


def gerar(slug: str) -> Path:
    pasta = FILIAIS / slug
    dados = json.loads((pasta / 'filial.json').read_text(encoding='utf-8'))
    if dados.get('slug') != slug:
        raise ErroDeModelo(f'filiais/{slug}/filial.json diz slug "{dados.get("slug")}"')
    destino = DIST / slug
    if destino.exists():
        shutil.rmtree(destino)
    for origem in sorted(MODELO.rglob('*')):
        if origem.is_dir():
            continue
        relativo = origem.relative_to(MODELO)
        alvo = destino / relativo
        alvo.parent.mkdir(parents=True, exist_ok=True)
        if origem.suffix in TEXTO and relativo.parts[0] not in SEM_MOTOR:
            saida = renderizar(origem.read_text(encoding='utf-8'), dados, str(relativo))
            alvo.write_text(saida, encoding='utf-8', newline='')
        else:
            shutil.copy2(origem, alvo)
    proprios = pasta / 'assets'
    if proprios.is_dir():
        shutil.copytree(proprios, destino / 'assets', dirs_exist_ok=True)
    conferir_referencias(destino)
    return destino


def conferir_referencias(destino: Path) -> None:
    """Toda imagem citada numa página precisa ter vindo para dist/ (modelo ou filial)."""
    faltando = []
    for pagina in destino.rglob('*.html'):
        for ref in re.findall(r'(?:src|href)="(/?assets/[^"?#]+)"', pagina.read_text(encoding='utf-8')):
            if not (destino / ref.lstrip('/')).is_file():
                faltando.append(f'{pagina.relative_to(destino)} → {ref}')
    if faltando:
        raise ErroDeModelo('arquivos citados que não existem:\n  ' + '\n  '.join(faltando))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('slug', nargs='?', help='pasta da filial em filiais/')
    p.add_argument('--todas', action='store_true', help='gera todas as filiais')
    args = p.parse_args()
    if args.todas:
        slugs = sorted(d.name for d in FILIAIS.iterdir() if (d / 'filial.json').is_file())
    elif args.slug:
        slugs = [args.slug]
    else:
        p.error('diga a filial (ex.: itaguai) ou use --todas')
    try:
        for slug in slugs:
            destino = gerar(slug)
            print(f'{slug}: gerado em {destino.relative_to(RAIZ)}/')
    except ErroDeModelo as e:
        print(f'erro: {e}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
