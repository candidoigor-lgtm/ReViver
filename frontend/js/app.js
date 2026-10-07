/* =========================================================
   ReViver - app.js
   Cadastro, login, modo anônimo, dados do usuário,
   múltiplas substâncias, conversas e pontos de acolhimento.
   ========================================================= */

const STORAGE_USERS = "reviver_users";
const STORAGE_CURRENT_USER = "reviver_current_user";
const STORAGE_ANONYMOUS = "reviver_anonymous";

function getUsers() {
    try {
        return JSON.parse(localStorage.getItem(STORAGE_USERS)) || [];
    } catch {
        return [];
    }
}

function saveUsers(users) {
    localStorage.setItem(STORAGE_USERS, JSON.stringify(users));
}

function getCurrentUser() {
    const id = localStorage.getItem(STORAGE_CURRENT_USER);
    if (!id) return null;
    return getUsers().find(user => user.id === id) || null;
}

function setCurrentUser(id) {
    localStorage.setItem(STORAGE_CURRENT_USER, id);
    localStorage.removeItem(STORAGE_ANONYMOUS);
}

function enterAnonymous() {
    localStorage.removeItem(STORAGE_CURRENT_USER);
    localStorage.setItem(STORAGE_ANONYMOUS, "true");
}

function logout() {
    localStorage.removeItem(STORAGE_CURRENT_USER);
    localStorage.removeItem(STORAGE_ANONYMOUS);
    window.location.href = "../index.html";
}

function nowBR() {
    return new Date().toLocaleString("pt-BR");
}

/* =========================
   CADASTRO
   ========================= */

const cadastroForm = document.getElementById("cadastroForm");

if (cadastroForm) {
    const createdAt = document.getElementById("createdAt");
    const updatedAt = document.getElementById("updatedAt");
    const now = nowBR();

    if (createdAt) createdAt.value = now;
    if (updatedAt) updatedAt.value = now;

    cadastroForm.addEventListener("submit", event => {
        event.preventDefault();

        const nome = document.getElementById("cadNome").value.trim();
        const email = document.getElementById("cadEmail").value.trim().toLowerCase();
        const senha = document.getElementById("cadSenha").value;
        const confirm = document.getElementById("cadConfirm").value;

        if (!nome || !email || !senha) {
            alert("Preencha nome, email e senha.");
            return;
        }

        if (senha !== confirm) {
            alert("As senhas não são iguais.");
            return;
        }

        const users = getUsers();

        if (users.some(user => user.email.toLowerCase() === email)) {
            alert("Já existe uma conta cadastrada com esse email.");
            return;
        }

        const user = {
            id: "user_" + Date.now(),
            nome,
            email,
            senha,
            idade: "",
            drogas: [],
            situacao: "",
            createdAt: createdAt?.value || now,
            updatedAt: updatedAt?.value || now,
            chats: []
        };

        users.push(user);
        saveUsers(users);
        setCurrentUser(user.id);

        alert("Cadastro realizado com sucesso!");
        window.location.href = "home.html";
    });
}

/* =========================
   LOGIN
   ========================= */

const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", event => {
        event.preventDefault();

        const email = document.getElementById("loginEmail").value.trim().toLowerCase();
        const senha = document.getElementById("loginSenha").value;

        const user = getUsers().find(
            item => item.email.toLowerCase() === email && item.senha === senha
        );

        if (!user) {
            alert("Email ou senha incorretos.");
            return;
        }

        setCurrentUser(user.id);
        window.location.href = "home.html";
    });
}

const anonymousButton = document.getElementById("anonymousButton");

if (anonymousButton) {
    anonymousButton.addEventListener("click", () => {
        enterAnonymous();
        window.location.href = "home.html";
    });
}

/* =========================
   NOME DO USUÁRIO
   ========================= */

const currentUser = getCurrentUser();

document.querySelectorAll("[data-user-name]").forEach(element => {
    element.textContent = currentUser ? currentUser.nome : "Visitante";
});

/* =========================
   SAIR
   ========================= */

document.querySelectorAll('[data-action="logout"]').forEach(button => {
    button.addEventListener("click", event => {
        event.preventDefault();
        logout();
    });
});

/* =========================
   MEUS DADOS
   ========================= */

const profileForm = document.getElementById("profileForm");

/* Select múltiplo com aparência semelhante ao select original */
const substanceSelector = document.getElementById("substanceSelector");
const substanceButton = document.getElementById("substanceButton");
const substanceOptions = document.getElementById("substanceOptions");
const substanceSelectedText = document.getElementById("substanceSelectedText");

