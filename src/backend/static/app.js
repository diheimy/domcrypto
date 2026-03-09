const ws = new WebSocket("ws://" + window.location.host + "/ws/opportunities");
const tableBody = document.getElementById("tableBody");
const minSpreadInput = document.getElementById("minSpread");
//const updateIntervalInput = document.getElementById("updateInterval");
const oppCount = document.getElementById("opp-count");
const globalSearch = document.getElementById("globalSearch");
const pauseBtn = document.getElementById("pauseBtn");
const lastUpdateEl = document.getElementById("last-update");

let latestData = []; 
let isPaused = false;
let favorites = JSON.parse(localStorage.getItem('neoarb_favorites') || '[]');
let activeSpot = ['mexc', 'gate', 'bitget', 'bingx'];
let activeFut = ['mexc_futures', 'gate_futures', 'bitget_futures', 'bingx_futures'];

window.onload = function() {
    const noteArea = document.getElementById("notepadArea");
    if(noteArea) noteArea.value = localStorage.getItem('neoarb_notes') || "";
    updatePauseButton();
};

// --- CONTROLES DE INTERFACE (Menus, Pausa, Filtros) ---

window.toggleExchange = function(el, type, key) {
    let list = (type === 'spot') ? activeSpot : activeFut;
    if (list.includes(key)) { list = list.filter(k => k !== key); el.classList.remove('active'); } 
    else { list.push(key); el.classList.add('active'); }
    if (type === 'spot') activeSpot = list; else activeFut = list;
    renderTable();
}

function updatePauseButton() {
    if (!pauseBtn) return;
    const statusDiv = document.getElementById("system-status");
    if (isPaused) {
        pauseBtn.innerHTML = '<i class="fa-solid fa-play"></i> Retomar';
        pauseBtn.classList.add("paused");
        if(statusDiv) statusDiv.innerHTML = '<span style="color:#eab308">● Pausado</span>';
    } else {
        pauseBtn.innerHTML = '<i class="fa-solid fa-power-off"></i> Executando';
        pauseBtn.classList.remove("paused");
        if(statusDiv) statusDiv.innerHTML = '<span style="color:#0ecb81">● Online</span>';
    }
}

function togglePause() { isPaused = !isPaused; updatePauseButton(); if (!isPaused) renderTable(); }

function resetFilters() {
    minSpreadInput.value = 0.5;
    //updateIntervalInput.value = 0;
    //globalSearch.value = "";
    //document.getElementById("presetSelect").value = "default";
    //activeSpot = ['mexc', 'gate', 'bitget', 'bingx'];
    //activeFut = ['mexc_futures', 'gate_futures', 'bitget_futures', 'bingx_futures'];
    //document.querySelectorAll('.exch-btn').forEach(btn => btn.classList.add('active'));
    //renderTable();
}

function applyPreset(preset) {
    //switch(preset) {
    //    case 'safe': minSpreadInput.value = 1.0; updateIntervalInput.value = 30000; break;
    //    case 'aggressive': minSpreadInput.value = 0.1; updateIntervalInput.value = 0; break;
    //    default: minSpreadInput.value = 0.5; updateIntervalInput.value = 0;
    }
    renderTable();
}

// --- UTILITÁRIOS (Calculadora e Notas) ---
function calculateProfit() {
    const amount = parseFloat(document.getElementById("calcAmount").value) || 0;
    const entry = parseFloat(document.getElementById("calcEntry").value) || 0;
    const exit = parseFloat(document.getElementById("calcExit").value) || 0;
    if (amount > 0 && entry > 0 && exit > 0) {
        const coins = amount / entry;
        const totalExit = coins * exit;
        const profit = totalExit - amount;
        const percent = ((exit - entry) / entry) * 100;
        document.getElementById("calcResult").innerHTML = `Lucro: $${profit.toFixed(2)} <br> <span style="font-size:12px">(${percent.toFixed(2)}%)</span>`;
    }
}
function saveNotes() { localStorage.setItem('neoarb_notes', document.getElementById("notepadArea").value); alert("Notas salvas!"); }

