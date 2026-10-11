// EventFlow - Frontend JavaScript Vanilla
const API_BASE = 'http://127.0.0.1:8000/api';
let authToken = null;
let currentUser = null;
let espaciosCache = [];

// DOM Elements (populated after DOM ready)
const elements = {};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initElements();
    initEventListeners();
    checkAuthState();
    loadEspacios();
    loadRecursos();
});

function initElements() {
    // Auth
    elements.btnLogin = document.getElementById('btn-login');
    elements.btnLogout = document.getElementById('btn-logout');
    elements.userInfo = document.getElementById('user-info');
    elements.loginModal = document.getElementById('login-modal');
    elements.loginForm = document.getElementById('login-form');
    elements.loginError = document.getElementById('login-error');
    elements.btnCancelLogin = document.getElementById('btn-cancel-login');
    
    // Espacios
    elements.btnAddEspacio = document.getElementById('btn-add-espacio');
    elements.espacioFormContainer = document.getElementById('espacio-form-container');
    elements.espacioForm = document.getElementById('espacio-form');
    elements.espacioFormTitle = document.getElementById('espacio-form-title');
    elements.espacioId = document.getElementById('espacio-id');
    elements.espacioNombre = document.getElementById('espacio-nombre');
    elements.espacioUbicacion = document.getElementById('espacio-ubicacion');
    elements.espacioAforo = document.getElementById('espacio-aforo');
    elements.espacioEstado = document.getElementById('espacio-estado');
    elements.btnCancelEspacio = document.getElementById('btn-cancel-espacio');
    elements.espacioFormError = document.getElementById('espacio-form-error');
    elements.espaciosList = document.getElementById('espacios-list');
    elements.espaciosLoading = document.getElementById('espacios-loading');
    elements.espaciosError = document.getElementById('espacios-error');
    
    // Recursos
    elements.btnAddRecurso = document.getElementById('btn-add-recurso');
    elements.recursoFormContainer = document.getElementById('recurso-form-container');
    elements.recursoForm = document.getElementById('recurso-form');
    elements.recursoFormTitle = document.getElementById('recurso-form-title');
    elements.recursoId = document.getElementById('recurso-id');
    elements.recursoNombre = document.getElementById('recurso-nombre');
    elements.recursoCodigo = document.getElementById('recurso-codigo');
    elements.recursoCosto = document.getElementById('recurso-costo');
    elements.recursoStock = document.getElementById('recurso-stock');
    elements.recursoEspacio = document.getElementById('recurso-espacio');
    elements.btnCancelRecurso = document.getElementById('btn-cancel-recurso');
    elements.recursoFormError = document.getElementById('recurso-form-error');
    elements.recursosList = document.getElementById('recursos-list');
    elements.recursosLoading = document.getElementById('recursos-loading');
    elements.recursosError = document.getElementById('recursos-error');
    
    // Filters
    elements.filterEspacio = document.getElementById('filter-espacio');
    elements.filterCostoMin = document.getElementById('filter-costo-min');
    elements.filterCostoMax = document.getElementById('filter-costo-max');
    elements.btnApplyFilters = document.getElementById('btn-apply-filters');
    elements.btnClearFilters = document.getElementById('btn-clear-filters');
}

// Event Listeners
function initEventListeners() {
    // Auth
    elements.btnLogin.addEventListener('click', () => showModal(elements.loginModal));
    elements.btnLogout.addEventListener('click', logout);
    elements.btnCancelLogin.addEventListener('click', () => hideModal(elements.loginModal));
    elements.loginForm.addEventListener('submit', handleLogin);
    
    // Espacios
    elements.btnAddEspacio.addEventListener('click', () => showEspacioForm());
    elements.btnCancelEspacio.addEventListener('click', hideEspacioForm);
    elements.espacioForm.addEventListener('submit', handleEspacioSubmit);
    
    // Recursos
    elements.btnAddRecurso.addEventListener('click', () => showRecursoForm());
    elements.btnCancelRecurso.addEventListener('click', hideRecursoForm);
    elements.recursoForm.addEventListener('submit', handleRecursoSubmit);
    
    // Filters
    elements.btnApplyFilters.addEventListener('click', loadRecursos);
    elements.btnClearFilters.addEventListener('click', clearFilters);
    
    // Close modal on overlay click
    elements.loginModal.addEventListener('click', (e) => {
        if (e.target === elements.loginModal) hideModal(elements.loginModal);
    });
}

