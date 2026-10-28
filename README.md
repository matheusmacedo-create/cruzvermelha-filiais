# Cruz Vermelha Brasileira — filiais

Núcleo compartilhado das filiais municipais da Cruz Vermelha Brasileira. **Um código-fonte só,
instalado separadamente em cada filial**: cada uma tem domínio, site, banco, configuração e conta
da Únicopag próprios (é o que o Google para ONGs e a prestação de contas pedem), mas uma correção
feita aqui vale para todas.

| Fase | Filial | Domínio | Repositório próprio |
| --- | --- | --- | --- |
| 1 | Rio de Janeiro | cruzvermelhariodejaneiro.org | `cruzvermelhariodejaneiro` (fora deste núcleo por enquanto) |
| 2 | Itaguaí | cruzvermelhaitaguai.org | `cruzvermelhaitaguai` |
| 3 | Petrópolis | cruzvermelhapetropolis.org | `_cruzvermelhapetropolis` |

## Como funciona

```
modelo/                 o site, com marcações {{…}} no lugar do que muda de filial para filial
  index.html
  privacidade/index.html
  consentimento.js
  assets/               fotos e ícones comuns a todas
filiais/<slug>/
  filial.json           dados da filial: CNPJ, endereço, contatos, medição, fotos da cidade
  assets/               logo e fotos da cidade, por cima dos comuns
scripts/gerar.py        modelo + filial.json → dist/<slug>/ (o site pronto para publicar)
scripts/conferir_no_ar.py  compara dist/<slug>/ com o que está publicado no domínio
```

```bash
python3 scripts/gerar.py itaguai          # gera dist/itaguai/
python3 scripts/gerar.py --todas
python3 scripts/conferir_no_ar.py itaguai # o que difere do que está no ar
```

Só Python 3, sem dependência. As marcações estão descritas no topo de `scripts/gerar.py`. Campo
que faltar no `filial.json` ou marcação que sobrar sem valor derrubam a geração, de propósito.

### Conferência de partida

O modelo nasceu do site de Itaguaí publicado em 28/10/2026, e `gerar.py itaguai` reproduz esse
site **byte a byte** (`index.html`, `privacidade/index.html`, `consentimento.js` e todas as
imagens). Os PNG aparecem como "recomprimidos pela CDN" no `conferir_no_ar.py`: a CDN da
Hostinger entrega uma versão otimizada deles, e o arquivo no servidor é igual ao do repositório.

## Dados de cada filial

Os dados institucionais vêm do Comprovante de Inscrição no CNPJ, transcritos como estão (a fonte
e a data ficam em `cnpj._fonte`). Diretoria, registro em cartório e documentos de pessoas **não**
entram no site: a filial de Itaguaí pediu para não expor.

Fotos da cidade: só com licença que permita o uso (Wikimedia Commons: domínio público, CC0,
CC BY, CC BY-SA) e com o crédito em `secao_cidade.creditos_html`. CC BY e CC BY-SA obrigam o
crédito: ele não sai da página.

## Segredos

Nada de chave, senha ou token neste repositório. Chave da Únicopag, senha do banco e afins vivem
só no servidor de cada filial, em arquivo de configuração fora do Git (`config.php`, já no
`.gitignore`).

## Publicar

Por enquanto, enviando `dist/<slug>/` para `domains/<dominio>/public_html` na conta Hostinger
(gerenciador de arquivos do hPanel ou API de arquivos), e rodando `conferir_no_ar.py` depois.

## Próximos passos

1. Decidir a base do modelo (página única, como Itaguaí, ou várias páginas, como Petrópolis).
2. Núcleo de doação pela Únicopag (`/doe/`), começando por Itaguaí, com banco próprio por filial.
3. Painel do diretor de cada filial.
4. Lista de conferência para filial nova (CNPJ ativo, domínio no nome da filial, conta Únicopag,
   e-mail, cadastro no Google para ONGs).