function updateSubstanceLabel() {
    if (!substanceOptions || !substanceSelectedText) return;
    const selected = [...substanceOptions.querySelectorAll('input[name="droga"]:checked')].map(input => input.value);
    substanceSelectedText.textContent = selected.length ? selected.join(", ") : "Selecione";
}

if (substanceButton && substanceSelector) {
    substanceButton.addEventListener("click", event => {
        event.stopPropagation();
        const open = substanceSelector.classList.toggle("open");
        substanceButton.setAttribute("aria-expanded", open ? "true" : "false");
    });

    document.addEventListener("click", event => {
        if (!substanceSelector.contains(event.target)) {
            substanceSelector.classList.remove("open");
            substanceButton.setAttribute("aria-expanded", "false");
        }
    });

    substanceOptions?.addEventListener("change", updateSubstanceLabel);
    updateSubstanceLabel();
}

if (profileForm) {
    const user = getCurrentUser();

    if (!user) {
        alert(
            "Você está no modo anônimo. Para salvar e modificar seus dados, entre em uma conta ou crie uma conta."
        );
    } else {
        const nome = document.getElementById("nome");
        const idade = document.getElementById("idade");
        const situacao = document.getElementById("situacao");

        const substanceInputs = [
            ...document.querySelectorAll('input[name="droga"]')
        ];

        nome.value = user.nome || "";
        idade.value = user.idade || "";
        situacao.value = user.situacao || "";

        const drogasSalvas = Array.isArray(user.drogas)
            ? user.drogas
            : [];

        substanceInputs.forEach(input => {
            input.checked = drogasSalvas.includes(input.value);
        });
        updateSubstanceLabel();

        profileForm.addEventListener("submit", event => {
            event.preventDefault();

            const users = getUsers();
            const index = users.findIndex(item => item.id === user.id);

            if (index === -1) {
                alert("Não foi possível encontrar sua conta.");
                return;
            }

            const drogasSelecionadas = substanceInputs
                .filter(input => input.checked)
                .map(input => input.value);

            users[index].nome = nome.value.trim();
            users[index].idade = idade.value;
            users[index].drogas = drogasSelecionadas;
            users[index].situacao = situacao.value.trim();
            users[index].updatedAt = nowBR();

            saveUsers(users);

            alert("Seus dados foram atualizados com sucesso!");
        });
    }
}

/* =========================
   CHATBOT
   ========================= */

const messagesContainer = document.getElementById("messages");
const chatForm = document.getElementById("chatForm");

let currentChat = null;

function getUserChats() {
    const user = getCurrentUser();
    return user && Array.isArray(user.chats) ? user.chats : [];
}

function saveUserChats(chats) {
    const user = getCurrentUser();
    if (!user) return;

    const users = getUsers();
    const index = users.findIndex(item => item.id === user.id);

    if (index === -1) return;

    users[index].chats = chats;
    users[index].updatedAt = nowBR();
    saveUsers(users);
}

function createChat() {
    return {
        id: "chat_" + Date.now(),
        title: "Nova conversa",
        createdAt: nowBR(),
        messages: []
    };
}

