/**
 * SIMBAR TKJ - Lab Inventory Management System
 * Frontend Client (Communicates with EC2 IAM Role Backend via REST API)
 * S3 Private Photo Streaming & DynamoDB Integration
 */

// Global State
let inventoryData = [];
let currentCategoryFilter = 'ALL';
let currentConditionFilter = 'ALL';
let searchQuery = '';
let currentViewMode = 'grid'; // 'grid' | 'table'
let selectedPhotoFile = null;

// ==========================================================================
// Initialization
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    fetchServerConfig();
    fetchInventoryData();
    setupDragAndDrop();
});

async function fetchServerConfig() {
    try {
        const res = await fetch('/api/config');
        if (res.ok) {
            const data = await res.json();
            const bannerTitle = document.getElementById('bannerTitle');
            const bannerDesc = document.getElementById('bannerDesc');
            const iamStatus = document.getElementById('iamStatusText');
            
            if (bannerTitle) bannerTitle.innerText = `Terhubung ke AWS (${data.region})`;
            if (bannerDesc) bannerDesc.innerText = `Tabel DynamoDB: ${data.dynamodb_table} | S3 Private: ${data.s3_bucket}`;
            if (iamStatus) iamStatus.innerText = 'Aktif (Auto-Auth)';
        }
    } catch (e) {
        console.warn('Could not fetch /api/config:', e);
    }
}

// ==========================================================================
// Data Fetching & DynamoDB Operations
// ==========================================================================
async function fetchInventoryData() {
    const refreshIcon = document.getElementById('refreshIcon');
    if (refreshIcon) refreshIcon.classList.add('fa-spin');

    document.getElementById('loadingState').style.display = 'flex';
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('gridContainer').innerHTML = '';
    document.getElementById('tableBody').innerHTML = '';

    try {
        const res = await fetch('/api/items');
        const json = await res.json();

        if (!json.success) {
            throw new Error(json.error || 'Gagal memuat data');
        }

        inventoryData = json.data || [];
        updateStats();
        renderInventory();
    } catch (err) {
        console.error('Fetch error:', err);
        showToast('Gagal memuat inventaris: ' + err.message, 'error');
        renderEmptyState('Gagal Terhubung ke DynamoDB', 'Pastikan IAM Role EC2 memiliki izin DynamoDB dan S3.');
    } finally {
        document.getElementById('loadingState').style.display = 'none';
        if (refreshIcon) refreshIcon.classList.remove('fa-spin');
    }
}

// ==========================================================================
// CRUD Actions: Create, Update, Delete
// ==========================================================================
async function handleItemFormSubmit(e) {
    e.preventDefault();

    const submitBtn = document.getElementById('btnSubmitItem');
    const submitText = document.getElementById('btnSubmitItemText');
    submitBtn.disabled = true;
    submitText.innerText = 'Menyimpan ke AWS...';

    try {
        const itemId = document.getElementById('itemId').value;
        const isEditing = Boolean(itemId);

        const formData = new FormData();
        formData.append('nama_barang', document.getElementById('itemName').value.trim());
        formData.append('kategori', document.getElementById('itemCategory').value);
        formData.append('kode_barang', document.getElementById('itemCode').value.trim());
        formData.append('lokasi', document.getElementById('itemLocation').value.trim());
        formData.append('jumlah', document.getElementById('itemQuantity').value);
        formData.append('kondisi', document.getElementById('itemCondition').value);
        formData.append('spesifikasi', document.getElementById('itemSpecs').value.trim());
        formData.append('keterangan', document.getElementById('itemNotes').value.trim());

        if (selectedPhotoFile) {
            formData.append('foto', selectedPhotoFile);
        }

        const url = isEditing ? `/api/items/${itemId}` : '/api/items';
        const method = isEditing ? 'PUT' : 'POST';

        const res = await fetch(url, {
            method: method,
            body: formData
        });

        const json = await res.json();

        if (!json.success) {
            throw new Error(json.error || json.message || 'Gagal memproses request');
        }

        showToast(json.message || 'Data berhasil disimpan!', 'success');
        closeItemModal();
        fetchInventoryData();
    } catch (err) {
        console.error('Save error:', err);
        showToast('Error: ' + err.message, 'error');
    } finally {
        submitBtn.disabled = false;
        submitText.innerText = 'Simpan Data';
    }
}

