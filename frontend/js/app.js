(function () {
  const API = localStorage.getItem('reviver-api') || 'http://127.0.0.1:5000';
  const USER_KEY = 'reviver-user-id';
  const CHAT_KEY = 'reviver-chat-id';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  const userId = () => localStorage.getItem(USER_KEY);
  const headers = () => ({
    'Content-Type': 'application/json',
    ...(userId() ? { 'X-Usuario-ID': userId() } : {})
  });

  async function api(path, options = {}) {
    const response = await fetch(API + path, {
      ...options,
      headers: { ...headers(), ...(options.headers || {}) }
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.erro || data.detail || 'Erro na API.');
    return data;
  }

  function showError(message) { alert(message); }

  // Cadastro
  const cadastro = $('#cadastroForm');
  if (cadastro) {
    cadastro.addEventListener('submit', async (e) => {
      e.preventDefault();
      const nome = $('#cadNome').value.trim();
      const email = $('#cadEmail').value.trim();
      const senha = $('#cadSenha').value;
      const confirm = $('#cadConfirm').value;
      if (senha !== confirm) return showError('As senhas não conferem.');
      try {
        const data = await api('/api/usuarios', {
          method: 'POST',
          body: JSON.stringify({ nome_exibicao: nome, email, senha })
        });
        localStorage.setItem(USER_KEY, data.usuario.id);
        location.href = 'informacoes.html';
      } catch (err) { showError(err.message); }
    });
  }

  // Login
  const login = $('#loginForm');
  if (login) {
    login.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        const data = await api('/api/login', {
          method: 'POST',
          body: JSON.stringify({ email: $('#loginEmail').value.trim(), senha: $('#loginSenha').value })
        });
        localStorage.setItem(USER_KEY, data.usuario.id);
        location.href = 'home.html';
      } catch (err) { showError(err.message); }
    });
  }

  // Perfil / meus dados
  const profileForm = $('#profileForm');
  async function carregarPerfil() {
    if (!userId()) return;
    try {
      const p = await api('/api/perfis/' + userId());
      if ($('#nome')) $('#nome').value = p.nome_exibicao || '';
      if ($('#idade') && p.ano_nascimento) $('#idade').value = new Date().getFullYear() - p.ano_nascimento;
      if ($('#cidade')) $('#cidade').value = p.cidade || '';
      if ($('#estado')) $('#estado').value = p.estado || '';
      const values = p.substancias_usadas || [];
      $$('#droga option').forEach(o => o.selected = values.includes(o.value || o.textContent));
      if ($('#situacao')) $('#situacao').value = p.estagio_recuperacao || '';
    } catch (err) { console.warn(err.message); }
  }
  if (profileForm) {
    carregarPerfil();
    profileForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!userId()) return location.href = 'login.html';
      const select = $('#droga');
      const substancias = select ? [...select.selectedOptions].map(o => o.value || o.textContent) : [];
      try {
        await api('/api/perfis', {
          method: 'POST',
          body: JSON.stringify({
            usuario_id: Number(userId()),
            nome_exibicao: $('#nome')?.value.trim(),
            idade: $('#idade')?.value,
            cidade: $('#cidade')?.value.trim(),
            estado: $('#estado')?.value.trim().toUpperCase(),
            substancias_usadas: substancias,
            estagio_recuperacao: $('#situacao')?.value || null
          })
        });
        location.href = 'home.html';
      } catch (err) { showError(err.message); }
    });
  }

  // Nome na home
  async function preencherNome() {
    if (!userId()) return;
    try {
      const p = await api('/api/perfis/' + userId());
      $$('.js-name').forEach(el => el.textContent = p.nome_exibicao || 'Você');
    } catch (_) {}
  }
  preencherNome();

  // Chat
  const chatForm = $('#chatForm');
  const messages = $('#messages');
  async function iniciarChat() {
    if (!userId()) return location.href = 'login.html';
    let id = localStorage.getItem(CHAT_KEY);
    if (id) {
      try { await carregarMensagens(id); return id; } catch (_) { localStorage.removeItem(CHAT_KEY); }
    }
    const chat = await api('/api/chats', { method: 'POST', body: JSON.stringify({}) });
    localStorage.setItem(CHAT_KEY, chat.id);
    return chat.id;
  }
  async function carregarMensagens(id) {
    const lista = await api('/api/chats/' + id + '/mensagens');
    if (!messages) return;
    messages.innerHTML = '';
    lista.forEach(m => addMessage(m.conteudo, m.remetente === 'usuario' ? 'user' : 'bot'));
  }
  function addMessage(text, role) {
    if (!messages) return;
    const div = document.createElement('div');
    div.className = 'message ' + role;
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }
  if (chatForm && messages) {
    iniciarChat().catch(err => showError(err.message));
    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = $('#chatInput');
      const text = input.value.trim();
      if (!text) return;
      input.value = '';
      addMessage(text, 'user');
      try {
        const id = localStorage.getItem(CHAT_KEY) || await iniciarChat();
        const data = await api('/api/chats/' + id + '/mensagens', {
          method: 'POST', body: JSON.stringify({ conteudo: text })
        });
        addMessage(data.assistente.conteudo, 'bot');
      } catch (err) { addMessage('Não consegui conectar ao servidor. Verifique se o Flask está rodando.', 'bot'); }
    });
  }

  // Mapa / serviços
  const mapList = $('.list');
  async function carregarServicos() {
    if (!mapList) return;
    try {
      const servicos = await api('/api/servicos');
      mapList.innerHTML = '';
      if (!servicos.length) {
        mapList.innerHTML = '<p>Nenhum serviço cadastrado no banco.</p>';
        return;
      }
      servicos.forEach(s => {
        const card = document.createElement('div');
        card.className = 'list-card service-item';
        card.innerHTML = '<span class="round-icon">⌖</span><div class="grow"><h3></h3><p></p></div><span class="chevron">›</span>';
        $('.grow h3', card).textContent = s.nome;
        $('.grow p', card).textContent = [s.descricao, s.endereco, s.cidade, s.estado].filter(Boolean).join(' • ');
        mapList.appendChild(card);
      });
    } catch (err) {
      mapList.innerHTML = '<p>Não foi possível carregar os serviços. Verifique o backend.</p>';
    }
  }
  carregarServicos();

  const search = $('#mapSearch');
  if (search) search.addEventListener('input', () => {
    const q = search.value.toLowerCase();
    $$('.service-item').forEach(item => item.style.display = item.textContent.toLowerCase().includes(q) ? 'flex' : 'none');
  });

  // Logout / voltar
  $$('.js-logout').forEach(b => b.addEventListener('click', () => {
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(CHAT_KEY);
    location.href = '../index.html';
  }));
  $$('.js-back').forEach(b => b.addEventListener('click', e => { e.preventDefault(); history.back(); }));

  // Datas do cadastro
  const now = new Date().toLocaleString('pt-BR');
  if ($('#createdAt')) $('#createdAt').value = now;
  if ($('#updatedAt')) $('#updatedAt').value = now;
})();
