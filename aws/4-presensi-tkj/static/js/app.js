/**
 * SIMPRES TKJ - Client-side Logic (English Localization)
 * Interfaces with Flask REST API + AWS DynamoDB + AWS S3 Private Storage
 */

document.addEventListener("DOMContentLoaded", () => {
    // State Store
    const state = {
        config: null,
        kelasList: [],
        siswaList: [],
        presensiList: [],
        activePhotoBlob: null,
        activePhotoFile: null,
        cameraStream: null
    };

    // DOM Elements Cache
    const elements = {
        // Badges & Stats
        badgeDynamo: document.getElementById("badge-dynamodb"),
        badgeS3: document.getElementById("badge-s3"),
        badgeAuth: document.getElementById("badge-auth"),
        badgeCandidateName: document.getElementById("badge-candidate-name"),
        statTotalSiswa: document.getElementById("stat-total-siswa"),
        statHadir: document.getElementById("stat-hadir-today"),
        statIzin: document.getElementById("stat-izin-today"),
        statSakit: document.getElementById("stat-sakit-today"),
        counterPresensi: document.getElementById("counter-presensi"),

        // Tabs
        tabBtns: document.querySelectorAll(".tab-btn"),
        tabPanels: document.querySelectorAll(".tab-panel"),

        // Form Presensi
        formPresensi: document.getElementById("form-presensi"),
        selectPresensiKelas: document.getElementById("presensi-kelas"),
        selectPresensiSiswa: document.getElementById("presensi-siswa"),
        statusRadios: document.querySelectorAll('input[name="status"]'),
        inputKeterangan: document.getElementById("presensi-keterangan"),
        fotoLabelText: document.getElementById("foto-label-text"),
        btnSubmitPresensi: document.getElementById("btn-submit-presensi"),

        // Photo Mode & Camera
        btnModeCamera: document.getElementById("btn-mode-camera"),
        btnModeUpload: document.getElementById("btn-mode-upload"),
        cameraSection: document.getElementById("camera-section"),
        uploadSection: document.getElementById("upload-section"),
        videoStream: document.getElementById("camera-stream"),
        cameraCanvas: document.getElementById("camera-canvas"),
        cameraPlaceholder: document.getElementById("camera-placeholder"),
        btnStartCamera: document.getElementById("btn-start-camera"),
        btnCaptureCamera: document.getElementById("btn-capture-camera"),
        btnRetakeCamera: document.getElementById("btn-retake-camera"),

        // Dropzone & Preview
        fotoDropzone: document.getElementById("foto-dropzone"),
        fotoInput: document.getElementById("foto-input"),
        previewContainer: document.getElementById("preview-container"),
        previewImage: document.getElementById("preview-image"),
        previewFilename: document.getElementById("preview-filename"),
        previewSize: document.getElementById("preview-size"),
        btnCancelPreview: document.getElementById("btn-cancel-preview"),

        // Rekap & Filter
        filterKelas: document.getElementById("filter-kelas"),
        filterTanggal: document.getElementById("filter-tanggal"),
        filterStatus: document.getElementById("filter-status"),
        btnResetFilter: document.getElementById("btn-reset-filter"),
        btnRefreshRekap: document.getElementById("btn-refresh-rekap"),
        presensiTableBody: document.getElementById("presensi-table-body"),

        // Kelola
        formTambahKelas: document.getElementById("form-tambah-kelas"),
        inputNamaKelas: document.getElementById("input-nama-kelas"),
        inputJurusan: document.getElementById("input-jurusan"),
        listKelasContainer: document.getElementById("list-kelas-container"),

        formTambahSiswa: document.getElementById("form-tambah-siswa"),
        siswaSelectKelas: document.getElementById("siswa-select-kelas"),
        inputNis: document.getElementById("input-nis"),
        inputNamaSiswa: document.getElementById("input-nama-siswa"),
        filterManageSiswaKelas: document.getElementById("filter-manage-siswa-kelas"),
        listSiswaContainer: document.getElementById("list-siswa-container"),

        // Modal
        photoModal: document.getElementById("photo-modal"),
        modalPhotoImg: document.getElementById("modal-photo-img"),
        modalPhotoTitle: document.getElementById("modal-photo-title"),
        modalPhotoDesc: document.getElementById("modal-photo-desc"),
        btnDownloadModalPhoto: document.getElementById("btn-download-modal-photo"),
        btnCloseModal: document.getElementById("btn-close-modal"),

        // Toast
        toastContainer: document.getElementById("toast-container")
    };

    // =========================================================================
    // INITIALIZATION
    // =========================================================================
    async function init() {
        setupTabNavigation();
        setupStatusRadioEvents();
        setupPhotoMode();
        setupCamera();
        setupDropzone();
        setupFormPresensi();
        setupFilters();
        setupManageForms();
        setupModal();

        // Load data from API
        await loadConfig();
        await loadKelas();
        await loadSiswa();
        await loadStats();
        await loadPresensi();
    }

    // =========================================================================
    // API CALLS
    // =========================================================================

    async function loadConfig() {
        try {
            const res = await fetch("/api/config");
            const data = await res.json();
            if (data.success) {
                state.config = data;
                elements.badgeDynamo.textContent = data.dynamodb_table;
                elements.badgeS3.textContent = data.s3_bucket;
                elements.badgeAuth.textContent = data.auth_method;

                if (data.your_name_set) {
                    elements.badgeCandidateName.textContent = data.your_name;
                }
            }
        } catch (err) {
            console.error("Failed to load AWS configuration:", err);
        }
    }

    async function loadStats() {
        try {
            const res = await fetch("/api/stats");
            const resData = await res.json();
            if (resData.success && resData.data) {
                const s = resData.data;
                elements.statTotalSiswa.textContent = s.total_siswa;
                elements.statHadir.textContent = s.hadir_hari_ini;
                elements.statIzin.textContent = s.izin_hari_ini;
                elements.statSakit.textContent = s.sakit_hari_ini;
            }
        } catch (err) {
            console.error("Failed to load statistics:", err);
        }
    }

    async function loadKelas() {
        try {
            const res = await fetch("/api/kelas");
            const resData = await res.json();
            if (resData.success) {
                state.kelasList = resData.data;
                renderKelasDropdowns();
                renderManageKelasList();
            }
        } catch (err) {
            console.error("Failed to load classes:", err);
            showToast("Failed to load classes from DynamoDB", "error");
        }
    }

    async function loadSiswa(kelasId = "") {
        try {
            let url = "/api/siswa";
            if (kelasId) url += `?kelas_id=${encodeURIComponent(kelasId)}`;
            const res = await fetch(url);
            const resData = await res.json();
            if (resData.success) {
                state.siswaList = resData.data;
                renderManageSiswaList();
            }
        } catch (err) {
            console.error("Failed to load students:", err);
        }
    }

    async function loadPresensi() {
        try {
            const params = new URLSearchParams();
            if (elements.filterKelas.value) params.append("kelas_id", elements.filterKelas.value);
            if (elements.filterTanggal.value) params.append("tanggal", elements.filterTanggal.value);
            if (elements.filterStatus.value) params.append("status", elements.filterStatus.value);

            const url = "/api/presensi" + (params.toString() ? "?" + params.toString() : "");
            const res = await fetch(url);
            const resData = await res.json();
            if (resData.success) {
                state.presensiList = resData.data;
                elements.counterPresensi.textContent = state.presensiList.length;
                renderPresensiTable();
            }
        } catch (err) {
            console.error("Failed to load attendance records:", err);
            showToast("Failed to load attendance records", "error");
        }
    }

    // =========================================================================
    // RENDERING HELPERS
    // =========================================================================

    function renderKelasDropdowns() {
        const optionsHtml = state.kelasList.map(k => 
            `<option value="${k.id}">${escapeHtml(k.nama_kelas)}</option>`
        ).join("");

        // Dropdown Presensi Form
        elements.selectPresensiKelas.innerHTML = 
            '<option value="">-- Choose Your Class --</option>' + optionsHtml;

        // Dropdown Add Student Form
        elements.siswaSelectKelas.innerHTML = 
            '<option value="">-- Select Class --</option>' + optionsHtml;

        // Dropdown Filter Logs
        elements.filterKelas.innerHTML = 
            '<option value="">All Classes</option>' + optionsHtml;

        // Dropdown Filter Manage Students
        elements.filterManageSiswaKelas.innerHTML = 
            '<option value="">All Classes</option>' + optionsHtml;
    }

    function renderPresensiTable() {
        if (!state.presensiList || state.presensiList.length === 0) {
            elements.presensiTableBody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center py-4 text-muted">
                        No attendance records found matching current filters.
                    </td>
                </tr>
            `;
            return;
        }

        elements.presensiTableBody.innerHTML = state.presensiList.map(item => {
            const photoUrl = `/api/presensi/${item.id}/foto`;
            let badgeClass = "badge-hadir";
            const normStatus = (item.status === "Present" || item.status === "Hadir") ? "Present"
                : (item.status === "Excused" || item.status === "Izin") ? "Excused" : "Sick";

            if (normStatus === "Excused") badgeClass = "badge-izin";
            if (normStatus === "Sick") badgeClass = "badge-sakit";

            return `
                <tr>
                    <td>
                        <img src="${photoUrl}" alt="Photo ${escapeHtml(item.nama_siswa)}" 
                             class="thumb-preview" 
                             data-presensi-id="${item.id}"
                             data-nama="${escapeHtml(item.nama_siswa)}"
                             data-status="${escapeHtml(normStatus)}"
                             data-waktu="${escapeHtml(item.tanggal)} ${escapeHtml(item.waktu)}"
                             title="Click to view full photo">
                    </td>
                    <td>
                        <div><strong>${escapeHtml(item.tanggal)}</strong></div>
                        <small class="text-muted">${escapeHtml(item.waktu)}</small>
                    </td>
                    <td>
                        <div><strong>${escapeHtml(item.nama_siswa)}</strong></div>
                        <small class="text-muted">ID: ${escapeHtml(item.nis || "-")}</small>
                    </td>
                    <td>${escapeHtml(item.nama_kelas)}</td>
                    <td>
                        <span class="status-badge ${badgeClass}">
                            ${normStatus === "Present" ? "✨" : normStatus === "Excused" ? "📝" : "🩺"}
                            ${escapeHtml(normStatus)}
                        </span>
                    </td>
                    <td>${escapeHtml(item.keterangan || "-")}</td>
                    <td><span class="text-muted" style="font-family: var(--font-mono); font-size: 0.8rem;">${escapeHtml(item.file_size || "-")}</span></td>
                    <td class="text-center">
                        <button type="button" class="btn btn-ghost btn-delete-presensi" data-id="${item.id}" title="Delete record">
                            🗑️
                        </button>
                    </td>
                </tr>
            `;
        }).join("");

        // Attach listeners for modal & delete
        elements.presensiTableBody.querySelectorAll(".thumb-preview").forEach(img => {
            img.addEventListener("click", () => {
                const id = img.dataset.presensiId;
                const nama = img.dataset.nama;
                const status = img.dataset.status;
                const waktu = img.dataset.waktu;
                openPhotoModal(id, nama, status, waktu);
            });
        });

        elements.presensiTableBody.querySelectorAll(".btn-delete-presensi").forEach(btn => {
            btn.addEventListener("click", async () => {
                const id = btn.dataset.id;
                if (confirm("Delete this attendance record and remove photo from S3?")) {
                    await deletePresensi(id);
                }
            });
        });
    }

    function renderManageKelasList() {
        if (!state.kelasList || state.kelasList.length === 0) {
            elements.listKelasContainer.innerHTML = '<li class="empty-text">No classes available. Add one above.</li>';
            return;
        }

        elements.listKelasContainer.innerHTML = state.kelasList.map(k => `
            <li>
                <div>
                    <strong>${escapeHtml(k.nama_kelas)}</strong>
                    <div class="text-muted" style="font-size: 0.75rem;">${escapeHtml(k.jurusan || "")}</div>
                </div>
                <button type="button" class="btn btn-ghost btn-delete-kelas" data-id="${k.id}" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;">
                    Delete
                </button>
            </li>
        `).join("");

        elements.listKelasContainer.querySelectorAll(".btn-delete-kelas").forEach(btn => {
            btn.addEventListener("click", async () => {
                const id = btn.dataset.id;
                if (confirm("Delete this class? Associated students will not be automatically deleted.")) {
                    await deleteKelas(id);
                }
            });
        });
    }

    function renderManageSiswaList() {
        if (!state.siswaList || state.siswaList.length === 0) {
            elements.listSiswaContainer.innerHTML = '<li class="empty-text">No students registered yet.</li>';
            return;
        }

        elements.listSiswaContainer.innerHTML = state.siswaList.map(s => `
            <li>
                <div>
                    <strong>${escapeHtml(s.nama_siswa)}</strong>
                    <div class="text-muted" style="font-size: 0.75rem;">ID: ${escapeHtml(s.nis || "-")} • ${escapeHtml(s.nama_kelas || "-")}</div>
                </div>
                <button type="button" class="btn btn-ghost btn-delete-siswa" data-id="${s.id}" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;">
                    Delete
                </button>
            </li>
        `).join("");

        elements.listSiswaContainer.querySelectorAll(".btn-delete-siswa").forEach(btn => {
            btn.addEventListener("click", async () => {
                const id = btn.dataset.id;
                if (confirm("Delete this student record?")) {
                    await deleteSiswa(id);
                }
            });
        });
    }

    // =========================================================================
    // EVENT HANDLERS & NAVIGATION
    // =========================================================================

    function setupTabNavigation() {
        elements.tabBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                elements.tabBtns.forEach(b => b.classList.remove("active"));
                elements.tabPanels.forEach(p => p.classList.remove("active"));

                btn.classList.add("active");
                const targetPanel = document.getElementById(btn.dataset.tab);
                if (targetPanel) targetPanel.classList.add("active");

                if (btn.dataset.tab !== "tab-presensi") {
                    stopCamera();
                }
            });
        });
    }

    function setupStatusRadioEvents() {
        elements.statusRadios.forEach(radio => {
            radio.addEventListener("change", (e) => {
                const status = e.target.value;
                if (status === "Present") {
                    elements.fotoLabelText.textContent = "Attendance Selfie Photo";
                    elements.inputKeterangan.placeholder = "e.g., Present at TKJ Computer Lab 2";
                } else if (status === "Excused") {
                    elements.fotoLabelText.textContent = "Excused Letter / Permission Document";
                    elements.inputKeterangan.placeholder = "e.g., Official school competition / Family leave";
                } else if (status === "Sick") {
                    elements.fotoLabelText.textContent = "Doctor's Note / Medical Proof";
                    elements.inputKeterangan.placeholder = "e.g., Fever / Resting at home";
                }
            });
        });

        // Dropdown Class change -> Load Students
        elements.selectPresensiKelas.addEventListener("change", async (e) => {
            const kelasId = e.target.value;
            elements.selectPresensiSiswa.innerHTML = '<option value="">-- Loading Students... --</option>';
            elements.selectPresensiSiswa.disabled = true;

            if (!kelasId) {
                elements.selectPresensiSiswa.innerHTML = '<option value="">-- Choose Class First --</option>';
                return;
            }

            try {
                const res = await fetch(`/api/siswa?kelas_id=${encodeURIComponent(kelasId)}`);
                const resData = await res.json();
                if (resData.success && resData.data.length > 0) {
                    elements.selectPresensiSiswa.innerHTML = 
                        '<option value="">-- Select Student Name --</option>' + 
                        resData.data.map(s => `<option value="${s.id}">${escapeHtml(s.nama_siswa)} (${escapeHtml(s.nis || "-")})</option>`).join("");
                    elements.selectPresensiSiswa.disabled = false;
                } else {
                    elements.selectPresensiSiswa.innerHTML = '<option value="">(No students found in this class)</option>';
                }
            } catch (err) {
                console.error("Failed to load students:", err);
                elements.selectPresensiSiswa.innerHTML = '<option value="">Failed to load data</option>';
            }
        });
    }

    // =========================================================================
    // CAMERA & PHOTO HANDLING
    // =========================================================================

    function setupPhotoMode() {
        elements.btnModeCamera.addEventListener("click", () => {
            elements.btnModeCamera.classList.add("active");
            elements.btnModeUpload.classList.remove("active");
            elements.cameraSection.style.display = "flex";
            elements.uploadSection.style.display = "none";
        });

        elements.btnModeUpload.addEventListener("click", () => {
            elements.btnModeUpload.classList.add("active");
            elements.btnModeCamera.classList.remove("active");
            elements.cameraSection.style.display = "none";
            elements.uploadSection.style.display = "block";
            stopCamera();
        });
    }

    function setupCamera() {
        elements.btnStartCamera.addEventListener("click", async () => {
            try {
                const constraints = {
                    video: {
                        facingMode: "user",
                        width: { ideal: 640 },
                        height: { ideal: 480 }
                    },
                    audio: false
                };

                state.cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
                elements.videoStream.srcObject = state.cameraStream;
                elements.cameraPlaceholder.style.display = "none";
                elements.videoStream.style.display = "block";

                elements.btnStartCamera.style.display = "none";
                elements.btnCaptureCamera.style.display = "inline-flex";
                elements.btnRetakeCamera.style.display = "none";
            } catch (err) {
                console.error("Camera access denied or failed:", err);
                showToast("Cannot access camera. Please use 'Upload Photo File' option.", "error");
            }
        });

        elements.btnCaptureCamera.addEventListener("click", () => {
            if (!state.cameraStream) return;

            const video = elements.videoStream;
            const canvas = elements.cameraCanvas;
            canvas.width = video.videoWidth || 640;
            canvas.height = video.videoHeight || 480;

            const ctx = canvas.getContext("2d");
            // Mirror image for realistic selfie preview
            ctx.translate(canvas.width, 0);
            ctx.scale(-1, 1);
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            canvas.toBlob((blob) => {
                if (!blob) {
                    showToast("Failed to capture image from camera", "error");
                    return;
                }

                state.activePhotoBlob = blob;
                state.activePhotoFile = null;

                const previewUrl = URL.createObjectURL(blob);
                elements.previewImage.src = previewUrl;
                elements.previewFilename.textContent = `selfie_${Date.now()}.jpg`;
                elements.previewSize.textContent = `${(blob.size / 1024).toFixed(1)} KB`;
                elements.previewContainer.style.display = "block";

                elements.btnCaptureCamera.style.display = "none";
                elements.btnRetakeCamera.style.display = "inline-flex";

                stopCamera();
                elements.cameraPlaceholder.style.display = "flex";
                elements.cameraPlaceholder.innerHTML = '<span class="camera-icon">✅</span><p>Selfie captured successfully!</p>';
                elements.videoStream.style.display = "none";
                showToast("Selfie photo captured!", "success");
            }, "image/jpeg", 0.9);
        });

        elements.btnRetakeCamera.addEventListener("click", () => {
            clearPhotoSelection();
            elements.btnRetakeCamera.style.display = "none";
            elements.btnStartCamera.click();
        });
    }

    function stopCamera() {
        if (state.cameraStream) {
            state.cameraStream.getTracks().forEach(track => track.stop());
            state.cameraStream = null;
        }
    }

    function setupDropzone() {
        const dropzone = elements.fotoDropzone;
        const fileInput = elements.fotoInput;

        ["dragenter", "dragover"].forEach(event => {
            dropzone.addEventListener(event, (e) => {
                e.preventDefault();
                dropzone.classList.add("dragover");
            });
        });

        ["dragleave", "drop"].forEach(event => {
            dropzone.addEventListener(event, (e) => {
                e.preventDefault();
                dropzone.classList.remove("dragover");
            });
        });

        dropzone.addEventListener("drop", (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) handleSelectedFile(files[0]);
        });

        fileInput.addEventListener("change", (e) => {
            if (e.target.files.length > 0) handleSelectedFile(e.target.files[0]);
        });

        elements.btnCancelPreview.addEventListener("click", () => {
            clearPhotoSelection();
        });
    }

    function handleSelectedFile(file) {
        const allowedTypes = ["image/jpeg", "image/png", "image/webp", "image/jpg"];
        if (!allowedTypes.includes(file.type)) {
            showToast("Only JPG, PNG, or WEBP images are allowed!", "error");
            return;
        }

        if (file.size > 15 * 1024 * 1024) {
            showToast("Maximum image size is 15 MB!", "error");
            return;
        }

        state.activePhotoFile = file;
        state.activePhotoBlob = null;

        const reader = new FileReader();
        reader.onload = (e) => {
            elements.previewImage.src = e.target.result;
            elements.previewFilename.textContent = file.name;
            elements.previewSize.textContent = `${(file.size / 1024).toFixed(1)} KB`;
            elements.previewContainer.style.display = "block";
            showToast("Photo file selected successfully", "success");
        };
        reader.readAsDataURL(file);
    }

    function clearPhotoSelection() {
        state.activePhotoBlob = null;
        state.activePhotoFile = null;
        elements.fotoInput.value = "";
        elements.previewContainer.style.display = "none";
        elements.previewImage.src = "";
        elements.cameraPlaceholder.innerHTML = '<span class="camera-icon">📷</span><p>Camera is currently off. Click below to activate your camera.</p>';
        elements.cameraPlaceholder.style.display = "flex";
        elements.videoStream.style.display = "none";
        elements.btnStartCamera.style.display = "inline-flex";
        elements.btnCaptureCamera.style.display = "none";
        elements.btnRetakeCamera.style.display = "none";
    }

    // =========================================================================
    // SUBMIT ATTENDANCE
    // =========================================================================

    function setupFormPresensi() {
        elements.formPresensi.addEventListener("submit", async (e) => {
            e.preventDefault();

            const kelasId = elements.selectPresensiKelas.value;
            const siswaId = elements.selectPresensiSiswa.value;
            const selectedStatusRadio = document.querySelector('input[name="status"]:checked');
            const status = selectedStatusRadio ? selectedStatusRadio.value : "Present";
            const keterangan = elements.inputKeterangan.value.trim();

            if (!kelasId || !siswaId) {
                showToast("Please choose class and student name first!", "error");
                return;
            }

            if (!state.activePhotoBlob && !state.activePhotoFile) {
                showToast("Please take a selfie or upload an image proof first!", "error");
                return;
            }

            const formData = new FormData();
            formData.append("kelas_id", kelasId);
            formData.append("siswa_id", siswaId);
            formData.append("status", status);
            formData.append("keterangan", keterangan);

            if (state.activePhotoFile) {
                formData.append("foto", state.activePhotoFile, state.activePhotoFile.name);
            } else if (state.activePhotoBlob) {
                formData.append("foto", state.activePhotoBlob, `selfie_${Date.now()}.jpg`);
            }

            const btn = elements.btnSubmitPresensi;
            const btnText = btn.querySelector(".btn-text");
            const spinner = btn.querySelector(".spinner");

            btn.disabled = true;
            btnText.textContent = "Uploading to S3 & Saving...";
            spinner.style.display = "inline-block";

            try {
                const res = await fetch("/api/presensi", {
                    method: "POST",
                    body: formData
                });
                const resData = await res.json();

                if (resData.success) {
                    showToast(resData.message || "Attendance recorded successfully!", "success");
                    elements.formPresensi.reset();
                    clearPhotoSelection();
                    elements.selectPresensiSiswa.innerHTML = '<option value="">-- Choose Class First --</option>';
                    elements.selectPresensiSiswa.disabled = true;

                    await loadStats();
                    await loadPresensi();

                    setTimeout(() => {
                        const rekapTab = document.querySelector('[data-tab="tab-rekap"]');
                        if (rekapTab) rekapTab.click();
                    }, 800);
                } else {
                    showToast(resData.message || resData.error || "Failed to submit attendance", "error");
                }
            } catch (err) {
                console.error("Error submitting attendance:", err);
                showToast("Network error connecting to Flask backend", "error");
            } finally {
                btn.disabled = false;
                btnText.textContent = "Submit Attendance";
                spinner.style.display = "none";
            }
        });
    }

    // =========================================================================
    // FILTERS & ACTIONS
    // =========================================================================

    function setupFilters() {
        elements.filterKelas.addEventListener("change", () => loadPresensi());
        elements.filterTanggal.addEventListener("change", () => loadPresensi());
        elements.filterStatus.addEventListener("change", () => loadPresensi());

        elements.btnResetFilter.addEventListener("click", () => {
            elements.filterKelas.value = "";
            elements.filterTanggal.value = "";
            elements.filterStatus.value = "";
            loadPresensi();
        });

        elements.btnRefreshRekap.addEventListener("click", async () => {
            elements.btnRefreshRekap.textContent = "⏳ Loading...";
            await loadPresensi();
            await loadStats();
            elements.btnRefreshRekap.textContent = "🔄 Refresh";
            showToast("Records refreshed", "success");
        });
    }

    async function deletePresensi(id) {
        try {
            const res = await fetch(`/api/presensi/${id}`, { method: "DELETE" });
            const resData = await res.json();
            if (resData.success) {
                showToast("Attendance record deleted", "success");
                await loadPresensi();
                await loadStats();
            } else {
                showToast(resData.message || "Failed to delete record", "error");
            }
        } catch (err) {
            showToast("Server error deleting record", "error");
        }
    }

    // =========================================================================
    // MANAGE CLASSES & STUDENTS
    // =========================================================================

    function setupManageForms() {
        // Add Class
        elements.formTambahKelas.addEventListener("submit", async (e) => {
            e.preventDefault();
            const nama = elements.inputNamaKelas.value.trim();
            const jurusan = elements.inputJurusan.value.trim();
            if (!nama) return;

            try {
                const res = await fetch("/api/kelas", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ nama_kelas: nama, jurusan })
                });
                const resData = await res.json();
                if (resData.success) {
                    showToast(resData.message, "success");
                    elements.inputNamaKelas.value = "";
                    await loadKelas();
                    await loadStats();
                } else {
                    showToast(resData.message || "Failed to create class", "error");
                }
            } catch (err) {
                showToast("Error creating class", "error");
            }
        });

        // Add Student
        elements.formTambahSiswa.addEventListener("submit", async (e) => {
            e.preventDefault();
            const kelasId = elements.siswaSelectKelas.value;
            const nis = elements.inputNis.value.trim();
            const nama = elements.inputNamaSiswa.value.trim();

            if (!kelasId || !nama) {
                showToast("Class and Student Name are required!", "error");
                return;
            }

            try {
                const res = await fetch("/api/siswa", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ kelas_id: kelasId, nis, nama_siswa: nama })
                });
                const resData = await res.json();
                if (resData.success) {
                    showToast(resData.message, "success");
                    elements.inputNamaSiswa.value = "";
                    elements.inputNis.value = "";
                    await loadSiswa(elements.filterManageSiswaKelas.value);
                    await loadStats();
                } else {
                    showToast(resData.message || "Failed to register student", "error");
                }
            } catch (err) {
                showToast("Error registering student", "error");
            }
        });

        // Filter Student list
        elements.filterManageSiswaKelas.addEventListener("change", (e) => {
            loadSiswa(e.target.value);
        });
    }

    async function deleteKelas(id) {
        try {
            const res = await fetch(`/api/kelas/${id}`, { method: "DELETE" });
            const resData = await res.json();
            if (resData.success) {
                showToast("Class deleted", "success");
                await loadKelas();
                await loadStats();
            } else {
                showToast(resData.message || "Failed to delete class", "error");
            }
        } catch (err) {
            showToast("Server error deleting class", "error");
        }
    }

    async function deleteSiswa(id) {
        try {
            const res = await fetch(`/api/siswa/${id}`, { method: "DELETE" });
            const resData = await res.json();
            if (resData.success) {
                showToast("Student deleted", "success");
                await loadSiswa(elements.filterManageSiswaKelas.value);
                await loadStats();
            } else {
                showToast(resData.message || "Failed to delete student", "error");
            }
        } catch (err) {
            showToast("Server error deleting student", "error");
        }
    }

    // =========================================================================
    // MODAL PREVIEW
    // =========================================================================

    function setupModal() {
        elements.btnCloseModal.addEventListener("click", closeModal);
        elements.photoModal.addEventListener("click", (e) => {
            if (e.target === elements.photoModal) closeModal();
        });

        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && elements.photoModal.classList.contains("open")) {
                closeModal();
            }
        });
    }

    function openPhotoModal(id, nama, status, waktu) {
        const photoUrl = `/api/presensi/${id}/foto`;
        elements.modalPhotoTitle.textContent = `Attendance Photo - ${nama}`;
        elements.modalPhotoImg.src = photoUrl;
        elements.modalPhotoDesc.innerHTML = `
            <strong>Status:</strong> ${escapeHtml(status)} &bull; 
            <strong>Time:</strong> ${escapeHtml(waktu)}
        `;
        elements.btnDownloadModalPhoto.href = `${photoUrl}?download=true`;
        elements.photoModal.classList.add("open");
    }

    function closeModal() {
        elements.photoModal.classList.remove("open");
        elements.modalPhotoImg.src = "";
    }

    // =========================================================================
    // UTILITIES
    // =========================================================================

    function showToast(message, type = "success") {
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span>${type === "success" ? "✅" : "⚠️"}</span>
            <span>${escapeHtml(message)}</span>
        `;
        elements.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateX(100%)";
            toast.style.transition = "all 0.3s ease";
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Start App
    init();
});