// --- AJUDANTES VISUAIS (Links, Logos, Badges) ---

function getTradeUrl(exchange, symbol) {
    const base = symbol.replace("USDT", "");
    if (exchange === 'mexc') return `https://www.mexc.com/exchange/${base}_USDT`;
    if (exchange === 'mexc_futures') return `https://futures.mexc.com/exchange/${base}_USDT`;
    if (exchange === 'gate') return `https://www.gate.io/trade/${base}_USDT`;
    if (exchange === 'gate_futures') return `https://www.gate.io/futures_trade/USDT/${base}_USDT`;
    if (exchange === 'bitget') return `https://www.bitget.com/spot/${base}USDT`;
    if (exchange === 'bitget_futures') return `https://www.bitget.com/futures/usdt/${base}USDT`;
    if (exchange === 'bingx') return `https://bingx.com/en-us/spot/${base}-USDT/`;
    if (exchange === 'bingx_futures') return `https://bingx.com/en-us/futures/forward/${base}-USDT/`;
    return '#';
}

function openLiteWindow(url) { window.open(url, '_blank', 'width=1300,height=900,menubar=no,toolbar=no,scrollbars=yes'); }

function formatVolume(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
    return num.toFixed(1);
}

function createLiquidityBadge(value) {
    if (!value || value <= 0) return `<div style="margin-top: 6px; height: 18px;"></div>`;
    return `<div style="margin-top: 6px;">
             <span style="background: rgba(16, 185, 129, 0.15); color: #10b981; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700;">
                ${formatVolume(value)} USDT
             </span>
           </div>`;
}

function getExchangeLogo(key) {
    if(key.includes('mexc')) return 'https://assets.coincap.io/assets/icons/mxc@2x.png';
    if(key.includes('gate')) return 'https://assets.coincap.io/assets/icons/gate@2x.png';
    if(key.includes('bitget')) return 'https://s2.coinmarketcap.com/static/img/exchanges/64x64/521.png';
    if(key.includes('bingx')) return 'https://s2.coinmarketcap.com/static/img/exchanges/64x64/1247.png';
    return '';
}
function getExchangeName(key) { return key.split('_')[0].toUpperCase(); }

window.handleImageError = function(img, symbol) {
    const symLower = symbol.toLowerCase();
    const symUpper = symbol.toUpperCase();
    if (!img.dataset.triedBackup1) { img.dataset.triedBackup1 = "true"; img.src = `https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/${symLower}.png`; } 
    else if (!img.dataset.triedBackup2) { img.dataset.triedBackup2 = "true"; img.src = `https://bin.bnbstatic.com/static/assets/logos/${symUpper}.png`; } 
    else { img.style.display = 'none'; }
}