async function deleteItem(id) {
    if (!confirm('Apakah Anda yakin ingin menghapus barang ini dari DynamoDB dan S3?')) return;

    try {
        const res = await fetch(`/api/items/${id}`, {
            method: 'DELETE'
        });
        const json = await res.json();

        if (!json.success) {
            throw new Error(json.error || json.message || 'Gagal menghapus');
        }

        showToast(json.message || 'Barang berhasil dihapus!', 'success');
        fetchInventoryData();
    } catch (err) {
        console.error('Delete error:', err);
        showToast('Gagal menghapus: ' + err.message, 'error');
    }
}

// ==========================================================================
// Rendering & UI Management
// ==========================================================================
function renderInventory() {
    const gridContainer = document.getElementById('gridContainer');
    const tableBody = document.getElementById('tableBody');
    const tableContainer = document.getElementById('tableContainer');
    const emptyState = document.getElementById('emptyState');

    // Filter items
    const filtered = inventoryData.filter(item => {
        const matchesCategory = currentCategoryFilter === 'ALL' || item.kategori === currentCategoryFilter;
        const matchesCondition = currentConditionFilter === 'ALL' || item.kondisi === currentConditionFilter;
        
        const q = searchQuery.toLowerCase();
        const matchesSearch = !q || 
            (item.nama_barang && item.nama_barang.toLowerCase().includes(q)) ||
            (item.kode_barang && item.kode_barang.toLowerCase().includes(q)) ||
            (item.spesifikasi && item.spesifikasi.toLowerCase().includes(q)) ||
            (item.lokasi && item.lokasi.toLowerCase().includes(q)) ||
            (item.keterangan && item.keterangan.toLowerCase().includes(q));

        return matchesCategory && matchesCondition && matchesSearch;
    });

    if (filtered.length === 0) {
        gridContainer.innerHTML = '';
        tableBody.innerHTML = '';
        renderEmptyState('Tidak ada data ditemukan', 'Coba ubah kata kunci pencarian atau filter kategori.');
        return;
    }

    emptyState.style.display = 'none';

    if (currentViewMode === 'grid') {
        gridContainer.style.display = 'grid';
        tableContainer.style.display = 'none';
        renderGridView(filtered);
    } else {
        gridContainer.style.display = 'none';
        tableContainer.style.display = 'block';
        renderTableView(filtered);
    }
}

