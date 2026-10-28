#!/usr/bin/env python3
"""Compara o que o gerador produziu (dist/<slug>/) com o que está publicado no domínio da filial.

Uso: python3 scripts/conferir_no_ar.py itaguai

Só lê: baixa cada arquivo de dist/<slug>/ pelo endereço público e diz quais diferem. Rode antes
de publicar (para ver o que vai mudar) e depois (para confirmar que subiu o que devia).

PNG e JPEG não são comparados byte a byte: a CDN da Hostinger (hcdn) entrega uma versão
recomprimida deles, então o arquivo no ar nunca é idêntico ao do servidor. Para esses, basta a
imagem existir no ar; o tamanho real no servidor se confere pela listagem de arquivos do hPanel.
"""
import json
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def baixar(url: str) -> bytes | None:
    pedido = urllib.request.Request(url, headers={'User-Agent': 'cruzvermelha-filiais/conferir'})
    try:
        with urllib.request.urlopen(pedido, timeout=30) as r:
            return r.read()
    except Exception:
        return None


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    slug = sys.argv[1]
    dominio = json.loads((RAIZ / 'filiais' / slug / 'filial.json').read_text(encoding='utf-8'))['dominio']
    dist = RAIZ / 'dist' / slug
    if not dist.is_dir():
        print(f'gere antes: python3 scripts/gerar.py {slug}')
        return 2
    iguais, diferentes, recomprimidas = 0, [], 0
    # .htaccess nunca é servido ao público: confira-o pela listagem de arquivos do hPanel.
    for arquivo in sorted(p for p in dist.rglob('*') if p.is_file() and p.name != '.htaccess'):
        rel = arquivo.relative_to(dist).as_posix()
        caminho = rel[:-len('index.html')] if rel.endswith('index.html') else rel
        no_ar = baixar(f'https://{dominio}/{caminho}')
        if no_ar == arquivo.read_bytes():
            iguais += 1
        elif no_ar is not None and arquivo.suffix.lower() in {'.png', '.jpg', '.jpeg'}:
            recomprimidas += 1
        else:
            diferentes.append(rel + ('  (não existe no ar)' if no_ar is None else ''))
    extra = f', {recomprimidas} imagens recomprimidas pela CDN' if recomprimidas else ''
    print(f'{dominio}: {iguais} iguais, {len(diferentes)} diferentes{extra}')
    for rel in diferentes:
        print('  ≠', rel)
    return 1 if diferentes else 0


if __name__ == '__main__':
    sys.exit(main())