// --- RENDERIZAÇÃO DA TABELA ---
function renderTable() {
    if (!tableBody) return;
    const minSpread = parseFloat(minSpreadInput.value) || 0;
    const term = globalSearch.value.toUpperCase();

    let filtered = latestData.filter(op => {
        const spreadOk = op.spread >= minSpread;
        const searchOk = op.symbol.includes(term);
        const spotOk = activeSpot.includes(op.buy_exchange);
        const futOk = activeFut.includes(op.sell_exchange);
        return spreadOk && searchOk && spotOk && futOk;
    });

    filtered.sort((a,b) => {
        const aFav = favorites.includes(a.symbol);
        const bFav = favorites.includes(b.symbol);
        if (aFav && !bFav) return -1;
        if (!aFav && bFav) return 1;
        return b.spread - a.spread;
    });

    if(oppCount) oppCount.textContent = filtered.length;
    
    tableBody.innerHTML = "";
    
    filtered.forEach(op => {
        try {
            const row = document.createElement("tr");
            const cleanSymbol = op.base_asset || op.symbol;
            const imgUrl = `https://assets.coincap.io/assets/icons/${cleanSymbol.toLowerCase()}@2x.png`;
            const isFav = favorites.includes(op.symbol);
            const starColor = isFav ? "#FCD535" : "#475569";
            const starClass = isFav ? "fa-solid fa-star" : "fa-regular fa-star";
            const exitColor = op.spread_exit > 0 ? "text-green" : "text-red";
            
            // URLs e Badges
            const buyUrl = getTradeUrl(op.buy_exchange, op.symbol);
            const sellUrl = getTradeUrl(op.sell_exchange, op.symbol);
            const maxLongHtml = createLiquidityBadge(op.max_long_usdt);
            const maxShortHtml = createLiquidityBadge(op.max_short_usdt);

            row.innerHTML = `
                <td>
                    <div onclick="toggleFavorite('${op.symbol}')" style="cursor:pointer;text-align:center;padding:10px;">
                        <i class="${starClass}" style="color:${starColor};font-size:16px;"></i>
                    </div>
                </td>
                <td>
                    <div class="coin-cell">
                        <div style="width:32px;height:32px;">
                            <img src="${imgUrl}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;" onerror="handleImageError(this, '${cleanSymbol}')">
                        </div>
                        <div>
                            <strong>${op.symbol}</strong>
                            <div style="font-size:11px;color:#848e9c;">${op.coin_name || cleanSymbol}</div>
                        </div>
                    </div>
                </td>
                
                <td>
                    <a href="#" onclick="openLiteWindow('${buyUrl}'); return false;" style="text-decoration:none;">
                        <div style="display:flex;align-items:center;gap:6px">
                            <img src="${getExchangeLogo(op.buy_exchange)}" style="width:16px;border-radius:50%">
                            <span style="font-size:12px;color:#3b82f6;font-weight:bold">${getExchangeName(op.buy_exchange)} <i class="fa-solid fa-arrow-up-right-from-square" style="font-size:9px"></i></span>
                        </div>
                        <div style="color:#e2e8f0;font-weight:bold;margin-top:2px">$${op.buy_price}</div>
                    </a>
                    ${maxLongHtml}
                </td>
                
                <td>
                    <a href="#" onclick="openLiteWindow('${sellUrl}'); return false;" style="text-decoration:none;">
                        <div style="display:flex;align-items:center;gap:6px">
                            <img src="${getExchangeLogo(op.sell_exchange)}" style="width:16px;border-radius:50%">
                            <span style="font-size:12px;color:#3b82f6;font-weight:bold">${getExchangeName(op.sell_exchange)} <i class="fa-solid fa-arrow-up-right-from-square" style="font-size:9px"></i></span>
                        </div>
                        <div style="color:#e2e8f0;font-weight:bold;margin-top:2px">$${op.sell_price}</div>
                    </a>
                    ${maxShortHtml}
                </td>
                
                <td><span class="profit-badge" style="background:rgba(16,185,129,0.2);color:#10b981;padding:4px 8px;border-radius:4px;font-weight:bold">+${op.spread}%</span></td>
                <td><span class="${exitColor}" style="font-weight:bold">${op.spread_exit}%</span></td>
                <td>${(op.volume/1000).toFixed(0)}k</td>
                <td><span style="color:${op.funding>0?'#10b981':'#ef4444'}">${(op.funding*100).toFixed(4)}%</span></td>
            `;
            tableBody.appendChild(row);
        } catch(e) {}
    });
}

ws.onmessage = (e) => {
    if(isPaused) return;
    try { latestData = JSON.parse(e.data); } catch(err){}
    //const now = Date.now();
    //const delay = parseInt(updateIntervalInput.value);
    //if (delay > 0 && (now - lastUpdate) < delay) return;
    //lastUpdate = now;
    if(lastUpdateEl) lastUpdateEl.innerText = "Atualizado: " + new Date().toLocaleTimeString();
    renderTable();
};

if(minSpreadInput) minSpreadInput.addEventListener('change', renderTable);
if(globalSearch) globalSearch.addEventListener('keyup', renderTable);