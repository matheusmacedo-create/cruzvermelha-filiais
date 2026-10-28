// Menu do celular: abre e fecha a lista de links.
(function () {
  var botao = document.querySelector('.menu-botao');
  var menu = document.getElementById('menu');
  if (!botao || !menu) return;
  botao.addEventListener('click', function () {
    var aberto = menu.classList.toggle('aberto');
    botao.setAttribute('aria-expanded', aberto ? 'true' : 'false');
  });
})();
