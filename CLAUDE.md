# Regras para agentes neste repositório

Leia o `README.md` antes de mexer: ele explica o modelo, os dados por filial e o gerador.

- **Interface, textos, comentários e commits em português do Brasil.**
- **Nunca grave segredo aqui**: chave da Únicopag, senha de banco, token de API. Eles vivem só no
  servidor de cada filial, fora do Git. Se alguém colar uma chave no chat, use-a só onde ela
  precisa estar (o arquivo de configuração no servidor) e nunca a escreva num arquivo do repositório.
- **O que é comum vai para `nucleo/` e `scripts/gerar.py`; o que é da filial, para
  `filiais/<slug>/`** (dados no `filial.json`, textos em `paginas/`, fotos no `fotos.json`). Ao mexer
  no núcleo, rode `python3 scripts/gerar.py --todas` e `python3 scripts/conferir_no_ar.py petropolis`:
  Petrópolis precisa continuar com 0 diferentes, salvo quando a mudança é para ela.
- **Texto de filial só afirma o que ela faz.** Não copie ação, programa ou número de uma filial para
  outra.
- **Dados institucionais saem do cartão CNPJ**, transcritos como estão. Não invente número,
  endereço, telefone ou dado de diretoria; diretoria e documentos de pessoas não vão para o site.
- **Fotos só com licença livre e crédito**, como descrito no README.
- O aviso de cookies (`consentimento.js`) e o bloco de medição do `<head>` seguem a LGPD e o Guia
  de Cookies da ANPD: Google Analytics e Pixel da Meta só carregam depois do "sim". Nunca recoloque
  o `<noscript>` com a imagem do Pixel.
- A metatag `facebook-domain-verification` precisa ficar no HTML estático (fora de JavaScript).
- Publicar: gere, envie `dist/<slug>/` para a pasta do domínio e rode
  `python3 scripts/conferir_no_ar.py <slug>`. Relate o que conferiu de verdade.
