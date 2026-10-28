/* Aviso de cookies do site (LGPD; Guia de Cookies da ANPD, 2022).
 *
 * Mesmo desenho do aviso de cruzvermelhariodejaneiro.org (site/consentimento/consentimento.js):
 * primeiro nível com três botões do mesmo tamanho (Rejeitar, Personalizar, Aceitar todos); segundo
 * nível com as categorias, estatística e marketing desligados até a pessoa ligar.
 *
 * A escolha fica no cookie {{prefixo_js}}_consentimento (necessário), só neste domínio, por 12 meses, no mesmo
 * formato do site do Rio (v=1&e=<0|1>&m=<0|1>&t=<s>). O cookie de lá não vale aqui: é de outro domínio.
 *
 * Quem baixa o Google Analytics e o Pixel da Meta é o bloco de medição do <head> (window.{{prefixo_js}}Medicao):
 * sem escolha, ou com "não", nada é baixado. Este arquivo só pergunta, grava e avisa o bloco.
 *
 * "Preferências de cookies": qualquer elemento com data-cookies reabre as categorias.
 */
(function () {
  'use strict';
  if (window.{{prefixo_js}}Consentimento) return;

  var NOME = '{{prefixo_js}}_consentimento';
  var VERSAO = '1';
  var VALIDADE_S = 365 * 24 * 60 * 60;
  var URL_POLITICA = '/privacidade/#cookies';

  var T = {
    titulo: 'Sua privacidade',
    texto: 'Usamos um cookie necessário para guardar a sua escolha. Com a sua permissão, usamos também cookies de estatística (Google Analytics), para saber quais partes do site são lidas, e de marketing (Pixel da Meta), para medir as nossas campanhas no Facebook e no Instagram. Você escolhe, e pode mudar quando quiser em “Preferências de cookies”, no rodapé.',
    politica: 'Política de Privacidade',
    rejeitar: 'Rejeitar', personalizar: 'Personalizar', aceitar: 'Aceitar todos',
    painel: 'Preferências de cookies',
    intro: 'Escolha quais cookies podemos usar. O necessário fica sempre ligado, porque é ele que guarda a sua escolha.',
    categorias: {
      necessarios: ['Necessários', 'Guardam a sua escolha sobre cookies, para o aviso não aparecer de novo a cada página.'],
      estatistica: ['Estatística', 'Google Analytics: conta as visitas e mostra quais partes do site são lidas, sem identificar você pelo nome.'],
      marketing: ['Marketing', 'Pixel da Meta (Facebook e Instagram): mede o alcance e o resultado das nossas campanhas de divulgação.']
    },
    sempre: 'Sempre ligados',
    rejeitarTudo: 'Rejeitar não necessários', salvar: 'Salvar escolhas', fechar: 'Fechar'
  };

  function ler() {
    var m = document.cookie.match(/(?:^|;\s*){{prefixo_js}}_consentimento=([^;]+)/);
    if (!m) return null;
    var p = {};
    try {
      decodeURIComponent(m[1]).split('&').forEach(function (par) {
        var i = par.indexOf('=');
        if (i > 0) p[par.slice(0, i)] = par.slice(i + 1);
      });
    } catch (e) { return null; }
    if (p.v !== VERSAO) return null;
    return { estatistica: p.e === '1', marketing: p.m === '1', em: parseInt(p.t, 10) || 0 };
  }

  function gravar(c) {
    var valor = 'v=' + VERSAO + '&e=' + (c.estatistica ? 1 : 0) + '&m=' + (c.marketing ? 1 : 0) + '&t=' + Math.floor(Date.now() / 1000);
    document.cookie = NOME + '=' + encodeURIComponent(valor) + '; Max-Age=' + VALIDADE_S + '; Path=/; SameSite=Lax' +
      (location.protocol === 'https:' ? '; Secure' : '');
  }

  // Quem tira a permissão depois de dar: os cookies das ferramentas saem do navegador (os de
  // primeira parte, que o próprio site consegue apagar).
  function apagarCookiesDeMedicao(estatistica, marketing) {
    var nomes = document.cookie.split(';').map(function (c) { return c.split('=')[0].trim(); });
    var base = location.hostname.replace(/^www\./i, '');
    nomes.forEach(function (n) {
      var ehEstatistica = n === '_ga' || n.indexOf('_ga_') === 0 || n === '_gid' || n.indexOf('_gat') === 0;
      var ehMarketing = n === '_fbp' || n === '_fbc';
      if ((ehEstatistica && !estatistica) || (ehMarketing && !marketing)) {
        ['', location.hostname, '.' + base].forEach(function (d) {
          document.cookie = n + '=; Max-Age=0; Path=/' + (d ? '; Domain=' + d : '');
        });
      }
    });
  }

  function escolher(c) {
    gravar(c);
    apagarCookiesDeMedicao(c.estatistica, c.marketing);
    if (window.{{prefixo_js}}Medicao && typeof window.{{prefixo_js}}Medicao.aplicar === 'function') window.{{prefixo_js}}Medicao.aplicar(c);
    fecharTudo();
  }

  var CSS = '' +
    '.cvrj-ck,.cvrj-ck-painel{font-family:inherit;color:#111;box-sizing:border-box}' +
    '.cvrj-ck *,.cvrj-ck-painel *{box-sizing:border-box;cursor:auto}' +
    '.cvrj-ck button,.cvrj-ck a,.cvrj-ck-painel button,.cvrj-ck-painel a,.cvrj-ck-painel label{cursor:pointer}' +
    '.cvrj-ck{position:fixed;z-index:2147483000;left:16px;bottom:16px;max-width:520px;width:calc(100% - 32px);background:#fff;border:1px solid #dcdfe4;border-radius:16px;box-shadow:0 12px 40px rgba(0,0,0,.18);padding:20px}' +
    '.cvrj-ck h2,.cvrj-ck-painel h2{margin:0 0 8px;font-size:1.05rem;line-height:1.3;font-weight:800;color:#111}' +
    '.cvrj-ck p,.cvrj-ck-painel p{margin:0 0 12px;font-size:.92rem;line-height:1.55;color:#333}' +
    '.cvrj-ck a,.cvrj-ck-painel a{color:#b00000;font-weight:700}' +
    '.cvrj-ck-botoes{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:4px}' +
    '.cvrj-ck-botoes button{min-height:44px;padding:10px 8px;border:1.5px solid #111;border-radius:10px;background:#fff;color:#111;font:inherit;font-size:.9rem;font-weight:700;line-height:1.2}' +
    '.cvrj-ck-botoes button:hover{background:#f3f4f6}' +
    '.cvrj-ck-botoes button:focus-visible,.cvrj-ck-painel input:focus-visible+span,.cvrj-ck-fechar:focus-visible{outline:3px solid #b00000;outline-offset:2px}' +
    '.cvrj-ck-fundo{position:fixed;inset:0;z-index:2147483001;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;padding:16px}' +
    '.cvrj-ck-painel{position:relative;background:#fff;border-radius:16px;max-width:560px;width:100%;max-height:calc(100vh - 32px);overflow:auto;padding:24px;box-shadow:0 20px 60px rgba(0,0,0,.3)}' +
    '.cvrj-ck-fechar{position:absolute;top:10px;right:10px;width:40px;height:40px;border:0;background:transparent;font-size:1.5rem;line-height:1;color:#111;border-radius:8px}' +
    '.cvrj-ck-cat{border:1px solid #e3e5e8;border-radius:12px;padding:14px 16px;margin:0 0 10px}' +
    '.cvrj-ck-cat label{display:flex;align-items:center;justify-content:space-between;gap:12px;font-weight:800;font-size:.95rem}' +
    '.cvrj-ck-cat p{margin:6px 0 0;font-size:.86rem}' +
    '.cvrj-ck-cat input{position:absolute;opacity:0;width:1px;height:1px}' +
    '.cvrj-ck-cat span.cvrj-ck-chave{flex:0 0 auto;width:44px;height:26px;border-radius:26px;background:#c4c8ce;position:relative;transition:background .15s}' +
    '.cvrj-ck-cat span.cvrj-ck-chave:after{content:"";position:absolute;top:3px;left:3px;width:20px;height:20px;border-radius:50%;background:#fff;transition:transform .15s}' +
    '.cvrj-ck-cat input:checked+span.cvrj-ck-chave{background:#b00000}' +
    '.cvrj-ck-cat input:checked+span.cvrj-ck-chave:after{transform:translateX(18px)}' +
    '.cvrj-ck-cat input:disabled+span.cvrj-ck-chave{opacity:.55}' +
    '.cvrj-ck-sempre{font-size:.78rem;font-weight:700;color:#555;margin-left:auto;margin-right:8px}' +
    '@media (max-width:560px){.cvrj-ck{left:8px;right:8px;bottom:8px;width:auto;padding:16px}.cvrj-ck-botoes{grid-template-columns:1fr}.cvrj-ck-painel{padding:20px 16px}}' +
    '@media print{.cvrj-ck,.cvrj-ck-fundo{display:none!important}}';

  function el(tag, attrs, filhos) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === 'texto') n.textContent = attrs[k];
      else n.setAttribute(k, attrs[k]);
    });
    (filhos || []).forEach(function (f) { if (f) n.appendChild(typeof f === 'string' ? document.createTextNode(f) : f); });
    return n;
  }

  function botao(texto, acao) {
    var b = el('button', { type: 'button', texto: texto });
    b.addEventListener('click', acao);
    return b;
  }

  function estilos() {
    if (document.getElementById('cvrj-ck-css')) return;
    var s = el('style', { id: 'cvrj-ck-css' });
    s.textContent = CSS;
    document.head.appendChild(s);
  }

  var aviso = null, fundo = null, voltarFoco = null;

  function fecharTudo() {
    if (aviso) { aviso.remove(); aviso = null; }
    if (fundo) { fundo.remove(); fundo = null; document.removeEventListener('keydown', teclado, true); }
    if (voltarFoco && document.contains(voltarFoco)) { try { voltarFoco.focus(); } catch (e) { /* segue */ } }
    voltarFoco = null;
  }

  function mostrarAviso() {
    if (aviso || fundo) return;
    estilos();
    aviso = el('section', { class: 'cvrj-ck', role: 'region', 'aria-labelledby': 'cvrj-ck-t1' }, [
      el('h2', { id: 'cvrj-ck-t1', texto: T.titulo }),
      el('p', {}, [T.texto + ' ', el('a', { href: URL_POLITICA, texto: T.politica }), '.']),
      el('div', { class: 'cvrj-ck-botoes' }, [
        botao(T.rejeitar, function () { escolher({ estatistica: false, marketing: false }); }),
        botao(T.personalizar, function () { abrirPainel(); }),
        botao(T.aceitar, function () { escolher({ estatistica: true, marketing: true }); })
      ])
    ]);
    document.body.appendChild(aviso);
  }

  function categoria(chave, ligada, fixa) {
    var c = T.categorias[chave];
    var entrada = el('input', { type: 'checkbox', role: 'switch', id: 'cvrj-ck-' + chave });
    entrada.checked = !!ligada;
    if (fixa) entrada.disabled = true;
    var rotulo = el('label', { for: 'cvrj-ck-' + chave }, [
      el('span', { texto: c[0] }),
      fixa ? el('span', { class: 'cvrj-ck-sempre', texto: T.sempre }) : null,
      entrada,
      el('span', { class: 'cvrj-ck-chave', 'aria-hidden': 'true' })
    ]);
    return el('div', { class: 'cvrj-ck-cat' }, [rotulo, el('p', { texto: c[1] })]);
  }

  // Fechar o painel sem escolher: o foco volta para onde estava, e quem ainda não escolheu volta a ver o aviso.
  function fecharPainel() {
    if (!fundo) return;
    fundo.remove(); fundo = null;
    document.removeEventListener('keydown', teclado, true);
    var foco = voltarFoco;
    voltarFoco = null;
    if (!ler()) mostrarAviso();
    else if (foco && document.contains(foco)) { try { foco.focus(); } catch (e) { /* segue */ } }
  }

  function teclado(e) {
    if (!fundo) return;
    if (e.key === 'Escape') {
      e.preventDefault();
      fecharPainel();
      return;
    }
    if (e.key !== 'Tab') return;
    var focaveis = fundo.querySelectorAll('button, a[href], input:not([disabled])');
    if (!focaveis.length) return;
    var primeiro = focaveis[0], ultimo = focaveis[focaveis.length - 1];
    if (e.shiftKey && document.activeElement === primeiro) { e.preventDefault(); ultimo.focus(); }
    else if (!e.shiftKey && document.activeElement === ultimo) { e.preventDefault(); primeiro.focus(); }
  }

  function abrirPainel() {
    estilos();
    if (aviso) { aviso.remove(); aviso = null; }
    if (fundo) return;
    voltarFoco = document.activeElement;
    var atual = ler() || { estatistica: false, marketing: false };
    var catEstatistica = categoria('estatistica', atual.estatistica);
    var catMarketing = categoria('marketing', atual.marketing);
    var painel = el('div', { class: 'cvrj-ck-painel', role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'cvrj-ck-t2' }, [
      botao('×', fecharPainel),
      el('h2', { id: 'cvrj-ck-t2', texto: T.painel }),
      el('p', {}, [T.intro + ' ', el('a', { href: URL_POLITICA, texto: T.politica }), '.']),
      categoria('necessarios', true, true),
      catEstatistica,
      catMarketing,
      el('div', { class: 'cvrj-ck-botoes' }, [
        botao(T.rejeitarTudo, function () { escolher({ estatistica: false, marketing: false }); }),
        botao(T.salvar, function () {
          escolher({
            estatistica: catEstatistica.querySelector('input').checked,
            marketing: catMarketing.querySelector('input').checked
          });
        }),
        botao(T.aceitar, function () { escolher({ estatistica: true, marketing: true }); })
      ])
    ]);
    var fechar = painel.firstChild;
    fechar.className = 'cvrj-ck-fechar';
    fechar.setAttribute('aria-label', T.fechar);
    fundo = el('div', { class: 'cvrj-ck-fundo' }, [painel]);
    fundo.addEventListener('click', function (e) { if (e.target === fundo) fecharPainel(); });
    document.body.appendChild(fundo);
    document.addEventListener('keydown', teclado, true);
    var primeiraChave = painel.querySelector('input:not([disabled])');
    if (primeiraChave) primeiraChave.focus();
  }

  // "Preferências de cookies": qualquer elemento com data-cookies abre as categorias.
  document.addEventListener('click', function (e) {
    var alvo = e.target && e.target.closest ? e.target.closest('[data-cookies]') : null;
    if (!alvo) return;
    e.preventDefault();
    abrirPainel();
  });

  window.{{prefixo_js}}Consentimento = { ler: ler, abrir: abrirPainel };

  function iniciar() {
    if (!ler()) mostrarAviso();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