function renderGridView(items) {
    const container = document.getElementById('gridContainer');
    container.innerHTML = items.map(item => {
        const categoryIcon = getCategoryIcon(item.kategori);
        const conditionBadgeClass = getConditionBadgeClass(item.kondisi);
        const photoUrl = item.s3_key ? `/api/items/${item.id}/photo` : null;

        const imgHtml = photoUrl 
            ? `<img src="${photoUrl}" alt="${escapeHtml(item.nama_barang)}" class="item-image" onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\'item-image-fallback\'><i class=\'${categoryIcon}\'></i><span>Foto S3</span></div>'">`
            : `<div class="item-image-fallback"><i class="${categoryIcon}"></i><span>Tidak Ada Foto</span></div>`;

        return `
            <div class="item-card">
                <div class="item-image-wrapper" onclick="openDetailModal('${item.id}')">
                    ${imgHtml}
                    <span class="badge-condition ${conditionBadgeClass}">${escapeHtml(item.kondisi || 'Baik')}</span>
                    <span class="badge-category"><i class="${categoryIcon}"></i> ${escapeHtml(item.kategori || 'Lainnya')}</span>
                </div>
                <div class="item-content">
                    <div class="item-header">
                        <h4 class="item-title">${escapeHtml(item.nama_barang)}</h4>
                        <span class="item-code">${escapeHtml(item.kode_barang || '-')}</span>
                    </div>
                    <p class="item-specs">${escapeHtml(item.spesifikasi || item.keterangan || 'Tidak ada spesifikasi tambahan.')}</p>
                    
                    <div class="item-meta-grid">
                        <div class="meta-item">
                            <span class="meta-label">Stok Fisik</span>
                            <span class="meta-value text-cyan">${item.jumlah || 1} Unit</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">Lokasi Rak/Lab</span>
                            <span class="meta-value">${escapeHtml(item.lokasi || '-')}</span>
                        </div>
                    </div>

                    <div class="item-actions">
                        <button class="btn btn-secondary btn-xs" onclick="openDetailModal('${item.id}')">
                            <i class="fa-solid fa-eye"></i> Detail
                        </button>
                        <div class="flex gap-1">
                            <button class="btn btn-secondary btn-xs" onclick="openEditModal('${item.id}')" title="Edit Barang">
                                <i class="fa-solid fa-pen-to-square"></i>
                            </button>
                            <button class="btn btn-danger-subtle btn-xs" onclick="deleteItem('${item.id}')" title="Hapus Barang">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function renderTableView(items) {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = items.map(item => {
        const categoryIcon = getCategoryIcon(item.kategori);
        const conditionBadgeClass = getConditionBadgeClass(item.kondisi);
        const photoUrl = item.s3_key ? `/api/items/${item.id}/photo` : null;

        const imgHtml = photoUrl 
            ? `<img src="${photoUrl}" alt="Thumb" class="table-thumb">`
            : `<div class="table-thumb-fallback"><i class="${categoryIcon}"></i></div>`;

        return `
            <tr>
                <td>${imgHtml}</td>
                <td><span class="item-code">${escapeHtml(item.kode_barang || '-')}</span></td>
                <td>
                    <div class="font-bold text-white">${escapeHtml(item.nama_barang)}</div>
                    <small class="text-muted">${escapeHtml(item.spesifikasi || '-')}</small>
                </td>
                <td><span class="badge-category"><i class="${categoryIcon}"></i> ${escapeHtml(item.kategori || 'Lainnya')}</span></td>
                <td>${escapeHtml(item.lokasi || '-')}</td>
                <td><strong class="text-cyan">${item.jumlah || 1}</strong> Unit</td>
                <td><span class="badge-condition ${conditionBadgeClass}" style="position: static;">${escapeHtml(item.kondisi || 'Baik')}</span></td>
                <td>
                    <div class="flex gap-1">
                        <button class="btn btn-secondary btn-xs" onclick="openDetailModal('${item.id}')" title="Detail">
                            <i class="fa-solid fa-eye"></i>
                        </button>
                        <button class="btn btn-secondary btn-xs" onclick="openEditModal('${item.id}')" title="Edit">
                            <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                        <button class="btn btn-danger-subtle btn-xs" onclick="deleteItem('${item.id}')" title="Hapus">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function renderEmptyState(title, desc) {
    const empty = document.getElementById('emptyState');
    document.getElementById('emptyTitle').innerText = title;
    document.getElementById('emptyDesc').innerText = desc;
    empty.style.display = 'flex';
}

function updateStats() {
    let totalTypes = inventoryData.length;
    let totalUnits = 0;
    let goodUnits = 0;
    let damagedUnits = 0;

    inventoryData.forEach(item => {
        const qty = parseInt(item.jumlah, 10) || 1;
        totalUnits += qty;
        if (item.kondisi === 'Baik') {
            goodUnits += qty;
        } else if (item.kondisi === 'Rusak Berat' || item.kondisi === 'Rusak Ringan' || item.kondisi === 'Dalam Perbaikan') {
            damagedUnits += qty;
        }
    });

    document.getElementById('statTotalTypes').innerText = totalTypes;
    document.getElementById('statTotalUnits').innerText = totalUnits;
    document.getElementById('statGoodUnits').innerText = goodUnits;
    document.getElementById('statDamagedUnits').innerText = damagedUnits;
    document.getElementById('countAll').innerText = totalTypes;
}

// ==========================================================================
// Filter & Search Handlers
// ==========================================================================
function handleSearchFilter() {
    searchQuery = document.getElementById('searchInput').value.trim();
    currentCategoryFilter = document.getElementById('filterCategory').value;
    currentConditionFilter = document.getElementById('filterCondition').value;
    
    document.getElementById('clearSearchBtn').style.display = searchQuery ? 'block' : 'none';
    renderInventory();
}

function clearSearch() {
    document.getElementById('searchInput').value = '';
    handleSearchFilter();
}

function setChipCategory(category, buttonEl) {
    document.querySelectorAll('.category-chips .chip').forEach(c => c.classList.remove('active'));
    buttonEl.classList.add('active');
    document.getElementById('filterCategory').value = category;
    handleSearchFilter();
}

function setViewMode(mode) {
    currentViewMode = mode;
    document.getElementById('btnViewGrid').classList.toggle('active', mode === 'grid');
    document.getElementById('btnViewTable').classList.toggle('active', mode === 'table');
    renderInventory();
}

// ==========================================================================
// Modal Controllers
// ==========================================================================
function openAddModal() {
    document.getElementById('itemForm').reset();
    document.getElementById('itemId').value = '';
    document.getElementById('existingS3Key').value = '';
    document.getElementById('itemModalTitle').innerText = 'Tambah Barang Inventaris';
    document.getElementById('btnSubmitItemText').innerText = 'Simpan Data';
    
    removePhotoPreview();
    generateAssetCode();

    document.getElementById('itemModal').classList.add('active');
}

function openEditModal(itemId) {
    const item = inventoryData.find(i => i.id === itemId);
    if (!item) return;

    document.getElementById('itemId').value = item.id;
    document.getElementById('existingS3Key').value = item.s3_key || '';
    document.getElementById('itemName').value = item.nama_barang || '';
    document.getElementById('itemCategory').value = item.kategori || 'Router';
    document.getElementById('itemCode').value = item.kode_barang || '';
    document.getElementById('itemLocation').value = item.lokasi || '';
    document.getElementById('itemQuantity').value = item.jumlah || 1;
    document.getElementById('itemCondition').value = item.kondisi || 'Baik';
    document.getElementById('itemSpecs').value = item.spesifikasi || '';
    document.getElementById('itemNotes').value = item.keterangan || '';

    document.getElementById('itemModalTitle').innerText = 'Edit Data Barang';
    document.getElementById('btnSubmitItemText').innerText = 'Perbarui Data';

    if (item.s3_key) {
        showPhotoPreview(`/api/items/${item.id}/photo`);
    } else {
        removePhotoPreview();
    }

    document.getElementById('itemModal').classList.add('active');
}

function closeItemModal() {
    document.getElementById('itemModal').classList.remove('active');
}

function openDetailModal(itemId) {
    const item = inventoryData.find(i => i.id === itemId);
    if (!item) return;

    document.getElementById('detailItemTitle').innerText = item.nama_barang;
    document.getElementById('detailItemCode').innerText = `Kode Aset: ${item.kode_barang || '-'}`;
    document.getElementById('detailCategory').innerText = item.kategori || '-';
    document.getElementById('detailCondition').innerHTML = `<span class="badge-condition ${getConditionBadgeClass(item.kondisi)}" style="position: static;">${item.kondisi}</span>`;
    document.getElementById('detailQuantity').innerText = `${item.jumlah || 1} Unit`;
    document.getElementById('detailLocation').innerText = item.lokasi || '-';
    document.getElementById('detailSpecs').innerText = item.spesifikasi || '-';
    document.getElementById('detailNotes').innerText = item.keterangan || '-';
    document.getElementById('detailId').innerText = item.id;

    const detailImg = document.getElementById('detailImg');
    const categoryIcon = getCategoryIcon(item.kategori);

    if (item.s3_key) {
        detailImg.src = `/api/items/${item.id}/photo`;
        detailImg.style.display = 'block';
    } else {
        detailImg.style.display = 'none';
        document.getElementById('detailImgWrapper').innerHTML = `<div class="item-image-fallback" style="height: 100%;"><i class="${categoryIcon}"></i><span>Tidak Ada Foto</span></div>`;
    }

    document.getElementById('btnEditFromDetail').onclick = () => {
        closeDetailModal();
        openEditModal(item.id);
    };

    document.getElementById('detailModal').classList.add('active');
}

function closeDetailModal() {
    document.getElementById('detailModal').classList.remove('active');
}

// ==========================================================================
// Photo Upload & Preview
// ==========================================================================
function handlePhotoSelect(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
        showToast('Ukuran foto terlalu besar! Maksimal 10MB.', 'error');
        return;
    }

    selectedPhotoFile = file;
    const reader = new FileReader();
    reader.onload = function(evt) {
        showPhotoPreview(evt.target.result);
    };
    reader.readAsDataURL(file);
}

function showPhotoPreview(srcUrl) {
    const preview = document.getElementById('imagePreview');
    const placeholder = document.getElementById('uploadPlaceholder');
    const removeBtn = document.getElementById('btnRemovePhoto');

    preview.src = srcUrl;
    preview.style.display = 'block';
    placeholder.style.display = 'none';
    removeBtn.style.display = 'inline-flex';
}

function removePhotoPreview() {
    selectedPhotoFile = null;
    document.getElementById('photoInput').value = '';
    document.getElementById('imagePreview').src = '';
    document.getElementById('imagePreview').style.display = 'none';
    document.getElementById('uploadPlaceholder').style.display = 'flex';
    document.getElementById('btnRemovePhoto').style.display = 'none';
}

function setupDragAndDrop() {
    const box = document.getElementById('photoPreviewBox');
    if (!box) return;

    ['dragenter', 'dragover'].forEach(name => {
        box.addEventListener(name, (e) => {
            e.preventDefault();
            box.style.borderColor = '#06b6d4';
        }, false);
    });

    ['dragleave', 'drop'].forEach(name => {
        box.addEventListener(name, (e) => {
            e.preventDefault();
            box.style.borderColor = 'rgba(51, 65, 85, 0.6)';
        }, false);
    });

    box.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) {
            document.getElementById('photoInput').files = files;
            handlePhotoSelect({ target: { files } });
        }
    }, false);
}

