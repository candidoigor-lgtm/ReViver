(function(){
  const storageKey='reviver-profile';
  const chatKey='reviver-chat';
  const profile=JSON.parse(localStorage.getItem(storageKey)||'null');
  const $=(s,r=document)=>r.querySelector(s);
  const $$=(s,r=document)=>[...r.querySelectorAll(s)];
  function fillProfile(){
    if(!profile) return;
    $$('.js-name').forEach(e=>e.textContent=profile.nome||'Você');
    $$('.js-age').forEach(e=>e.textContent=profile.idade||'—');
    const drug=$('.js-drug'); if(drug) drug.value=profile.droga||'';
    const situation=$('.js-situation'); if(situation) situation.value=profile.situacao||'';
  }
  fillProfile();
  const profileForm=$('#profileForm');
  if(profileForm){
    profileForm.addEventListener('submit',e=>{e.preventDefault();
      const data={nome:$('#nome')?.value.trim(),idade:$('#idade')?.value.trim(),droga:$('#droga')?.value,situacao:$('#situacao')?.value.trim()};
      localStorage.setItem(storageKey,JSON.stringify(data)); location.href='home.html';
    });
  }
  const cadastro=$('#cadastroForm');
  if(cadastro){cadastro.addEventListener('submit',e=>{e.preventDefault();
    const nome=$('#cadNome').value.trim();
    if(!nome){alert('Digite seu nome.');return;}
    const data={nome,idade:'',droga:'',situacao:''};localStorage.setItem(storageKey,JSON.stringify(data));location.href='informacoes.html';
  });}
  const anonymous=$('.js-anonymous');
  if(anonymous) anonymous.addEventListener('click',()=>{localStorage.removeItem(storageKey);location.href='home.html'});
  const chatForm=$('#chatForm'), messages=$('#messages');
  if(chatForm&&messages){
    const saved=JSON.parse(localStorage.getItem(chatKey)||'[]');
    if(saved.length){messages.innerHTML='';saved.forEach(m=>addMessage(m.text,m.role,false));}
    function addMessage(text,role,save=true){const div=document.createElement('div');div.className='message '+role;div.textContent=text;messages.appendChild(div);messages.scrollTop=messages.scrollHeight;if(save){saved.push({text,role});localStorage.setItem(chatKey,JSON.stringify(saved.slice(-30)));}}
    chatForm.addEventListener('submit',e=>{e.preventDefault();const input=$('#chatInput');const text=input.value.trim();if(!text)return;addMessage(text,'user');input.value='';setTimeout(()=>{let reply='Posso ajudar com informações gerais, acompanhar seus dados e mostrar serviços de apoio. Se precisar de atendimento, procure um profissional de saúde ou serviço especializado.';const low=text.toLowerCase();if(low.includes('mapa')||low.includes('clínica')||low.includes('caps')) reply='Posso abrir o mapa e mostrar pontos de acolhimento cadastrados. Clique em “Mapa” no menu inicial.';else if(low.includes('parar')||low.includes('ajuda')) reply='Buscar ajuda é um passo importante. Posso mostrar serviços de apoio e informações para você conversar com um profissional.';addMessage(reply,'bot');},450);});
  }
  const search=$('#mapSearch');
  if(search){search.addEventListener('input',()=>{const q=search.value.toLowerCase();$$('.service-item').forEach(item=>item.style.display=item.textContent.toLowerCase().includes(q)?'flex':'none');});}
  $$('.js-back').forEach(b=>b.addEventListener('click',()=>history.back()));
})();
