// Use relative path for Nginx proxy
const GATEWAY_URL = '/api';

let currentUser = null;

// --- App State & Navigation ---
function showView(viewId) {
    if (!currentUser && viewId !== 'auth') {
        showView('auth');
        return;
    }

    document.querySelectorAll('.view').forEach(el => el.style.display = 'none');
    document.getElementById(`view-${viewId}`).style.display = 'block';

    // Update active nav
    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
    // Simple nav highlighting

    if (viewId === 'shop') fetchProducts();
    if (viewId === 'orders') fetchMyOrders();
}

function updateUserInfo() {
    const userInfoDiv = document.getElementById('user-info');
    const display = document.getElementById('username-display');
    const wallet = document.getElementById('wallet-display');
    const logoutBtn = document.getElementById('logout-btn');

    if (currentUser) {
        display.textContent = currentUser.name;
        wallet.textContent = `Balance: $${currentUser.wallet || 0}`;
        logoutBtn.style.display = 'inline-block';

        // Refresh wallet in background
        fetchUser(currentUser.id);
    } else {
        display.textContent = 'Guest';
        wallet.textContent = '';
        logoutBtn.style.display = 'none';
        showView('auth');
    }
}

async function fetchUser(id) {
    try {
        const res = await fetch(`${GATEWAY_URL}/users/${id}`);
        if (res.ok) {
            currentUser = await res.json();
            const wallet = document.getElementById('wallet-display');
            wallet.textContent = `Balance: $${currentUser.wallet}`;
        }
    } catch (e) { }
}

// --- Auth ---
function switchAuth(mode) {
    document.getElementById('login-form').style.display = mode === 'login' ? 'block' : 'none';
    document.getElementById('register-form').style.display = mode === 'register' ? 'block' : 'none';
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;

    try {
        const res = await fetch(`${GATEWAY_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });

        if (res.ok) {
            const data = await res.json();
            // Fetch full user details to get wallet
            const userRes = await fetch(`${GATEWAY_URL}/users/${data.id}`);
            currentUser = await userRes.json();

            showToast('Login successful!');
            updateUserInfo();
            showView('shop');
        } else {
            showToast('Login failed. User not found.', 'error');
        }
    } catch (err) {
        showToast('Connection error', 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;

    try {
        const res = await fetch(`${GATEWAY_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email })
        });

        if (res.ok) {
            currentUser = await res.json();
            showToast('Account created! Welcome bonus: $1000');
            updateUserInfo();
            showView('shop');
        }
    } catch (err) {
        showToast('Registration failed', 'error');
    }
}

function logout() {
    currentUser = null;
    updateUserInfo();
    showToast('Logged out');
}

// --- Shop ---
async function fetchProducts() {
    try {
        const res = await fetch(`${GATEWAY_URL}/products`);
        const products = await res.json();

        const container = document.getElementById('products-grid');
        container.innerHTML = products.map(p => `
            <div class="product-card">
                <span class="tag ${p.stock > 0 ? 'stock' : 'out'}">
                    ${p.stock > 0 ? `In Stock: ${p.stock}` : 'Out of Stock'}
                </span>
                <h3>${p.name}</h3>
                <div class="price-row">
                    <span class="price">$${p.price}</span>
                </div>
                <button onclick="buyProduct(${p.id}, ${p.price})" 
                        class="primary-btn" 
                        ${p.stock === 0 ? 'disabled style="opacity:0.5;cursor:not-allowed"' : ''}>
                    ${p.stock > 0 ? 'Buy Now' : 'Sold Out'}
                </button>
            </div>
        `).join('');
    } catch (err) {
        showToast('Failed to load products', 'error');
    }
}

async function buyProduct(productId, price) {
    if (!currentUser) return showToast('Please login first', 'error');
    if (confirm(`Confirm purchase for $${price}?`)) {
        try {
            const res = await fetch(`${GATEWAY_URL}/orders`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: currentUser.id,
                    product_id: productId,
                    quantity: 1
                })
            });

            const data = await res.json();

            if (res.ok) {
                showToast(`Order #${data.id} confirmed!`);
                updateUserInfo(); // Refresh wallet
                fetchProducts(); // Refresh stock
            } else {
                showToast(data.detail || 'Purchase failed', 'error');
            }
        } catch (err) {
            showToast('Transaction failed', 'error');
        }
    }
}

// --- Orders ---
async function fetchMyOrders() {
    if (!currentUser) return;
    try {
        const res = await fetch(`${GATEWAY_URL}/orders/user/${currentUser.id}`);
        const orders = await res.json();

        const container = document.getElementById('orders-list');
        if (orders.length === 0) {
            container.innerHTML = '<p class="text-center">No orders yet.</p>';
            return;
        }

        container.innerHTML = orders.map(o => `
            <div class="card" style="margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>Order #${o.id}</strong>
                    <div>Product ID: ${o.product_id}</div>
                    <div style="font-size: 0.8rem; color: #666">Qty: ${o.quantity} • Status: ${o.status}</div>
                </div>
            </div>
        `).join('');
    } catch (err) {
        showToast('Failed to load orders', 'error');
    }
}

// --- Admin ---
async function handleCreateProduct(e) {
    e.preventDefault();
    const name = document.getElementById('prod-name').value;
    const price = parseFloat(document.getElementById('prod-price').value);
    const stock = parseInt(document.getElementById('prod-stock').value);

    try {
        const res = await fetch(`${GATEWAY_URL}/products`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, price, stock })
        });

        if (res.ok) {
            showToast('Product added successfully!');
            e.target.reset();
        }
    } catch (err) {
        showToast('Failed to add product', 'error');
    }
}

async function checkSystemStatus() {
    try {
        const res = await fetch(`${GATEWAY_URL}/status`);
        const data = await res.json();
        document.getElementById('system-status').innerHTML =
            `<span style="color: green">● Online</span> (Gateway: ${data.status})`;
    } catch (err) {
        document.getElementById('system-status').innerHTML =
            `<span style="color: red">● Offline</span>`;
    }
}

async function runStressTest() {
    const sec = document.getElementById('stress-sec').value;
    const intensity = document.getElementById('stress-int').value;
    
    showToast(`Triggering load for ${sec}s...`, 'info');
    
    try {
        // This hits: http://localhost:3000/api/stress?seconds=15&intensity=2
        const res = await fetch(`${GATEWAY_URL}/stress?seconds=${sec}&intensity=${intensity}`);
        const data = await res.json();
        showToast("Stress test active!", "success");
    } catch (err) {
        showToast("Failed to trigger stress", "error");
    }
}

// --- Utilities ---
function showToast(msg, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = msg;
    document.getElementById('toast-container').appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Init
checkSystemStatus();
updateUserInfo(); 