// ==========================================================================
// Utilities & Helpers
// ==========================================================================
function generateAssetCode() {
    const category = document.getElementById('itemCategory').value;
    let prefix = 'TKJ';
    switch (category) {
        case 'Router': prefix = 'TKJ-RTR'; break;
        case 'Switch': prefix = 'TKJ-SW'; break;
        case 'Server': prefix = 'TKJ-SRV'; break;
        case 'AccessPoint': prefix = 'TKJ-AP'; break;
        case 'Tool': prefix = 'TKJ-TOOL'; break;
        case 'Kabel': prefix = 'TKJ-CBL'; break;
        case 'Sparepart': prefix = 'TKJ-PRT'; break;
        default: prefix = 'TKJ-GEN';
    }
    const rand = Math.floor(100 + Math.random() * 900);
    document.getElementById('itemCode').value = `${prefix}-${rand}`;
}

function getCategoryIcon(cat) {
    switch (cat) {
        case 'Router': return 'fa-solid fa-network-wired';
        case 'Switch': return 'fa-solid fa-arrows-split-up-and-left';
        case 'Server': return 'fa-solid fa-server';
        case 'AccessPoint': return 'fa-solid fa-wifi';
        case 'Tool': return 'fa-solid fa-screwdriver-wrench';
        case 'Kabel': return 'fa-solid fa-ethernet';
        case 'Sparepart': return 'fa-solid fa-microchip';
        default: return 'fa-solid fa-box-archive';
    }
}