// Auth Functions
async function checkAuthState() {
    const token = sessionStorage.getItem('authToken');
    const userData = sessionStorage.getItem('userData');
    
    if (token && userData) {
        authToken = token;
        currentUser = JSON.parse(userData);
        updateAuthUI(true);
        return true;
    }
    updateAuthUI(false);
    return false;
}

function updateAuthUI(isLoggedIn) {
    if (isLoggedIn) {
        elements.btnLogin.classList.add('hidden');
        elements.btnLogout.classList.remove('hidden');
        elements.userInfo.classList.remove('hidden');
        elements.userInfo.textContent = `Hola, ${currentUser.username}`;
        elements.btnAddEspacio.disabled = false;
        elements.btnAddRecurso.disabled = false;
    } else {
        elements.btnLogin.classList.remove('hidden');
        elements.btnLogout.classList.add('hidden');
        elements.userInfo.classList.add('hidden');
        elements.btnAddEspacio.disabled = true;
        elements.btnAddRecurso.disabled = true;
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const formData = new FormData(elements.loginForm);
    const username = formData.get('username');
    const password = formData.get('password');
    
    setLoading(elements.loginForm.querySelector('button[type="submit"]'), true);
    hideError(elements.loginError);
    
    try {
        const response = await fetch(`${API_BASE}/auth/token/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok && data.access) {
            authToken = data.access;
            currentUser = { username };
            sessionStorage.setItem('authToken', authToken);
            sessionStorage.setItem('userData', JSON.stringify(currentUser));
            updateAuthUI(true);
            hideModal(elements.loginModal);
            elements.loginForm.reset();
            showSuccess('Inicio de sesión exitoso');
            loadEspacios();
            loadRecursos();
        } else {
            showError(elements.loginError, data.detail || 'Credenciales inválidas');
        }
    } catch (error) {
        showError(elements.loginError, 'Error de conexión. Verifica que el servidor esté corriendo.');
    } finally {
        setLoading(elements.loginForm.querySelector('button[type="submit"]'), false);
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    sessionStorage.removeItem('authToken');
    sessionStorage.removeItem('userData');
    updateAuthUI(false);
    showSuccess('Sesión cerrada correctamente');
}

// API Helper
async function apiRequest(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const url = `${API_BASE}${endpoint}`;
    console.log('apiRequest:', options.method || 'GET', url, 'token:', authToken ? 'yes' : 'no');
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    let data;
    try {
        data = await response.json();
    } catch {
        data = {};
    }
    
    return { response, data, ok: response.ok, status: response.status };
}

// Espacios Functions
async function loadEspacios() {
    showLoading(elements.espaciosLoading, true);
    hideError(elements.espaciosError);
    
    try {
        const { response, data, ok } = await apiRequest('/espacios/');
        
        if (ok) {
            espaciosCache = data.results || data;
            renderEspacios(espaciosCache);
            updateEspacioSelect();
        } else {
            showError(elements.espaciosError, 'Error al cargar espacios');
        }
    } catch (error) {
        showError(elements.espaciosError, 'Error de conexión al cargar espacios');
    } finally {
        showLoading(elements.espaciosLoading, false);
    }
}

function renderEspacios(espacios) {
    elements.espaciosList.innerHTML = '';
    
    if (espacios.length === 0) {
        elements.espaciosList.innerHTML = '<p class="empty-state">No hay espacios registrados</p>';
        return;
    }
    
    espacios.forEach(espacio => {
        const card = createEspacioCard(espacio);
        elements.espaciosList.appendChild(card);
    });
}

function createEspacioCard(espacio) {
    const card = document.createElement('div');
    card.className = 'card';
    
    const estadoClass = `badge-${espacio.estado}`;
    const estadoLabel = getEstadoLabel(espacio.estado);
    
    card.innerHTML = `
        <div class="card-header">
            <h3 class="card-title">${escapeHtml(espacio.nombre)}</h3>
            <div class="card-actions">
                <button class="btn-icon edit" data-id="${espacio.id}" title="Editar">✏️</button>
                <button class="btn-icon delete" data-id="${espacio.id}" title="Eliminar">🗑️</button>
            </div>
        </div>
        <div class="card-body">
            <div class="card-field">
                <span class="card-field-label">Ubicación</span>
                <span class="card-field-value">${escapeHtml(espacio.ubicacion)}</span>
            </div>
            <div class="card-field">
                <span class="card-field-label">Aforo</span>
                <span class="card-field-value">${espacio.aforo_maximo} personas</span>
            </div>
            <div class="card-field">
                <span class="card-field-label">Estado</span>
                <span class="card-field-value"><span class="badge ${estadoClass}">${estadoLabel}</span></span>
            </div>
            <div class="card-field">
                <span class="card-field-label">Recursos</span>
                <span class="card-field-value">${espacio.recursos_count || 0}</span>
            </div>
        </div>
    `;
    
    card.querySelector('.edit').addEventListener('click', () => editEspacio(espacio));
    card.querySelector('.delete').addEventListener('click', () => deleteEspacio(espacio.id, espacio.nombre));
    
    return card;
}

function getEstadoLabel(estado) {
    const labels = {
        'operativo': 'Operativo',
        'mantenimiento': 'Mantenimiento',
        'fuera_servicio': 'Fuera de servicio'
    };
    return labels[estado] || estado;
}

function showEspacioForm(espacio = null) {
    elements.espacioForm.reset();
    hideError(elements.espacioFormError);
    
    if (espacio) {
        elements.espacioFormTitle.textContent = 'Editar Espacio';
        elements.espacioId.value = espacio.id;
        elements.espacioNombre.value = espacio.nombre;
        elements.espacioUbicacion.value = espacio.ubicacion;
        elements.espacioAforo.value = espacio.aforo_maximo;
        elements.espacioEstado.value = espacio.estado;
    } else {
        elements.espacioFormTitle.textContent = 'Nuevo Espacio';
        elements.espacioId.value = '';
    }
    
    elements.espacioFormContainer.classList.remove('hidden');
    elements.espacioNombre.focus();
}

function hideEspacioForm() {
    elements.espacioFormContainer.classList.add('hidden');
    elements.espacioForm.reset();
}

async function handleEspacioSubmit(e) {
    console.log('handleEspacioSubmit called', e);
    e.preventDefault();
    
    const id = elements.espacioId.value;
    const data = {
        nombre: elements.espacioNombre.value.trim(),
        ubicacion: elements.espacioUbicacion.value.trim(),
        aforo_maximo: parseInt(elements.espacioAforo.value),
        estado: elements.espacioEstado.value
    };
    
    const submitBtn = elements.espacioForm.querySelector('button[type="submit"]');
    setLoading(submitBtn, true);
    hideError(elements.espacioFormError);
    
    try {
        const endpoint = id ? `/espacios/${id}/` : '/espacios/';
        const method = id ? 'PUT' : 'POST';
        
        const payload = JSON.stringify(data);
        const { response, data: responseData, ok, status } = await apiRequest(endpoint, {
            method,
            body: payload
        });
        
        if (ok) {
            showSuccess(id ? 'Espacio actualizado correctamente' : 'Espacio creado correctamente');
            hideEspacioForm();
            loadEspacios();
        } else {
            const errorMsg = formatValidationErrors(responseData);
            showError(elements.espacioFormError, errorMsg);
        }
    } catch (error) {
        console.error('handleEspacioSubmit fetch error:', error);
        showError(elements.espacioFormError, 'Error de conexión: ' + error.message);
    } finally {
        setLoading(submitBtn, false);
    }
}

async function editEspacio(espacio) {
    showEspacioForm(espacio);
}

async function deleteEspacio(id, nombre) {
    if (!confirm(`¿Eliminar el espacio "${nombre}"?`)) return;
    
    try {
        const { response, data, ok, status } = await apiRequest(`/espacios/${id}/`, {
            method: 'DELETE'
        });
        
        if (ok) {
            showSuccess('Espacio eliminado correctamente');
            loadEspacios();
        } else if (status === 400) {
            showErrorAlert(data.error || 'No se puede eliminar: tiene recursos asociados');
        } else {
            showErrorAlert('Error al eliminar el espacio');
        }
    } catch (error) {
        showErrorAlert('Error de conexión');
    }
}

// Recursos Functions
async function loadRecursos() {
    showLoading(elements.recursosLoading, true);
    hideError(elements.recursosError);
    
    const params = new URLSearchParams();
    if (elements.filterEspacio.value) params.append('espacio', elements.filterEspacio.value);
    if (elements.filterCostoMin.value) params.append('costo_min', elements.filterCostoMin.value);
    if (elements.filterCostoMax.value) params.append('costo_max', elements.filterCostoMax.value);
    
    const queryString = params.toString();
    const endpoint = `/recursos/${queryString ? '?' + queryString : ''}`;
    
    try {
        const { response, data, ok } = await apiRequest(endpoint);
        
        if (ok) {
            renderRecursos(data.results || data);
        } else {
            showError(elements.recursosError, 'Error al cargar recursos');
        }
    } catch (error) {
        showError(elements.recursosError, 'Error de conexión al cargar recursos');
    } finally {
        showLoading(elements.recursosLoading, false);
    }
}

function renderRecursos(recursos) {
    elements.recursosList.innerHTML = '';
    
    if (recursos.length === 0) {
        elements.recursosList.innerHTML = '<p class="empty-state">No hay recursos registrados</p>';
        return;
    }
    
    recursos.forEach(recurso => {
        const card = createRecursoCard(recurso);
        elements.recursosList.appendChild(card);
    });
}

function createRecursoCard(recurso) {
    const card = document.createElement('div');
    card.className = 'card';
    
    card.innerHTML = `
        <div class="card-header">
            <h3 class="card-title">${escapeHtml(recurso.nombre)}</h3>
            <div class="card-actions">
                <button class="btn-icon edit" data-id="${recurso.id}" title="Editar">✏️</button>
                <button class="btn-icon delete" data-id="${recurso.id}" title="Eliminar">🗑️</button>
            </div>
        </div>
        <div class="card-body">
            <div class="card-field">
                <span class="card-field-label">Código</span>
                <span class="card-field-value">${escapeHtml(recurso.codigo_inventario)}</span>
            </div>
            <div class="card-field">
                <span class="card-field-label">Costo</span>
                <span class="card-field-value">$${parseFloat(recurso.costo).toFixed(2)}</span>
            </div>
            <div class="card-field">
                <span class="card-field-label">Stock</span>
                <span class="card-field-value">${recurso.cantidad_stock}</span>
            </div>
            <div class="card-field">
                <span class="card-field-label">Espacio</span>
                <span class="card-field-value">${escapeHtml(recurso.espacio_nombre || 'N/A')}</span>
            </div>
        </div>
    `;
    
    card.querySelector('.edit').addEventListener('click', () => editRecurso(recurso));
    card.querySelector('.delete').addEventListener('click', () => deleteRecurso(recurso.id, recurso.nombre));
    
    return card;
}

function updateEspacioSelect() {
    const select = elements.recursoEspacio;
    const currentValue = select.value;
    
    select.innerHTML = '<option value="">Seleccionar espacio...</option>';
    
    espaciosCache.forEach(espacio => {
        const option = document.createElement('option');
        option.value = espacio.id;
        option.textContent = `${espacio.nombre} (${espacio.ubicacion})`;
        select.appendChild(option);
    });
    
    // Restore value if editing
    if (currentValue) {
        select.value = currentValue;
    }
    
    // Also update filter select
    const filterSelect = elements.filterEspacio;
    const filterValue = filterSelect.value;
    filterSelect.innerHTML = '<option value="">Todos</option>';
    espaciosCache.forEach(espacio => {
        const option = document.createElement('option');
        option.value = espacio.id;
        option.textContent = `${espacio.nombre} (${espacio.ubicacion})`;
        filterSelect.appendChild(option);
    });
    if (filterValue) filterSelect.value = filterValue;
}

function showRecursoForm(recurso = null) {
    elements.recursoForm.reset();
    hideError(elements.recursoFormError);
    
    if (recurso) {
        elements.recursoFormTitle.textContent = 'Editar Recurso';
        elements.recursoId.value = recurso.id;
        elements.recursoNombre.value = recurso.nombre;
        elements.recursoCodigo.value = recurso.codigo_inventario;
        elements.recursoCosto.value = recurso.costo;
        elements.recursoStock.value = recurso.cantidad_stock;
        elements.recursoEspacio.value = recurso.espacio_id || '';
    } else {
        elements.recursoFormTitle.textContent = 'Nuevo Recurso';
        elements.recursoId.value = '';
    }
    
    elements.recursoFormContainer.classList.remove('hidden');
    elements.recursoNombre.focus();
}

function hideRecursoForm() {
    elements.recursoFormContainer.classList.add('hidden');
    elements.recursoForm.reset();
}

async function handleRecursoSubmit(e) {
    e.preventDefault();
    
    const id = elements.recursoId.value;
    const data = {
        nombre: elements.recursoNombre.value.trim(),
        codigo_inventario: elements.recursoCodigo.value.trim().toUpperCase(),
        costo: parseFloat(elements.recursoCosto.value),
        cantidad_stock: parseInt(elements.recursoStock.value),
        espacio_id: parseInt(elements.recursoEspacio.value)
    };
    
    const submitBtn = elements.recursoForm.querySelector('button[type="submit"]');
    setLoading(submitBtn, true);
    hideError(elements.recursoFormError);
    
    try {
        const endpoint = id ? `/recursos/${id}/` : '/recursos/';
        const method = id ? 'PUT' : 'POST';
        
        const payload = JSON.stringify(data);
        const { response, data: responseData, ok, status } = await apiRequest(endpoint, {
            method,
            body: payload
        });
        
        if (ok) {
            showSuccess(id ? 'Recurso actualizado correctamente' : 'Recurso creado correctamente');
            hideRecursoForm();
            loadRecursos();
        } else {
            const errorMsg = formatValidationErrors(responseData);
            showError(elements.recursoFormError, errorMsg);
        }
    } catch (error) {
        console.error('handleRecursoSubmit fetch error:', error);
        showError(elements.recursoFormError, 'Error de conexión: ' + error.message);
    } finally {
        setLoading(submitBtn, false);
    }
}

async function editRecurso(recurso) {
    showRecursoForm(recurso);
}

async function deleteRecurso(id, nombre) {
    if (!confirm(`¿Eliminar el recurso "${nombre}"?`)) return;
    
    try {
        const { response, data, ok } = await apiRequest(`/recursos/${id}/`, {
            method: 'DELETE'
        });
        
        if (ok) {
            showSuccess('Recurso eliminado correctamente');
            loadRecursos();
        } else {
            showErrorAlert('Error al eliminar el recurso');
        }
    } catch (error) {
        showErrorAlert('Error de conexión');
    }
}

function clearFilters() {
    elements.filterEspacio.value = '';
    elements.filterCostoMin.value = '';
    elements.filterCostoMax.value = '';
    loadRecursos();
}

// UI Helpers
function showModal(modal) {
    modal.classList.remove('hidden');
    modal.querySelector('input')?.focus();
}

function hideModal(modal) {
    modal.classList.add('hidden');
}

function showLoading(element, show) {
    if (show) {
        element.classList.remove('hidden');
    } else {
        element.classList.add('hidden');
    }
}

function setLoading(button, loading) {
    if (loading) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.textContent = 'Cargando...';
    } else {
        button.disabled = false;
        button.textContent = button.dataset.originalText || button.textContent;
    }
}

function showError(element, message) {
    element.textContent = message;
    element.classList.remove('hidden');
}

function hideError(element) {
    element.classList.add('hidden');
    element.textContent = '';
}

function showErrorAlert(message) {
    alert(message); // Simple alert for delete confirmations
}

function showSuccess(message) {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = 'success-message';
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '2000';
    toast.style.maxWidth = '350px';
    toast.style.boxShadow = 'var(--shadow)';
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function formatValidationErrors(errors) {
    if (typeof errors === 'string') return errors;
    if (Array.isArray(errors)) return errors.join(', ');
    
    const messages = [];
    for (const [field, fieldErrors] of Object.entries(errors)) {
        if (Array.isArray(fieldErrors)) {
            messages.push(`${field}: ${fieldErrors.join(', ')}`);
        } else {
            messages.push(`${field}: ${fieldErrors}`);
        }
    }
    return messages.join('; ');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}