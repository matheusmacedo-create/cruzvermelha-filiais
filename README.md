# Cruz Vermelha Brasileira — filiais

Núcleo compartilhado das filiais municipais da Cruz Vermelha Brasileira. **Um código-fonte só,
instalado separadamente em cada filial**: cada uma tem domínio, site, banco, configuração e conta
da Únicopag próprios (é o que o Google para ONGs e a prestação de contas pedem), mas uma correção
feita aqui vale para todas.

| Fase | Filial | Domínio | Repositório próprio |
| --- | --- | --- | --- |
| 1 | Rio de Janeiro | cruzvermelhariodejaneiro.org | `cruzvermelhariodejaneiro` (fora deste núcleo por enquanto) |
| 2 | Itaguaí | cruzvermelhaitaguai.org | `cruzvermelhaitaguai` |
| 3 | Petrópolis | cruzvermelhapetropolis.org | `_cruzvermelhapetropolis` (a Redação fica lá) |

## Como funciona

O modelo é o site de Petrópolis (27/10/2026): várias páginas, só fotos da cidade, de licença livre.
O gerador veio de `pagina/scripts/gerar_site_petropolis.py` e reproduz aquele site **byte a byte**
a partir de `filiais/petropolis/`.

```
nucleo/
  assets/site.css, site.js    estilo e menu do celular, iguais em todas
  assets/complementos.css     só para páginas que pedem (a política LGPD completa)
  estaticos/                  copiado para todas (favicon)
  consentimento.js            aviso de cookies (LGPD), só para filial com medição
  medicao.html                bloco do <head> que só baixa GA e Pixel depois do "sim"
filiais/<slug>/
  filial.json                 dados do cartão CNPJ, contatos, logo, menu, páginas, medição
  fotos.json                  cada foto: arquivo, tamanho, alt, legenda, autor, licença, origem
  paginas/*.html              o miolo de cada página, com marcações {{…}}
  estaticos/                  copiado como está: fotos, logo, .htaccess
scripts/gerar.py              núcleo + filial → dist/<slug>/ (o site pronto para publicar)
scripts/conferir_no_ar.py     compara dist/<slug>/ com o que está publicado no domínio
```

```bash
python3 scripts/gerar.py --todas
python3 scripts/conferir_no_ar.py petropolis   # 0 diferentes = o núcleo não mudou nada no ar
```

Só Python 3, sem dependência. As marcações estão no topo de `scripts/gerar.py`. Campo que falte,
foto que não exista ou marcação desconhecida derrubam a geração, de propósito.

O que é comum mora no núcleo (cabeçalho, rodapé, `<head>`, Princípios Fundamentais, créditos,
sitemap, robots). O que é da filial mora em `filiais/<slug>/`: o texto de cada página é dela, porque
cada cidade tem a sua história e as suas ações. **Não invente ação, número ou programa**: o texto
de uma filial só afirma o que ela de fato faz.

### Medição e consentimento

Filial com `medicao` no `filial.json` (Itaguaí) ganha o aviso de cookies, o bloco de medição no
`<head>`, a metatag de verificação do domínio no Facebook e o link "Preferências de cookies" no
rodapé. GA e Pixel só são baixados depois do "sim" (LGPD; Guia de Cookies da ANPD). A política de
privacidade dessa filial precisa ter a seção de cookies (`#cookies`) com a tabela. Filial sem
`medicao` (Petrópolis) não usa cookie nenhum, e a política dela diz isso.

## Dados de cada filial

Os dados institucionais vêm do Comprovante de Inscrição no CNPJ (`filial._fonte` diz qual).
Diretoria, registro em cartório e documentos de pessoas **não** entram no site.

Fotos: só com licença que permita o uso (Wikimedia Commons: domínio público, CC0, CC BY, CC BY-SA),
com autor e licença no `fotos.json`; a página `/creditos/` e as legendas saem dele.

## Segredos

Nada de chave, senha ou token neste repositório. Chave da Únicopag, senha do banco e afins vivem
só no servidor de cada filial, em arquivo de configuração fora do Git (`config.php`, no `.gitignore`).

## Publicar

Enviar `dist/<slug>/` para `domains/<dominio>/public_html` na conta Hostinger (gerenciador de
arquivos do hPanel ou API de arquivos) e rodar `conferir_no_ar.py`. Os PNG aparecem como
"recomprimidos pela CDN": a CDN da Hostinger entrega uma versão otimizada deles. O `.htaccess` não
é servido ao público; confira-o pela listagem do hPanel.

## Próximos passos

1. Núcleo de doação pela Únicopag (`/doe/`), começando por Itaguaí, com banco próprio por filial.
2. Painel do diretor de cada filial.
3. Lista de conferência para filial nova (CNPJ ativo, domínio no nome da filial, conta Únicopag,
   e-mail, cadastro no Google para ONGs).
4. Levar o `site.css` ao núcleo de verdade (hoje o comentário dele ainda fala de Petrópolis; mudar
   troca a versão do CSS em Petrópolis, então vai junto com a próxima publicação de lá).
