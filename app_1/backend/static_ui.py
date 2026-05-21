"""
HTML UI for Rozgar AI (Fallback for environments without Node.js)
"""
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en" class="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Rozgar AI</title>
    <!-- Tailwind -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <!-- Leaflet Map CSS/JS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        brand: { 500: '#008b4b', 600: '#006c3a', 700: '#004d2a' },
                        surface: { 50: '#f8fafc', 100: '#f1f5f9', 200: '#e2e8f0', 800: '#1e293b' }
                    },
                    animation: {
                        'slide-up': 'slideUp 0.3s ease-out forwards',
                        'fade-in': 'fadeIn 0.2s ease-out forwards',
                        'pop-in': 'popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards',
                        'pulse-ring': 'pulseRing 2s cubic-bezier(0.215, 0.61, 0.355, 1) infinite',
                    },
                    keyframes: {
                        slideUp: { '0%': { transform: 'translateY(20px)', opacity: '0' }, '100%': { transform: 'translateY(0)', opacity: '1' } },
                        fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
                        popIn: { '0%': { transform: 'scale(0.8)', opacity: '0' }, '100%': { transform: 'scale(1)', opacity: '1' } },
                        pulseRing: { '0%': { transform: 'scale(0.5)', opacity: '0' }, '50%': { opacity: '0.6' }, '100%': { transform: 'scale(2.5)', opacity: '0' } }
                    }
                }
            }
        }
    </script>
    <style>
        body { background-color: #f1f5f9; font-family: system-ui, -apple-system, sans-serif; -webkit-tap-highlight-color: transparent; margin: 0; transition: filter 0.3s ease, background-color 0.3s ease; }
        
        /* Dark Mode Hack (Invert colors except images/map/backgrounds) */
        html.dark body { filter: invert(0.92) hue-rotate(180deg); background-color: #111; }
        html.dark img, html.dark .leaflet-container, html.dark .bg-cover, html.dark #interactive-map { filter: invert(1) hue-rotate(180deg); }
        
        .app-container { max-width: 480px; margin: 0 auto; background: white; height: 100vh; display: flex; flex-direction: column; position: relative; box-shadow: 0 0 20px rgba(0,0,0,0.1); overflow: hidden; }
        .view-content { flex: 1; overflow-y: auto; padding-bottom: 80px; }
        
        .view-content::-webkit-scrollbar { width: 6px; }
        .view-content::-webkit-scrollbar-track { background: transparent; }
        .view-content::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
        .view-content::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
        
        .bottom-nav { position: absolute; bottom: 0; width: 100%; background: white; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-around; padding: 10px 0 15px 0; z-index: 50; }
        .nav-item { display: flex; flex-direction: column; align-items: center; color: #94a3b8; font-size: 11px; font-weight: 500; cursor: pointer; transition: color 0.2s, transform 0.2s; }
        .nav-item:active { transform: scale(0.9); }
        .nav-item.active { color: #008b4b; }
        .nav-icon { font-size: 20px; margin-bottom: 4px; }
        
        .mic-fab { position: absolute; bottom: 80px; right: 20px; width: 56px; height: 56px; border-radius: 50%; background-color: #008b4b; color: white; display: flex; align-items: center; justify-content: center; font-size: 24px; box-shadow: 0 4px 12px rgba(0,139,75,0.4); z-index: 40; cursor: pointer; transition: transform 0.2s; }
        .mic-fab:active { transform: scale(0.95); }
        
        .hidden-view { display: none !important; }
        
        .overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.5); z-index: 100; display: none; flex-direction: column; justify-content: flex-end; opacity: 0; transition: opacity 0.3s; }
        .overlay.active { display: flex; opacity: 1; }
        .sheet { background: white; border-radius: 24px 24px 0 0; padding: 20px; transform: translateY(100%); transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); max-height: 85vh; display: flex; flex-direction: column; }
        .overlay.active .sheet { transform: translateY(0); }
        
        .popup-modal { position: absolute; inset: 0; background: rgba(0,0,0,0.5); z-index: 110; display: none; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s; }
        .popup-modal.active { display: flex; opacity: 1; }
        .popup-content { background: white; width: 85%; border-radius: 16px; padding: 20px; transform: scale(0.9); transition: transform 0.2s; max-height: 80vh; overflow-y: auto; }
        .popup-modal.active .popup-content { transform: scale(1); }

        .profile-img-container { width: 100px; height: 100px; border-radius: 50%; background: #e2e8f0; margin: 0 auto; position: relative; overflow: hidden; border: 3px solid white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .profile-img { width: 100%; height: 100%; object-fit: cover; }
        .upload-badge { position: absolute; bottom: 0; right: 0; background: #008b4b; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; border: 2px solid white; cursor: pointer; }

        #interactive-map { width: 100%; height: 100%; z-index: 1; }
        
        .my-location-marker { position: relative; width: 16px; height: 16px; background-color: #3b82f6; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 10px rgba(0,0,0,0.3); }
        .my-location-marker::before { content: ''; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 40px; height: 40px; background-color: rgba(59, 130, 246, 0.4); border-radius: 50%; animation: pulseRing 2s cubic-bezier(0.215, 0.61, 0.355, 1) infinite; pointer-events: none; }
        
        .rainbow-text {
            background-image: linear-gradient(to right, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #8b00ff);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
    </style>
</head>
<body>

<div class="app-container">
    
    <!-- HEADER -->
    <div id="main-header" class="px-4 py-3 flex justify-between items-center bg-white border-b border-surface-100 z-10">
        <div class="font-extrabold text-2xl tracking-tight flex items-center gap-2 rainbow-text">
            Rozgar
        </div>
        <div class="flex gap-5 text-surface-500 relative">
            <i class="fa-solid fa-bell text-xl cursor-pointer hover:text-brand-500 transition-colors" onclick="openNotifications()">
                <!-- Red dot for unread -->
                <span id="notif-dot" class="absolute top-0 right-8 w-2 h-2 bg-red-500 rounded-full border border-white"></span>
            </i>
            <i class="fa-solid fa-cog text-xl cursor-pointer hover:text-brand-500 transition-colors" onclick="openModal('Settings')"></i>
        </div>
    </div>

    <!-- ================= VIEWS ================= -->

    <!-- 1. HOME VIEW -->
    <div id="view-home" class="view-content bg-surface-50">
        <!-- Banner -->
        <div class="m-4 rounded-2xl bg-brand-500 text-white p-5 shadow-lg relative overflow-hidden animate-fade-in">
            <div class="relative z-10">
                <h2 class="text-xl font-bold mb-1 shadow-sm">"Sirf Bolo, Kaam Ho Jaye"</h2>
                <p class="text-xs text-brand-100 font-medium">Pakistan's #1 Voice AI Marketplace</p>
            </div>
            <div class="absolute -right-4 -top-2 text-brand-700/40 text-6xl font-arabic font-bold select-none">صرف بولو</div>
        </div>

        <!-- Search Bar -->
        <div class="px-4 mb-6 animate-slide-up" style="animation-delay: 0.1s" onclick="openChat()">
            <div class="bg-white rounded-xl p-3 flex items-center gap-3 border border-surface-200 shadow-sm cursor-text hover:border-brand-500 transition-colors">
                <i class="fa-solid fa-search text-brand-500"></i>
                <div class="text-surface-400 text-sm flex-1">Type in Urdu, Roman Urdu, or English...</div>
            </div>
        </div>

        <!-- Categories -->
        <div class="px-4 mb-6 animate-slide-up" style="animation-delay: 0.2s">
            <div class="flex justify-between items-end mb-3">
                <h3 class="font-bold text-surface-800">Service Categories</h3>
                <span class="text-xs text-brand-500 font-semibold cursor-pointer active:opacity-70" onclick="switchView('map')">View on Map</span>
            </div>
            <div class="flex overflow-x-auto gap-3 pb-2 scrollbar-hide" id="categories-grid">
                <!-- Populated via JS -->
            </div>
        </div>

        <!-- Top Rated -->
        <div class="px-4 pb-4 animate-slide-up" style="animation-delay: 0.3s">
            <h3 class="font-bold text-surface-800 mb-3">Choose Providers (All Budgets)</h3>
            <div class="space-y-3" id="top-providers-list"></div>
        </div>
    </div>

    <!-- 2. MAP VIEW -->
    <div id="view-map" class="view-content hidden-view relative">
        <!-- Top Controls Overlay -->
        <div class="absolute top-4 left-4 right-4 z-[500] flex gap-2">
            <!-- Back Button -->
            <button class="bg-white/90 backdrop-blur rounded-xl shadow-md p-3 flex items-center justify-center text-surface-600 hover:text-brand-500 active:scale-95 transition-all border border-surface-200" onclick="switchView('home')">
                <i class="fa-solid fa-chevron-left"></i>
            </button>
            
            <!-- Search Bar with Search Button -->
            <div class="flex-1 bg-white/90 backdrop-blur rounded-xl shadow-md p-2 flex items-center gap-2 border border-surface-200">
                <input type="text" id="map-search-input" placeholder="Search NUTECH, EME..." class="flex-1 bg-transparent outline-none text-sm font-medium px-2" value="NUTECH, I-12">
                <button class="w-8 h-8 bg-brand-500 text-white rounded-lg flex items-center justify-center active:scale-90 transition-transform" onclick="simulateMapSearch()">
                    <i class="fa-solid fa-search"></i>
                </button>
            </div>
        </div>
        
        <!-- Interactive Map Container -->
        <div id="interactive-map"></div>
        
        <!-- Bottom card for map -->
        <div class="absolute bottom-4 left-4 right-4 bg-white rounded-2xl p-4 shadow-[0_-4px_20px_rgba(0,0,0,0.1)] z-[500] animate-slide-up">
            <h4 class="font-bold text-sm mb-3 flex items-center justify-between">
                <span>Providers nearby</span>
                <span class="bg-brand-100 text-brand-700 px-2 py-0.5 rounded text-xs">Live</span>
            </h4>
            <div class="flex gap-3 overflow-x-auto pb-2 scrollbar-hide" id="map-cards-container">
                <!-- Populated via JS -->
            </div>
        </div>
    </div>

    <!-- 3. HISTORY VIEW -->
    <div id="view-history" class="view-content hidden-view bg-surface-50 flex flex-col h-full">
        <div class="bg-white px-4 pt-4 border-b flex-shrink-0">
            <h2 class="text-xl font-bold mb-4">My Bookings</h2>
            <div class="flex gap-6 border-b" id="history-tabs">
                <div class="pb-3 border-b-2 border-brand-500 font-semibold text-brand-500 text-sm cursor-pointer" onclick="switchHistoryTab('upcoming')">Upcoming <span id="count-upcoming">(0)</span></div>
                <div class="pb-3 text-surface-400 font-medium text-sm cursor-pointer hover:text-surface-600 transition-colors" onclick="switchHistoryTab('completed')">Completed <span id="count-completed">(0)</span></div>
                <div class="pb-3 text-surface-400 font-medium text-sm cursor-pointer hover:text-surface-600 transition-colors" onclick="switchHistoryTab('cancelled')">Cancelled <span id="count-cancelled">(0)</span></div>
            </div>
        </div>
        
        <div class="p-4 flex-1 overflow-y-auto" id="history-list">
            <!-- Rendered via JS -->
        </div>
    </div>

    <!-- 4. PROFILE VIEW -->
    <div id="view-profile" class="view-content hidden-view bg-surface-50">
        <!-- Pakistan Monument Banner -->
        <div class="h-40 relative overflow-hidden bg-cover bg-center shadow-inner" style="background-image: url('https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Pakistan_Monument%2C_Islamabad.jpg/800px-Pakistan_Monument%2C_Islamabad.jpg');">
            <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
        </div>
        <div class="px-4 relative -mt-16 mb-6 text-center animate-fade-in">
            <div class="profile-img-container mb-3 relative border-4 border-white shadow-lg bg-white w-24 h-24 mx-auto">
                <img id="profile-pic" src="https://ui-avatars.com/api/?name=Ahmad+Khan&background=008b4b&color=fff&size=128" class="profile-img rounded-full" alt="Profile">
                <label for="img-upload" class="upload-badge absolute bottom-0 right-0 bg-brand-500 text-white rounded-full p-1.5 cursor-pointer shadow-md hover:bg-brand-600 active:scale-95 transition-all border-2 border-white">
                    <i class="fa-solid fa-camera text-xs"></i>
                </label>
                <input type="file" id="img-upload" class="hidden" accept="image/*" onchange="loadProfilePic(event)">
            </div>
            <h2 class="text-2xl font-extrabold text-surface-800 drop-shadow-sm">Ahmad Khan</h2>
            <p class="text-sm font-medium text-surface-500">+92 300 1234567</p>
        </div>
        
        <div class="bg-white mx-4 rounded-xl shadow-sm border border-surface-100 overflow-hidden mb-6 animate-slide-up">
            <div class="p-4 border-b flex items-center justify-between cursor-pointer hover:bg-surface-50 active:bg-surface-100 transition-colors" onclick="openModal('Saved Addresses')">
                <div class="flex items-center gap-3 text-surface-700">
                    <div class="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center text-blue-500"><i class="fa-solid fa-map-location-dot"></i></div>
                    <span class="font-medium">Saved Addresses</span>
                </div>
                <i class="fa-solid fa-chevron-right text-surface-300 text-sm"></i>
            </div>
            <div class="p-4 border-b flex items-center justify-between cursor-pointer hover:bg-surface-50 active:bg-surface-100 transition-colors" onclick="openModal('Payment Methods')">
                <div class="flex items-center gap-3 text-surface-700">
                    <div class="w-8 h-8 rounded-full bg-green-50 flex items-center justify-center text-green-500"><i class="fa-solid fa-credit-card"></i></div>
                    <span class="font-medium">Payment Methods</span>
                </div>
                <i class="fa-solid fa-chevron-right text-surface-300 text-sm"></i>
            </div>
            <div class="p-4 flex items-center justify-between cursor-pointer hover:bg-surface-50 active:bg-surface-100 transition-colors" onclick="openModal('Help & Support')">
                <div class="flex items-center gap-3 text-surface-700">
                    <div class="w-8 h-8 rounded-full bg-purple-50 flex items-center justify-center text-purple-500"><i class="fa-solid fa-circle-question"></i></div>
                    <span class="font-medium">Help & Support</span>
                </div>
                <i class="fa-solid fa-chevron-right text-surface-300 text-sm"></i>
            </div>
        </div>
        
        <button class="mx-4 w-[calc(100%-32px)] py-3 text-red-500 font-bold bg-white border border-red-200 shadow-sm rounded-xl active:scale-95 transition-transform" onclick="alert('Logged out successfully.')">Log Out</button>
    </div>

    <!-- Floating Mic Button -->
    <div id="fab" class="mic-fab" onclick="openChat()">
        <i class="fa-solid fa-microphone"></i>
    </div>

    <!-- BOTTOM NAVIGATION -->
    <div class="bottom-nav shadow-[0_-4px_10px_rgba(0,0,0,0.05)]">
        <div class="nav-item active" onclick="switchView('home', this)">
            <i class="fa-solid fa-house nav-icon"></i>
            <span>Home</span>
        </div>
        <div class="nav-item" onclick="switchView('map', this)">
            <i class="fa-solid fa-map-location-dot nav-icon"></i>
            <span>Map</span>
        </div>
        <div class="nav-item" onclick="switchView('history', this)">
            <i class="fa-solid fa-clock-rotate-left nav-icon"></i>
            <span>History</span>
        </div>
        <div class="nav-item" onclick="switchView('profile', this)">
            <i class="fa-solid fa-user nav-icon"></i>
            <span>Profile</span>
        </div>
    </div>
    
    <!-- CHAT / VOICE OVERLAY -->
    <div id="chat-overlay" class="overlay">
        <div class="sheet">
            <div class="flex justify-between items-center mb-4">
                <h3 class="font-bold text-lg flex items-center gap-2 text-surface-800"><i class="fa-solid fa-robot text-brand-500"></i> AI Orchestrator</h3>
                <button onclick="closeChat()" class="w-8 h-8 bg-surface-100 rounded-full flex items-center justify-center text-surface-500 hover:bg-surface-200"><i class="fa-solid fa-times"></i></button>
            </div>
            
            <div id="chat-messages" class="flex-1 overflow-y-auto mb-4 space-y-4 pr-2">
                <div class="flex gap-3">
                    <div class="w-8 h-8 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center flex-shrink-0"><i class="fa-solid fa-bolt"></i></div>
                    <div class="bg-surface-100 rounded-2xl rounded-tl-none p-3 text-sm text-surface-800">
                        Hello! I am Rozgar AI. Speak or type your request:<br>
                        <em class="text-xs text-surface-500 mt-1 block">e.g. "Mujhe kal subah AC technician chahiye"</em>
                    </div>
                </div>
            </div>
            
            <div class="border-t pt-3 flex gap-2 items-center relative">
                <input type="text" id="chat-input" placeholder="Type or tap microphone..." class="flex-1 bg-surface-100 border border-surface-200 focus:border-brand-500 rounded-full px-4 py-3 outline-none text-sm transition-colors">
                <button id="chat-send" class="w-11 h-11 rounded-full bg-brand-500 text-white flex items-center justify-center flex-shrink-0 shadow-md active:scale-90 transition-transform">
                    <i class="fa-solid fa-paper-plane"></i>
                </button>
            </div>
        </div>
    </div>

    <!-- GENERIC POPUP MODAL -->
    <div id="generic-modal" class="popup-modal" onclick="if(event.target===this) closeModal()">
        <div class="popup-content shadow-2xl flex flex-col max-h-[80vh]">
            <div class="flex justify-between items-center mb-4 border-b pb-2 flex-shrink-0">
                <h3 class="font-bold text-lg text-surface-800" id="modal-title">Title</h3>
                <button onclick="closeModal()" class="text-surface-400 hover:text-surface-600"><i class="fa-solid fa-times"></i></button>
            </div>
            <div id="modal-body" class="text-sm text-surface-600 space-y-3 overflow-y-auto pr-2 pb-2">
                <!-- Content injected here -->
            </div>
        </div>
    </div>

</div>

<script>
    // --- State Management ---
    let myBookings = [
        { id: 'b1', service: 'Plumbing Fix', provider: 'Hassan Plumbing', status: 'completed', price: 'PKR 800', date: '12 May 2026', time: '2:00 PM', location: 'F-10, Islamabad' },
        { id: 'b2', service: 'Electrician', provider: 'PowerLine Pro', status: 'cancelled', price: 'PKR 1200', date: '14 May 2026', time: '10:00 AM', location: 'G-13, Islamabad' },
        { id: 'b3', service: 'AC Technician', provider: 'CoolBreeze HVAC', status: 'upcoming', price: 'PKR 1500', date: 'Tomorrow', time: '11:00 AM', location: 'G-13, Islamabad', eta: '45 mins' }
    ];
    let currentHistoryTab = 'upcoming';
    let mapInitialized = false;
    let leafletMap = null;
    let tempPendingBooking = null; // Store booking before confirming

    // --- Navigation ---
    function switchView(viewName, element = null) {
        document.querySelectorAll('.view-content').forEach(el => el.classList.add('hidden-view'));
        document.getElementById(`view-${viewName}`).classList.remove('hidden-view');
        
        if (element) {
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            element.classList.add('active');
        } else {
            const items = document.querySelectorAll('.nav-item');
            items.forEach(el => el.classList.remove('active'));
            if(viewName==='map') items[1].classList.add('active');
            if(viewName==='history') items[2].classList.add('active');
            if(viewName==='home') items[0].classList.add('active');
        }
        
        const fab = document.getElementById('fab');
        fab.style.display = (viewName === 'home') ? 'flex' : 'none';
        
        const header = document.getElementById('main-header');
        if (viewName === 'profile' || viewName === 'map') header.classList.add('hidden-view');
        else header.classList.remove('hidden-view');

        if (viewName === 'history') renderHistory();
        if (viewName === 'map' && !mapInitialized) initMap();
    }

    // --- Dynamic Data Fetching & Rendering ---
    let globalProviders = [];
    let userLat = 33.626;
    let userLng = 73.042;
    let currentFilter = 'nearest';

    function renderCategories() {
        const catMap = [
            { name: "AC Technician", icon: "fa-snowflake", color: "blue" },
            { name: "Plumber", icon: "fa-faucet-drip", color: "cyan" },
            { name: "Electrician", icon: "fa-bolt", color: "yellow" },
            { name: "Carpenter", icon: "fa-hammer", color: "orange" },
            { name: "Laundry", icon: "fa-shirt", color: "indigo" },
            { name: "Mobile Repair", icon: "fa-mobile", color: "gray" },
            { name: "Cleaning", icon: "fa-broom", color: "green" },
            { name: "Beauty Services", icon: "fa-spa", color: "pink" },
            { name: "Car Mechanic", icon: "fa-car", color: "red" },
            { name: "Doctor Visit", icon: "fa-user-doctor", color: "teal" },
            { name: "Cobbler / Shoe Repair", icon: "fa-shoe-prints", color: "purple" },
            { name: "Window Fixer", icon: "fa-window-maximize", color: "amber" },
            { name: "Computer Repair", icon: "fa-desktop", color: "lime" },
            { name: "Laptop Repair", icon: "fa-laptop", color: "emerald" },
            { name: "Painter", icon: "fa-paint-roller", color: "rose" },
            { name: "Pest Control", icon: "fa-bug", color: "brown" },
            { name: "Water Tank Cleaning", icon: "fa-tint", color: "sky" },
            { name: "Movers", icon: "fa-truck", color: "slate" },
            { name: "Locksmith", icon: "fa-key", color: "zinc" },
            { name: "Gardening", icon: "fa-seedling", color: "emerald" },
            { name: "Interior Work", icon: "fa-home", color: "indigo" },
            { name: "Salon", icon: "fa-cut", color: "pink" },
            { name: "Lab Test", icon: "fa-vial", color: "fuchsia" },
            { name: "Bike Mechanic", icon: "fa-bicycle", color: "cyan" }
        ];
        
        const grid = document.getElementById('categories-grid');
        grid.innerHTML = '';
        catMap.forEach(c => {
            grid.innerHTML += `
                <div class="flex-shrink-0 bg-white p-3 rounded-xl border border-surface-200 flex flex-col items-center justify-center gap-2 shadow-sm active:scale-95 transition-transform cursor-pointer w-24 h-24" onclick="openChatWith('${c.name}')">
                    <div class="w-10 h-10 rounded-full bg-${c.color}-50 flex items-center justify-center text-${c.color}-500"><i class="fa-solid ${c.icon}"></i></div>
                    <div class="font-semibold text-xs text-center leading-tight">${c.name}</div>
                </div>
            `;
        });
    }

    async function loadProviders() {
        try {
            renderCategories();
            const res = await fetch(`/api/v1/providers?lat=${userLat}&lng=${userLng}&sort_by=${currentFilter}`);
            const data = await res.json();
            globalProviders = data.providers;
            renderProviderList();
            if (mapInitialized) updateMapMarkers();
        } catch(e) {
            console.error("Failed to load providers", e);
        }
    }

    function renderProviderList() {
        const listContainer = document.getElementById('top-providers-list');
        listContainer.innerHTML = `
            <div class="flex gap-2 mb-3 overflow-x-auto pb-1 scrollbar-hide text-xs font-bold">
                <div class="px-3 py-1.5 rounded-full cursor-pointer transition-colors ${currentFilter==='nearest' ? 'bg-brand-500 text-white' : 'bg-surface-200 text-surface-600'}" onclick="setFilter('nearest')">Nearest</div>
                <div class="px-3 py-1.5 rounded-full cursor-pointer transition-colors ${currentFilter==='cheapest' ? 'bg-brand-500 text-white' : 'bg-surface-200 text-surface-600'}" onclick="setFilter('cheapest')">Cheapest</div>
                <div class="px-3 py-1.5 rounded-full cursor-pointer transition-colors ${currentFilter==='highest_rated' ? 'bg-brand-500 text-white' : 'bg-surface-200 text-surface-600'}" onclick="setFilter('highest_rated')">Top Rated</div>
            </div>
        `;
        
        // Show top 10 in the list to prevent lag
        globalProviders.slice(0, 10).forEach(p => {
            const initial = p.name.split(' ').map(n=>n[0]).join('').substring(0,2).toUpperCase();
            const colors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-orange-500', 'bg-indigo-500', 'bg-pink-500'];
            const color = colors[p.id.charCodeAt(p.id.length-1) % colors.length];
            
            listContainer.innerHTML += `
                <div class="bg-white rounded-xl p-3 border border-surface-200 shadow-sm flex items-center justify-between active:scale-95 transition-transform cursor-pointer hover:border-brand-300" onclick="openChatWith('${p.category}')">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-full ${color} text-white flex items-center justify-center font-bold text-sm shadow-inner relative overflow-hidden">
                            <img src="${p.avatar}" class="w-full h-full object-cover" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex'">
                            <div class="absolute inset-0 flex items-center justify-center hidden">${initial}</div>
                        </div>
                        <div>
                            <div class="font-bold text-sm text-surface-800">${p.name}</div>
                            <div class="text-[11px] text-surface-500">${p.category} • ${p.distance_km} km away</div>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-xs font-bold text-yellow-600 bg-yellow-50 px-2 py-1 rounded border border-yellow-200 inline-flex items-center gap-1 mb-1">
                            <i class="fa-solid fa-star text-[10px]"></i> ${p.rating}
                        </div>
                        <div class="text-[10px] font-bold text-brand-600">PKR ${p.hourly_rate}/hr</div>
                    </div>
                </div>
            `;
        });
    }

    function setFilter(filter) {
        currentFilter = filter;
        loadProviders();
    }
    
    // Load providers on boot
    loadProviders();

    let mapMarkers = [];
    
    function updateMapMarkers() {
        if(!leafletMap) return;
        
        // Clear existing markers
        mapMarkers.forEach(m => leafletMap.removeLayer(m));
        mapMarkers = [];
        
        const mapCards = document.getElementById('map-cards-container');
        mapCards.innerHTML = '';
        
        const customIcon = L.divIcon({
            className: 'custom-pin',
            html: '<i class="fa-solid fa-location-dot" style="color: #008b4b; font-size: 36px; text-shadow: 0 4px 6px rgba(0,0,0,0.3);"></i>',
            iconSize: [36, 36],
            iconAnchor: [18, 36]
        });
        
        // Render up to 50 pins to keep map smooth
        globalProviders.slice(0, 50).forEach((p, index) => {
            const marker = L.marker([p.lat, p.lng], {icon: customIcon}).addTo(leafletMap);
            mapMarkers.push(marker);
            
            const popupHtml = `
                <div class="text-center w-32">
                    <img src="${p.avatar}" class="w-12 h-12 rounded-full mx-auto mb-1 border-2 border-brand-500">
                    <b class="text-sm">${p.name}</b><br>
                    <span class="text-xs text-surface-500">${p.category} - PKR ${p.hourly_rate}/hr</span>
                    <button class="w-full mt-2 bg-brand-500 text-white rounded py-1 text-xs font-bold" onclick="directBookMap('${p.name}', '${p.category}', 'PKR ${p.hourly_rate}')">Book Now</button>
                </div>
            `;
            marker.bindPopup(popupHtml);

            mapCards.innerHTML += `
                <div class="flex-shrink-0 w-64 border rounded-xl p-3 bg-surface-50 border-surface-200 shadow-sm cursor-pointer" onclick="leafletMap.setView([${p.lat}, ${p.lng}], 15)">
                    <div class="flex gap-2 items-center mb-2">
                        <img src="${p.avatar}" class="w-10 h-10 rounded-full border border-surface-200">
                        <div class="flex-1">
                            <div class="font-semibold text-sm text-surface-800 leading-tight">${p.name}</div>
                            <div class="text-[10px] text-surface-500">${p.category} • ${p.distance_km} km away</div>
                        </div>
                        <div class="text-xs font-bold text-yellow-600"><i class="fa-solid fa-star"></i> ${p.rating}</div>
                    </div>
                    <div class="flex justify-between items-center text-[11px] mb-2">
                        <span class="text-surface-600"><i class="fa-solid fa-clock mr-1 text-brand-500"></i> ETA: ${p.response_time_min}m</span>
                        <span class="font-bold text-brand-600">PKR ${p.hourly_rate}/hr</span>
                    </div>
                    <button class="w-full bg-brand-500 text-white hover:bg-brand-600 transition-colors py-1.5 rounded-lg text-xs font-bold flex items-center justify-center gap-2" onclick="directBookMap('${p.name}', '${p.category}', 'PKR ${p.hourly_rate}')">
                        <i class="fa-solid fa-bolt"></i> Direct Book
                    </button>
                </div>
            `;
        });
    }

    // --- Interactive Leaflet Map ---
    function initMap() {
        if(typeof L === 'undefined') return;
        
        const mapCenter = [userLat, userLng];
        leafletMap = L.map('interactive-map', { zoomControl: false }).setView(mapCenter, 13);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap'
        }).addTo(leafletMap);

        const myLocIcon = L.divIcon({
            className: 'custom-div-icon',
            html: '<div class="my-location-marker"></div>',
            iconSize: [16, 16],
            iconAnchor: [8, 8]
        });
        L.marker(mapCenter, {icon: myLocIcon}).addTo(leafletMap).bindPopup('<b>You are here</b><br>Near NUTECH, I-12');

        updateMapMarkers();
        mapInitialized = true;
    }
    
    function simulateMapSearch() {
        const val = document.getElementById('map-search-input').value;
        if(val && leafletMap) {
            leafletMap.setZoom(11);
            setTimeout(() => {
                leafletMap.panTo([33.606, 72.981]);
                setTimeout(() => leafletMap.setZoom(14), 600);
            }, 600);
        }
    }

    // --- Modals ---
    function openModal(title, contentHtml = '') {
        document.getElementById('modal-title').innerText = title;
        const body = document.getElementById('modal-body');
        
        if (title === 'Saved Addresses') {
            body.innerHTML = `
                <div class="border rounded-xl p-3 mb-2 flex justify-between items-center bg-brand-50 border-brand-200">
                    <div><span class="font-bold block text-surface-800">Home</span><span class="text-xs text-surface-500">Near NUTECH, I-12, Islamabad</span></div>
                    <i class="fa-solid fa-check-circle text-brand-500"></i>
                </div>
                <div class="border rounded-xl p-3 mb-3 flex justify-between items-center"><span class="font-bold text-surface-800">Office</span><span class="text-xs text-surface-500">EME College, Rawalpindi</span></div>
                <button class="w-full py-2 bg-surface-100 rounded-lg text-brand-600 font-bold border border-surface-200" onclick="alert('Open map selector to pin new address.')">+ Add New Address</button>
            `;
        } else if (title === 'Payment Methods') {
            body.innerHTML = `
                <div class="border rounded-xl p-3 mb-2 flex items-center gap-3"><i class="fa-solid fa-money-bill-wave text-green-500"></i><span class="font-bold">Cash on Completion</span></div>
                <div class="border rounded-xl p-3 mb-3 flex items-center gap-3 opacity-50"><i class="fa-solid fa-wallet text-blue-500"></i><span>EasyPaisa / JazzCash</span></div>
                <button class="w-full py-2 bg-surface-100 rounded-lg text-brand-600 font-bold border border-surface-200" onclick="alert('Redirecting to secure card payment gateway...')">+ Add Card</button>
            `;
        } else if (title === 'Settings') {
            const isDark = document.documentElement.classList.contains('dark');
            body.innerHTML = `
                <div class="flex justify-between items-center py-2 border-b"><span class="font-medium">Language</span><span class="text-brand-500 font-bold text-xs bg-brand-50 px-2 py-1 rounded">English / Roman Urdu</span></div>
                <div class="flex justify-between items-center py-2 border-b"><span class="font-medium">Push Notifications</span><input type="checkbox" checked class="accent-brand-500 w-4 h-4"></div>
                <div class="flex justify-between items-center py-2 border-b">
                    <span class="font-medium">Dark Mode</span>
                    <input type="checkbox" class="accent-brand-500 w-4 h-4" onchange="toggleDarkMode()" ${isDark ? 'checked' : ''}>
                </div>
                <p class="text-xs text-center mt-4 text-surface-400">Rozgar App Version 1.0.3</p>
            `;
        } else if (title === 'Help & Support') {
            body.innerHTML = `
                <p>Need assistance? Contact our 24/7 support team.</p>
                <div class="bg-brand-50 text-brand-700 p-3 rounded-lg flex items-center gap-2 mb-2 font-bold justify-center"><i class="fa-brands fa-whatsapp text-lg"></i> Chat on WhatsApp</div>
                <div class="bg-surface-100 text-surface-700 p-3 rounded-lg flex items-center gap-2 font-bold justify-center"><i class="fa-solid fa-phone"></i> 0800-ROZGAR</div>
            `;
        } else {
            body.innerHTML = contentHtml;
        }
        
        document.getElementById('generic-modal').classList.add('active');
    }

    function closeModal() {
        document.getElementById('generic-modal').classList.remove('active');
    }
    
    function toggleDarkMode() {
        document.documentElement.classList.toggle('dark');
    }

    // --- Notifications Logic ---
    function openNotifications() {
        document.getElementById('notif-dot').style.display = 'none';
        const upc = myBookings.find(b => b.status === 'upcoming');
        let html = '';
        if (upc) {
            html = `
                <div class="bg-blue-50 border border-blue-200 p-3 rounded-lg mb-2 relative animate-pop-in">
                    <div class="absolute top-0 right-0 bg-red-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-bl-lg">NOW</div>
                    <div class="font-bold text-blue-800 flex items-center gap-2 mb-1"><i class="fa-solid fa-clock"></i> 1 Hour Left!</div>
                    <p class="text-xs text-blue-900">Your appointment with <b>${upc.provider}</b> is coming up soon. ETA is ${upc.eta}. Please be ready!</p>
                </div>
            `;
        }
        html += `
            <div class="p-3 border-b border-surface-100">
                <div class="font-bold text-sm text-surface-700 mb-1">Booking Confirmed</div>
                <p class="text-xs text-surface-500">Your AC Repair booking was confirmed yesterday.</p>
            </div>
            <div class="p-3">
                <div class="font-bold text-sm text-surface-700 mb-1">Welcome to Rozgar AI</div>
                <p class="text-xs text-surface-500">Start booking services via voice today!</p>
            </div>
        `;
        openModal('Notifications', html);
    }

    // --- History Logic ---
    function switchHistoryTab(tab) {
        currentHistoryTab = tab;
        const tabs = document.getElementById('history-tabs').children;
        Array.from(tabs).forEach(t => t.className = "pb-3 text-surface-400 font-medium text-sm cursor-pointer hover:text-surface-600 transition-colors");
        let activeIndex = tab === 'upcoming' ? 0 : (tab === 'completed' ? 1 : 2);
        tabs[activeIndex].className = "pb-3 border-b-2 border-brand-500 font-semibold text-brand-500 text-sm cursor-pointer";
        renderHistory();
    }

    function cancelBooking(id) {
        if(confirm("Are you sure you want to cancel this booking?")) {
            const booking = myBookings.find(b => b.id === id);
            if(booking) booking.status = 'cancelled';
            renderHistory();
        }
    }

    function renderHistory() {
        const filtered = myBookings.filter(b => b.status === currentHistoryTab);
        document.getElementById('count-upcoming').innerText = `(${myBookings.filter(b=>b.status==='upcoming').length})`;
        document.getElementById('count-completed').innerText = `(${myBookings.filter(b=>b.status==='completed').length})`;
        document.getElementById('count-cancelled').innerText = `(${myBookings.filter(b=>b.status==='cancelled').length})`;
        
        const list = document.getElementById('history-list');
        list.innerHTML = '';
        
        if (filtered.length === 0) {
            list.innerHTML = `<div class="text-center py-10 text-surface-400"><i class="fa-solid fa-box-open text-4xl mb-3 opacity-50"></i><p>No ${currentHistoryTab} bookings found.</p></div>`;
            return;
        }

        filtered.forEach(b => {
            let badgeHtml = '';
            let actionHtml = '';
            
            if (b.status === 'upcoming') {
                badgeHtml = `<div class="text-[10px] font-bold text-blue-600 bg-blue-100 px-2 py-1 rounded inline-block mb-2 tracking-wide uppercase">Confirmed • ${b.eta || 'N/A'}</div>`;
                actionHtml = `
                    <div class="flex gap-2 mt-4 pt-3 border-t">
                        <button class="flex-1 border border-red-200 text-red-500 hover:bg-red-50 py-2 rounded-lg text-sm font-semibold transition-colors active:scale-95" onclick="cancelBooking('${b.id}')">Cancel</button>
                        <button class="flex-1 bg-brand-50 text-brand-600 hover:bg-brand-100 py-2 rounded-lg text-sm font-semibold transition-colors active:scale-95"><i class="fa-brands fa-whatsapp mr-1"></i> Contact</button>
                    </div>
                `;
            } else if (b.status === 'completed') {
                badgeHtml = `<div class="text-[10px] font-bold text-green-600 bg-green-100 px-2 py-1 rounded inline-block mb-2 tracking-wide uppercase">Completed</div>`;
                actionHtml = `<div class="mt-3 text-center"><button class="text-brand-500 text-sm font-semibold" onclick="openChatWith('${b.service}')">Book Again</button></div>`;
            } else if (b.status === 'cancelled') {
                badgeHtml = `<div class="text-[10px] font-bold text-surface-500 bg-surface-100 px-2 py-1 rounded inline-block mb-2 tracking-wide uppercase">Cancelled</div>`;
            }

            list.innerHTML += `
                <div class="bg-white rounded-xl p-4 shadow-sm border border-surface-200 mb-4 animate-fade-in relative overflow-hidden">
                    ${b.status === 'upcoming' ? '<div class="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>' : ''}
                    <div class="flex justify-between items-start mb-2">
                        <div>
                            ${badgeHtml}
                            <h4 class="font-bold text-surface-800">${b.service}</h4>
                            <p class="text-sm text-surface-500"><i class="fa-solid fa-user-tie text-xs w-4"></i> ${b.provider}</p>
                        </div>
                        <div class="text-right">
                            <div class="font-bold text-surface-800">${b.price}</div>
                        </div>
                    </div>
                    <div class="flex items-center gap-2 text-[11px] text-surface-500 mt-3 bg-surface-50 p-2 rounded-lg border border-surface-100">
                        <i class="fa-regular fa-calendar text-brand-500"></i> ${b.date}, ${b.time}
                        <span class="mx-1 opacity-50">|</span>
                        <i class="fa-solid fa-location-dot text-brand-500"></i> <span class="truncate max-w-[120px]">${b.location}</span>
                    </div>
                    ${actionHtml}
                </div>
            `;
        });
    }

    // --- Profile Image Upload Simulation ---
    function loadProfilePic(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) { document.getElementById('profile-pic').src = e.target.result; }
            reader.readAsDataURL(file);
        }
    }

    // --- Chat & Booking Orchestration UI ---
    const chatOverlay = document.getElementById('chat-overlay');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    function openChat() {
        chatOverlay.classList.add('active');
        setTimeout(() => chatInput.focus(), 300);
    }
    
    function closeChat() {
        chatOverlay.classList.remove('active');
    }
    
    function openChatWith(service) {
        openChat();
        chatInput.value = `Mujhe ${service} chahiye...`;
    }

    function directBookMap(provider, service, cost) {
        openChat();
        // Immediately show the confirmation prompt for this specific provider
        const mockBooking = {
            booking_id: 'b' + Date.now(),
            service: service,
            provider: { name: provider },
            slot: 'As soon as possible',
            eta_minutes: '15',
            estimated_cost: cost,
            location: 'My Location'
        };
        showConfirmationPrompt(mockBooking);
    }

    function addMessage(text, sender) {
        const isUser = sender === 'user';
        const msgHtml = `
            <div class="flex gap-3 ${isUser ? 'flex-row-reverse' : ''} mb-4 animate-slide-up">
                ${isUser ? '' : `<div class="w-8 h-8 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center flex-shrink-0"><i class="fa-solid fa-robot"></i></div>`}
                <div class="${isUser ? 'bg-brand-500 text-white shadow-brand-500/30' : 'bg-surface-100 text-surface-800 shadow-sm border border-surface-200'} rounded-2xl ${isUser ? 'rounded-tr-none' : 'rounded-tl-none'} p-3 text-sm max-w-[85%] shadow-sm leading-relaxed">
                    ${text}
                </div>
            </div>
        `;
        chatMessages.insertAdjacentHTML('beforeend', msgHtml);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    document.getElementById('chat-send').addEventListener('click', sendRequest);
    chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendRequest(); });

    async function sendRequest() {
        const text = chatInput.value.trim();
        if (!text) return;
        
        addMessage(text, 'user');
        chatInput.value = '';
        chatInput.disabled = true;
        
        const loaderId = 'loader-' + Date.now();
        chatMessages.insertAdjacentHTML('beforeend', `
            <div id="${loaderId}" class="flex gap-3 mb-4 animate-fade-in">
                <div class="w-8 h-8 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center flex-shrink-0"><i class="fa-solid fa-circle-notch fa-spin"></i></div>
                <div class="bg-surface-50 rounded-2xl rounded-tl-none p-3 text-sm text-surface-500 italic border border-surface-200">Finding the best matches...</div>
            </div>
        `);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/api/v1/request', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            const data = await response.json();
            
            document.getElementById(loaderId).remove();
            
            if (data.success && data.booking) {
                // Instead of direct confirm, ask the user
                showConfirmationPrompt(data.booking);
            } else {
                addMessage(`Sorry, I couldn't process that: ${data.error}`, 'bot');
            }
        } catch (err) {
            document.getElementById(loaderId)?.remove();
            addMessage(`Network error connecting to AI engine.`, 'bot');
        } finally {
            chatInput.disabled = false;
            chatInput.focus();
        }
    }

    // Function to show "Are you sure you want to confirm?" card
    function showConfirmationPrompt(b) {
        tempPendingBooking = b;
        const promptHtml = `
            <div class="bg-white border-2 border-brand-500 rounded-xl p-4 shadow-lg w-full mt-2 relative overflow-hidden" id="pending-card-${b.booking_id}">
                <div class="flex items-center gap-2 text-brand-600 font-bold mb-3 border-b pb-2">
                    <i class="fa-solid fa-file-invoice"></i> Review Booking Details
                </div>
                <div class="grid grid-cols-2 gap-y-3 text-sm">
                    <div><span class="block text-surface-400 text-[10px] uppercase font-bold tracking-wider">Provider</span><span class="font-semibold text-surface-800">${b.provider.name}</span></div>
                    <div><span class="block text-surface-400 text-[10px] uppercase font-bold tracking-wider">Service</span><span class="font-semibold text-surface-800">${b.service}</span></div>
                    <div><span class="block text-surface-400 text-[10px] uppercase font-bold tracking-wider">Time</span><span class="font-semibold text-surface-800">${b.slot}</span></div>
                    <div><span class="block text-surface-400 text-[10px] uppercase font-bold tracking-wider">ETA</span><span class="font-bold text-brand-600">${b.eta_minutes} mins</span></div>
                </div>
                <div class="mt-3 pt-3 border-t bg-surface-50 -mx-4 -mb-4 p-4 flex justify-between items-center font-bold">
                    <span class="text-surface-600">Est. Cost</span>
                    <span class="text-lg text-brand-600">${b.estimated_cost}</span>
                </div>
            </div>
            <div class="bg-surface-100 p-3 rounded-b-xl border border-t-0 border-surface-200 mt-0">
                <p class="text-sm text-surface-700 mb-3 text-center font-bold">Do you want to confirm this booking?</p>
                <div class="flex gap-2">
                    <button class="flex-1 bg-white border border-surface-300 text-surface-700 py-2 rounded-lg font-bold text-sm active:scale-95" onclick="declineBooking()">Cancel</button>
                    <button class="flex-1 bg-brand-500 text-white py-2 rounded-lg font-bold text-sm shadow-md active:scale-95" onclick="acceptBooking()">Confirm Now</button>
                </div>
            </div>
        `;
        addMessage(promptHtml, 'bot');
    }

    function declineBooking() {
        tempPendingBooking = null;
        addMessage("Booking cancelled. Let me know if you need anything else!", 'bot');
    }

    function acceptBooking() {
        if(!tempPendingBooking) return;
        const b = tempPendingBooking;
        
        // Hide the action buttons from the previous card by overwriting its parent innerHTML or simply adding a success message
        addMessage(`
            <div class="bg-brand-50 border border-brand-200 rounded-lg p-3 text-brand-700 text-sm font-bold flex items-center gap-2">
                <i class="fa-solid fa-check-circle text-lg"></i> Booking Confirmed Successfully!
            </div>
        `, 'bot');

        // Add to internal state & re-render history
        myBookings.unshift({
            id: b.booking_id || 'b'+Date.now(),
            service: b.service,
            provider: b.provider.name,
            status: 'upcoming',
            price: b.estimated_cost,
            date: 'Today',
            time: b.slot,
            location: b.location || 'My Location',
            eta: b.eta_minutes + ' mins'
        });
        renderHistory();
        
        document.getElementById('notif-dot').style.display = 'block';
        tempPendingBooking = null;
        
        // Switch to history view after 1.5 seconds
        setTimeout(() => {
            closeChat();
            switchView('history');
        }, 1500);
    }
    
    renderHistory();
</script>
</body>
</html>
"""