function getConditionBadgeClass(cond) {
    switch (cond) {
        case 'Baik': return 'badge-baik';
        case 'Rusak Ringan': return 'badge-rusak-ringan';
        case 'Rusak Berat': return 'badge-rusak-berat';
        case 'Dalam Perbaikan': return 'badge-perbaikan';
        case 'Dipinjam': return 'badge-dipinjam';
        default: return 'badge-baik';
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function exportToCSV() {
    if (inventoryData.length === 0) {
        showToast('Tidak ada data inventaris untuk diexport.', 'info');
        return;
    }

    const headers = ['ID', 'Kode Aset', 'Nama Barang', 'Kategori', 'Lokasi', 'Jumlah', 'Kondisi', 'Spesifikasi', 'Keterangan', 'Created At'];
    const rows = inventoryData.map(item => [
        `"${item.id || ''}"`,
        `"${(item.kode_barang || '').replace(/"/g, '""')}"`,
        `"${(item.nama_barang || '').replace(/"/g, '""')}"`,
        `"${(item.kategori || '').replace(/"/g, '""')}"`,
        `"${(item.lokasi || '').replace(/"/g, '""')}"`,
        item.jumlah || 1,
        `"${(item.kondisi || '').replace(/"/g, '""')}"`,
        `"${(item.spesifikasi || '').replace(/"/g, '""')}"`,
        `"${(item.keterangan || '').replace(/"/g, '""')}"`,
        `"${(item.created_at || '').replace(/"/g, '""')}"`
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `Inventaris_TKJ_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast('File CSV berhasil diunduh!', 'success');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'fa-solid fa-circle-info';
    if (type === 'success') icon = 'fa-solid fa-circle-check';
    if (type === 'error') icon = 'fa-solid fa-triangle-exclamation';

    toast.innerHTML = `<i class="${icon}"></i> <span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
