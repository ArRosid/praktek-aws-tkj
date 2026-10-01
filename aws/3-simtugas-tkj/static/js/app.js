/**
 * SIMTUGAS TKJ - Frontend JavaScript
 * Mengelola flow reaktif: Guru tambah kelas -> Guru tambah siswa -> Siswa kumpul tugas (PDF)
 */

document.addEventListener("DOMContentLoaded", () => {
    // State aplikasi
    let allKelas = [];
    let currentSiswaList = [];

    // --- ELEMENTS ---
    // Tabs
    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabPanels = document.querySelectorAll(".tab-panel");

    // Siswa Form
    const formKumpulTugas = document.getElementById("form-kumpul-tugas");
    const selectKelasSiswa = document.getElementById("select-kelas-siswa");
    const selectSiswa = document.getElementById("select-siswa");
    const fileInput = document.getElementById("file-tugas");
    const dropzone = document.getElementById("dropzone");
    const selectedFileInfo = document.getElementById("selected-file-info");
    const btnSubmitTugas = document.getElementById("btn-submit-tugas");

    // Rekap Table & Filters
    const filterKelasRekap = document.getElementById("filter-kelas-rekap");
    const btnRefreshRekap = document.getElementById("btn-refresh-rekap");
    const tugasTableBody = document.getElementById("tugas-table-body");
    const counterTugas = document.getElementById("counter-tugas");

    // Kelola Guru (Kelas & Siswa)
    const formTambahKelas = document.getElementById("form-tambah-kelas");
    const namaKelasInput = document.getElementById("nama-kelas");
    const jurusanKelasInput = document.getElementById("jurusan-kelas");
    const listKelasContainer = document.getElementById("list-kelas-container");

    const formTambahSiswa = document.getElementById("form-tambah-siswa");
    const selectKelasTambahSiswa = document.getElementById("select-kelas-tambah-siswa");
    const namaSiswaInput = document.getElementById("nama-siswa-input");
    const nisSiswaInput = document.getElementById("nis-siswa-input");
    const filterSiswaByKelas = document.getElementById("filter-siswa-by-kelas");
    const listSiswaContainer = document.getElementById("list-siswa-container");

    // Badges
    const badgeDynamoDB = document.getElementById("badge-dynamodb");
    const badgeS3 = document.getElementById("badge-s3");


    // =========================================================================
    // 1. NOTIFIKASI TOAST
    // =========================================================================
    function showToast(message, type = "info") {
        const container = document.getElementById("toast-container");
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `<div>${message}</div>`;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateX(100%)";
            toast.style.transition = "all 0.3s ease";
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }


    // =========================================================================
    // 2. TAB NAVIGATION
    // =========================================================================
    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetId = btn.dataset.tab;

            tabButtons.forEach(b => b.classList.remove("active"));
            tabPanels.forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            const targetPanel = document.getElementById(targetId);
            if (targetPanel) targetPanel.classList.add("active");

            // Refresh data saat tab dibuka
            if (targetId === "tab-rekap") {
                loadTugasList();
            } else if (targetId === "tab-kelola") {
                loadKelasList();
                loadSiswaList();
            }
        });
    });


    // =========================================================================
    // 3. LOAD CONFIG AWS
    // =========================================================================
    async function loadConfig() {
        try {
            const res = await fetch("/api/config");
            const data = await res.json();
            if (data.success) {
                if (badgeDynamoDB) badgeDynamoDB.textContent = data.dynamodb_table;
                if (badgeS3) badgeS3.textContent = data.s3_bucket;
            }
        } catch (err) {
            console.warn("Gagal memuat config:", err);
        }
    }


    // =========================================================================
    // 4. KELOLA DATA KELAS
    // =========================================================================
    async function loadKelasList() {
        try {
            const res = await fetch("/api/kelas");
            const result = await res.json();

            if (!result.success) {
                showToast("Gagal memuat data kelas: " + result.error, "error");
                return;
            }

            allKelas = result.data || [];
            renderKelasDropdowns();
            renderKelasCards();
        } catch (err) {
            console.error(err);
            showToast("Koneksi gagal ke server", "error");
        }
    }

    function renderKelasDropdowns() {
        // Dropdown di Form Kumpul Siswa
        selectKelasSiswa.innerHTML = `<option value="">-- Pilih Kelas Anda --</option>`;
        // Dropdown di Form Tambah Siswa Guru
        selectKelasTambahSiswa.innerHTML = `<option value="">-- Pilih Kelas --</option>`;
        // Filter di Tab Rekap
        filterKelasRekap.innerHTML = `<option value="">Semua Kelas</option>`;
        // Filter di Tab Kelola Siswa
        filterSiswaByKelas.innerHTML = `<option value="">Semua Kelas</option>`;

        allKelas.forEach(k => {
            const opt1 = new Option(k.nama_kelas, k.id);
            const opt2 = new Option(k.nama_kelas, k.id);
            const opt3 = new Option(k.nama_kelas, k.id);
            const opt4 = new Option(k.nama_kelas, k.id);

            selectKelasSiswa.add(opt1);
            selectKelasTambahSiswa.add(opt2);
            filterKelasRekap.add(opt3);
            filterSiswaByKelas.add(opt4);
        });
    }

    function renderKelasCards() {
        if (!listKelasContainer) return;
        if (allKelas.length === 0) {
            listKelasContainer.innerHTML = `<div class="empty-state">Belum ada kelas yang dibuat. Silakan tambahkan di form atas.</div>`;
            return;
        }

        listKelasContainer.innerHTML = allKelas.map(k => `
            <div class="list-item">
                <div>
                    <div class="list-item-title">${escapeHtml(k.nama_kelas)}</div>
                    <div class="list-item-sub">${escapeHtml(k.jurusan || 'TKJ')} &bull; <span style="font-family: var(--font-mono); font-size: 0.72rem;">${k.id}</span></div>
                </div>
                <button class="btn btn-danger btn-sm btn-hapus-kelas" data-id="${k.id}" title="Hapus Kelas">
                    Hapus
                </button>
            </div>
        `).join("");

        // Attach listener tombol hapus kelas
        listKelasContainer.querySelectorAll(".btn-hapus-kelas").forEach(btn => {
            btn.addEventListener("click", async () => {
                const id = btn.dataset.id;
                if (!confirm("Apakah yakin ingin menghapus kelas ini?")) return;

                try {
                    const res = await fetch(`/api/kelas/${id}`, { method: "DELETE" });
                    const resJson = await res.json();
                    if (resJson.success) {
                        showToast(resJson.message, "success");
                        loadKelasList();
                    } else {
                        showToast("Gagal: " + resJson.error, "error");
                    }
                } catch (e) {
                    showToast("Terjadi kesalahan jaringan", "error");
                }
            });
        });
    }

    // Submit Tambah Kelas
    if (formTambahKelas) {
        formTambahKelas.addEventListener("submit", async (e) => {
            e.preventDefault();
            const nama = namaKelasInput.value.trim();
            const jurusan = jurusanKelasInput.value.trim();

            if (!nama) return;

            try {
                const res = await fetch("/api/kelas", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ nama_kelas: nama, jurusan: jurusan })
                });
                const result = await res.json();
                if (result.success) {
                    showToast(result.message, "success");
                    namaKelasInput.value = "";
                    loadKelasList();
                } else {
                    showToast("Gagal menambah kelas: " + (result.message || result.error), "error");
                }
            } catch (err) {
                showToast("Gagal menghubungi server", "error");
            }
        });
    }


    // =========================================================================
    // 5. KELOLA DATA SISWA
    // =========================================================================
    async function loadSiswaList(filterKelasId = "") {
        try {
            const url = filterKelasId ? `/api/siswa?kelas_id=${encodeURIComponent(filterKelasId)}` : "/api/siswa";
            const res = await fetch(url);
            const result = await res.json();

            if (!result.success) {
                showToast("Gagal memuat siswa: " + result.error, "error");
                return;
            }

            currentSiswaList = result.data || [];
            renderSiswaCards();
        } catch (err) {
            console.error(err);
        }
    }

    function renderSiswaCards() {
        if (!listSiswaContainer) return;
        if (currentSiswaList.length === 0) {
            listSiswaContainer.innerHTML = `<div class="empty-state">Belum ada data siswa untuk kelas ini.</div>`;
            return;
        }

        listSiswaContainer.innerHTML = currentSiswaList.map(s => `
            <div class="list-item">
                <div>
                    <div class="list-item-title">${escapeHtml(s.nama_siswa)}</div>
                    <div class="list-item-sub">
                        <span class="badge-tag">${escapeHtml(s.nama_kelas || 'Kelas')}</span> 
                        &bull; NIS: ${escapeHtml(s.nis || '-')}
                    </div>
                </div>
                <button class="btn btn-danger btn-sm btn-hapus-siswa" data-id="${s.id}" title="Hapus Siswa">
                    Hapus
                </button>
            </div>
        `).join("");

        // Attach listener tombol hapus siswa
        listSiswaContainer.querySelectorAll(".btn-hapus-siswa").forEach(btn => {
            btn.addEventListener("click", async () => {
                const id = btn.dataset.id;
                if (!confirm("Apakah yakin ingin menghapus data siswa ini?")) return;

                try {
                    const res = await fetch(`/api/siswa/${id}`, { method: "DELETE" });
                    const resJson = await res.json();
                    if (resJson.success) {
                        showToast(resJson.message, "success");
                        loadSiswaList(filterSiswaByKelas ? filterSiswaByKelas.value : "");
                    } else {
                        showToast("Gagal: " + resJson.error, "error");
                    }
                } catch (e) {
                    showToast("Terjadi kesalahan jaringan", "error");
                }
            });
        });
    }

    // Submit Tambah Siswa
    if (formTambahSiswa) {
        formTambahSiswa.addEventListener("submit", async (e) => {
            e.preventDefault();
            const kelasId = selectKelasTambahSiswa.value;
            const namaSiswa = namaSiswaInput.value.trim();
            const nis = nisSiswaInput.value.trim();

            if (!kelasId || !namaSiswa) {
                showToast("Pilih kelas dan isi nama siswa!", "error");
                return;
            }

            try {
                const res = await fetch("/api/siswa", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ kelas_id: kelasId, nama_siswa: namaSiswa, nis: nis })
                });
                const result = await res.json();
                if (result.success) {
                    showToast(result.message, "success");
                    namaSiswaInput.value = "";
                    nisSiswaInput.value = "";
                    loadSiswaList(filterSiswaByKelas ? filterSiswaByKelas.value : "");
                } else {
                    showToast("Gagal: " + (result.message || result.error), "error");
                }
            } catch (err) {
                showToast("Gagal menghubungi server", "error");
            }
        });
    }

    // Filter siswa di panel guru
    if (filterSiswaByKelas) {
        filterSiswaByKelas.addEventListener("change", () => {
            loadSiswaList(filterSiswaByKelas.value);
        });
    }


    // =========================================================================
    // 6. FORM SISWA: REAKTIF PILIH KELAS -> PILIH SISWA
    // =========================================================================
    if (selectKelasSiswa) {
        selectKelasSiswa.addEventListener("change", async () => {
            const kelasId = selectKelasSiswa.value;

            if (!kelasId) {
                selectSiswa.innerHTML = `<option value="">-- Pilih kelas terlebih dahulu --</option>`;
                selectSiswa.disabled = true;
                return;
            }

            selectSiswa.disabled = true;
            selectSiswa.innerHTML = `<option value="">Memuat siswa...</option>`;

            try {
                const res = await fetch(`/api/siswa?kelas_id=${encodeURIComponent(kelasId)}`);
                const result = await res.json();

                if (result.success && result.data.length > 0) {
                    selectSiswa.innerHTML = `<option value="">-- Pilih Nama Anda --</option>`;
                    result.data.forEach(s => {
                        const label = s.nis && s.nis !== "-" ? `${s.nama_siswa} (${s.nis})` : s.nama_siswa;
                        selectSiswa.add(new Option(label, s.id));
                    });
                    selectSiswa.disabled = false;
                } else {
                    selectSiswa.innerHTML = `<option value="">(Belum ada siswa di kelas ini. Harap lapor guru)</option>`;
                    selectSiswa.disabled = true;
                }
            } catch (err) {
                selectSiswa.innerHTML = `<option value="">Gagal memuat siswa</option>`;
            }
        });
    }


    // =========================================================================
    // 7. FILE UPLOAD & DROPZONE HANDLING
    // =========================================================================
    if (dropzone && fileInput) {
        // Drag & drop visual effects
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('dragover');
            });
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files && files.length > 0) {
                fileInput.files = files;
                handleFileSelect(files[0]);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files && fileInput.files.length > 0) {
                handleFileSelect(fileInput.files[0]);
            }
        });
    }

    function handleFileSelect(file) {
        if (!file) return;

        // Validasi ekstensi PDF
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showToast("Harap pilih file dengan format PDF (.pdf)!", "error");
            fileInput.value = "";
            selectedFileInfo.classList.add("hidden");
            return;
        }

        // Tampilkan info file
        const sizeKB = (file.size / 1024).toFixed(1);
        const displaySize = sizeKB > 1024 ? `${(sizeKB / 1024).toFixed(2)} MB` : `${sizeKB} KB`;

        selectedFileInfo.querySelector(".file-name").textContent = file.name;
        selectedFileInfo.querySelector(".file-size").textContent = `(${displaySize})`;
        selectedFileInfo.classList.remove("hidden");
    }


    // =========================================================================
    // 8. SUBMIT PENGUMPULAN TUGAS (UPLOAD KE S3 & DYNAMODB)
    // =========================================================================
    if (formKumpulTugas) {
        formKumpulTugas.addEventListener("submit", async (e) => {
            e.preventDefault();

            const kelasId = selectKelasSiswa.value;
            const siswaId = selectSiswa.value;
            const judul = document.getElementById("input-judul-tugas").value.trim();
            const catatan = document.getElementById("input-catatan").value.trim();
            const file = fileInput.files[0];

            if (!kelasId || !siswaId) {
                showToast("Pilih kelas dan nama siswa terlebih dahulu!", "error");
                return;
            }
            if (!file) {
                showToast("Lampirkan file PDF tugas!", "error");
                return;
            }

            // Set loading state
            btnSubmitTugas.disabled = true;
            btnSubmitTugas.querySelector(".btn-text").textContent = "Mengunggah PDF ke S3...";

            const formData = new FormData();
            formData.append("kelas_id", kelasId);
            formData.append("siswa_id", siswaId);
            formData.append("judul_tugas", judul);
            formData.append("catatan", catatan);
            formData.append("file_tugas", file);

            try {
                const res = await fetch("/api/tugas", {
                    method: "POST",
                    body: formData
                });
                const result = await res.json();

                if (result.success) {
                    showToast("🎉 " + result.message, "success");
                    formKumpulTugas.reset();
                    selectSiswa.innerHTML = `<option value="">-- Pilih kelas terlebih dahulu --</option>`;
                    selectSiswa.disabled = true;
                    selectedFileInfo.classList.add("hidden");

                    // Refresh counter & rekap
                    loadTugasList();
                } else {
                    showToast("Gagal mengumpulkan: " + (result.message || result.error), "error");
                }
            } catch (err) {
                showToast("Gagal mengirim file ke server", "error");
            } finally {
                btnSubmitTugas.disabled = false;
                btnSubmitTugas.querySelector(".btn-text").textContent = "Kumpulkan Tugas Sekarang 🚀";
            }
        });
    }


    // =========================================================================
    // 9. REKAP TUGAS MASUK (TAB GURU)
    // =========================================================================
    async function loadTugasList() {
        if (!tugasTableBody) return;

        const filterKelasId = filterKelasRekap ? filterKelasRekap.value : "";
        const url = filterKelasId ? `/api/tugas?kelas_id=${encodeURIComponent(filterKelasId)}` : "/api/tugas";

        tugasTableBody.innerHTML = `<tr><td colspan="6" class="text-center loading-cell">Memuat data tugas dari DynamoDB...</td></tr>`;

        try {
            const res = await fetch(url);
            const result = await res.json();

            if (!result.success) {
                tugasTableBody.innerHTML = `<tr><td colspan="6" class="text-center empty-cell text-danger">Error: ${result.error}</td></tr>`;
                return;
            }

            const tugasList = result.data || [];
            if (counterTugas) counterTugas.textContent = tugasList.length;

            if (tugasList.length === 0) {
                tugasTableBody.innerHTML = `<tr><td colspan="6" class="text-center empty-cell">Belum ada siswa yang mengumpulkan tugas.</td></tr>`;
                return;
            }

            tugasTableBody.innerHTML = tugasList.map((t, idx) => {
                const dateObj = new Date(t.created_at);
                const formattedDate = dateObj.toLocaleString("id-ID", {
                    day: "numeric",
                    month: "short",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit"
                });

                return `
                    <tr>
                        <td class="time-cell">${formattedDate}</td>
                        <td><span class="badge-tag">${escapeHtml(t.nama_kelas || 'Kelas')}</span></td>
                        <td><strong>${escapeHtml(t.nama_siswa || 'Siswa')}</strong></td>
                        <td>
                            <div style="font-weight: 600;">${escapeHtml(t.judul_tugas || '-')}</div>
                            ${t.catatan && t.catatan !== '-' ? `<div style="font-size: 0.78rem; color: var(--text-dim); margin-top: 2px;">Catatan: ${escapeHtml(t.catatan)}</div>` : ''}
                        </td>
                        <td>
                            <div class="badge-pdf">
                                <span>📄 PDF</span>
                                <span>(${t.file_size || 'N/A'})</span>
                            </div>
                        </td>
                        <td>
                            <div style="display: flex; gap: 0.4rem; align-items: center;">
                                <a href="/api/tugas/${t.id}/file" target="_blank" class="btn btn-secondary btn-sm" title="Lihat/Preview PDF">
                                    Buka
                                </a>
                                <a href="/api/tugas/${t.id}/file?download=true" class="btn btn-secondary btn-sm" title="Download PDF">
                                    Unduh
                                </a>
                                <button class="btn btn-danger btn-sm btn-hapus-tugas" data-id="${t.id}" title="Hapus Tugas">
                                    🗑️
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            }).join("");

            // Listener hapus tugas
            tugasTableBody.querySelectorAll(".btn-hapus-tugas").forEach(btn => {
                btn.addEventListener("click", async () => {
                    const id = btn.dataset.id;
                    if (!confirm("Hapus berkas tugas ini dari DynamoDB dan S3?")) return;

                    try {
                        const delRes = await fetch(`/api/tugas/${id}`, { method: "DELETE" });
                        const delJson = await delRes.json();
                        if (delJson.success) {
                            showToast(delJson.message, "success");
                            loadTugasList();
                        } else {
                            showToast("Gagal: " + delJson.error, "error");
                        }
                    } catch (e) {
                        showToast("Terjadi kesalahan jaringan", "error");
                    }
                });
            });

        } catch (err) {
            console.error(err);
            tugasTableBody.innerHTML = `<tr><td colspan="6" class="text-center empty-cell text-danger">Gagal menghubungi server</td></tr>`;
        }
    }

    if (filterKelasRekap) {
        filterKelasRekap.addEventListener("change", loadTugasList);
    }

    if (btnRefreshRekap) {
        btnRefreshRekap.addEventListener("click", () => {
            loadTugasList();
            showToast("Data tugas disegarkan", "info");
        });
    }


    // Helper XSS prevention
    function escapeHtml(text) {
        if (!text) return "";
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }


    // =========================================================================
    // INITIALIZATION
    // =========================================================================
    loadConfig();
    loadKelasList();
    loadTugasList();
    loadSiswaList();
});