function addMessage(text, type) {
    if (!messagesContainer) return;

    const message = document.createElement("div");
    message.className = "message " + type;
    message.textContent = text;

    messagesContainer.appendChild(message);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function saveChatMessage(sender, text) {
    if (!getCurrentUser() || !currentChat) return;

    currentChat.messages.push({
        sender,
        text,
        time: nowBR()
    });

    const chats = getUserChats();
    const index = chats.findIndex(chat => chat.id === currentChat.id);

    if (index === -1) chats.push(currentChat);
    else chats[index] = currentChat;

    saveUserChats(chats);
}

function botResponse(text) {
    const lower = text.toLowerCase();

    if (
        lower.includes("crise") ||
        lower.includes("socorro") ||
        lower.includes("não aguento") ||
        lower.includes("nao aguento")
    ) {
        return "Sinto muito que você esteja passando por esse momento. Se houver perigo imediato, procure um serviço de emergência ou uma pessoa de confiança próxima. Também posso ajudar você a encontrar pontos de acolhimento.";
    }

    if (
        lower.includes("mapa") ||
        lower.includes("acolhimento") ||
        lower.includes("ajuda")
    ) {
        return "Você pode acessar o Mapa pela página inicial para consultar os pontos de acolhimento cadastrados.";
    }

    if (
        lower.includes("droga") ||
        lower.includes("substância") ||
        lower.includes("substancia")
    ) {
        return "Posso fornecer informações gerais sobre substâncias, tratamento e formas de buscar ajuda. Para uma avaliação individual, procure um profissional ou serviço de saúde.";
    }

    return "Entendi. Obrigado por compartilhar isso comigo. Posso conversar com você, explicar informações sobre a plataforma ou ajudar a encontrar recursos de apoio.";
}

if (chatForm && messagesContainer) {
    const chats = getUserChats();

    currentChat = chats.length
        ? chats[chats.length - 1]
        : createChat();

    if (currentChat.messages?.length) {
        currentChat.messages.forEach(message => {
            addMessage(
                message.text,
                message.sender === "user" ? "user" : "bot"
            );
        });
    }

    chatForm.addEventListener("submit", event => {
        event.preventDefault();

        const input = document.getElementById("chatInput");
        const text = input.value.trim();

        if (!text) return;

        addMessage(text, "user");
        saveChatMessage("user", text);
        input.value = "";

        setTimeout(() => {
            const response = botResponse(text);
            addMessage(response, "bot");
            saveChatMessage("bot", response);
        }, 400);
    });
}

/* =========================
   MAPA / PONTOS DE ACOLHIMENTO
   ========================= */

const services = [
    {
        nome: "CAPS AD",
        descricao: "Centro de Atenção Psicossocial Álcool e Outras Drogas",
        distancia: "2,3 km"
    },
    {
        nome: "Comunidade Terapêutica",
        descricao: "Apoio e tratamento para dependência de substâncias",
        distancia: "4,1 km"
    },
    {
        nome: "Unidade Básica de Saúde",
        descricao: "Atendimento psicológico e médico",
        distancia: "5,6 km"
    },
    {
        nome: "Centro de Referência",
        descricao: "Atendimento especializado de assistência social",
        distancia: "7,8 km"
    }
];

function showService(service) {
    alert(
        service.nome +
        "\n\n" +
        service.descricao +
        "\n\nDistância aproximada: " +
        service.distancia
    );
}

document.querySelectorAll(".service-item").forEach((item, index) => {
    const service = services[index];
    if (!service) return;

    item.style.cursor = "pointer";
    item.setAttribute("role", "button");
    item.setAttribute("tabindex", "0");

    item.addEventListener("click", () => showService(service));

    item.addEventListener("keydown", event => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            showService(service);
        }
    });
});

/*
   Os quatro primeiros pins representam os quatro pontos
   listados ao lado do mapa.
*/
document.querySelectorAll(".pin").forEach((pin, index) => {
    const service = services[index % services.length];

    pin.style.cursor = "pointer";
    pin.setAttribute("title", service.nome);

    pin.addEventListener("click", event => {
        event.stopPropagation();
        showService(service);
    });
});

/* =========================
   BUSCA NO MAPA
   ========================= */

const mapSearch = document.getElementById("mapSearch");

if (mapSearch) {
    mapSearch.addEventListener("input", () => {
        const search = mapSearch.value.toLowerCase().trim();

        document.querySelectorAll(".service-item").forEach((item, index) => {
            const service = services[index];
            if (!service) return;

            const content = (
                service.nome + " " + service.descricao
            ).toLowerCase();

            item.style.display =
                !search || content.includes(search)
                    ? ""
                    : "none";
        });
    });
}

/* =========================
   LOCALIZAÇÃO
   ========================= */

const locationButton = document.querySelector(".searchbar button");

if (locationButton) {
    locationButton.addEventListener("click", () => {
        if (!navigator.geolocation) {
            alert("Seu navegador não oferece suporte à localização.");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            position => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                if (mapSearch) {
                    mapSearch.value =
                        `${lat.toFixed(5)}, ${lon.toFixed(5)}`;
                }

                alert(
                    "Sua localização foi identificada.\n\n" +
                    `Latitude: ${lat.toFixed(5)}\n` +
                    `Longitude: ${lon.toFixed(5)}\n\n` +
                    "Os pontos de acolhimento cadastrados continuam disponíveis na lista ao lado."
                );
            },
            () => {
                alert(
                    "Não foi possível obter sua localização. " +
                    "Verifique a permissão de localização do navegador."
                );
            }
        );
    });
}

/* =========================
   VOLTAR
   ========================= */

document.querySelectorAll(".js-back").forEach(button => {
    button.addEventListener("click", event => {
        event.preventDefault();

        if (window.history.length > 1) {
            window.history.back();
        } else {
            window.location.href = "home.html";
        }
    });
});
