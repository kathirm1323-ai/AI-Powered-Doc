/**
 * DocMind AI — Frontend Application Logic
 * Handles file upload, API communication, and results rendering.
 */

(() => {
    "use strict";

    // ── Configuration ──────────────────────────────────────────
    const API_BASE = window.location.origin;

    // ── DOM References ─────────────────────────────────────────
    const $ = (sel) => document.querySelector(sel);
    const heroSection     = $("#hero-section");
    const uploadZone      = $("#upload-zone");
    const fileInput       = $("#file-input");
    const filePreview     = $("#file-preview");
    const fileName        = $("#file-name");
    const fileMeta        = $("#file-meta");
    const fileIconWrapper = $("#file-icon-wrapper");
    const fileRemove      = $("#file-remove");
    const analyzeBtn      = $("#analyze-btn");
    const processingSection   = $("#processing-section");
    const processingStatus    = $("#processing-status");
    const progressFill        = $("#progress-fill");
    const resultsSection      = $("#results-section");
    const resultsFilename     = $("#results-filename");
    const errorSection        = $("#error-section");
    const errorMessage        = $("#error-message");
    const retryBtn            = $("#retry-btn");
    const newAnalysisBtn      = $("#new-analysis-btn");

    // Stats
    const statWords     = $("#stat-words");
    const statChars     = $("#stat-chars");
    const statType      = $("#stat-type");
    const statSentiment = $("#stat-sentiment");

    // Results content
    const resultSummary             = $("#result-summary");
    const sentimentBadge            = $("#sentiment-badge");
    const resultSentimentExplanation = $("#result-sentiment-explanation");
    const entitiesGrid              = $("#entities-grid");

    let selectedFile = null;

    // ── Utilities ──────────────────────────────────────────────
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
        return (bytes / (1024 * 1024)).toFixed(2) + " MB";
    }

    function getFileExtension(name) {
        return name.split(".").pop().toLowerCase();
    }

    function getFileTypeLabel(ext) {
        const map = {
            pdf: "PDF", docx: "DOCX", doc: "DOC",
            png: "PNG", jpg: "JPG", jpeg: "JPEG",
            webp: "WebP", bmp: "BMP", tiff: "TIFF", tif: "TIFF",
        };
        return map[ext] || ext.toUpperCase();
    }

    function getFileTypeClass(ext) {
        if (ext === "pdf") return "pdf";
        if (ext === "docx" || ext === "doc") return "docx";
        return "image";
    }

    function formatNumber(n) {
        return n.toLocaleString("en-US");
    }

    function sleep(ms) {
        return new Promise((r) => setTimeout(r, ms));
    }

    // ── Section Management ─────────────────────────────────────
    function showSection(section) {
        [heroSection, processingSection, resultsSection, errorSection].forEach(
            (s) => (s.style.display = "none")
        );
        section.style.display = "";
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    function resetUpload() {
        selectedFile = null;
        fileInput.value = "";
        uploadZone.style.display = "";
        filePreview.style.display = "none";
        fileIconWrapper.className = "file-icon-wrapper";
    }

    // ── File Selection ─────────────────────────────────────────
    function handleFileSelect(file) {
        if (!file) return;
        selectedFile = file;

        const ext = getFileExtension(file.name);

        fileName.textContent = file.name;
        fileMeta.textContent = `${getFileTypeLabel(ext)} • ${formatFileSize(file.size)}`;
        fileIconWrapper.className = `file-icon-wrapper ${getFileTypeClass(ext)}`;

        uploadZone.style.display = "none";
        filePreview.style.display = "";
    }

    // ── Drag & Drop ────────────────────────────────────────────
    uploadZone.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length) handleFileSelect(e.target.files[0]);
    });

    uploadZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        uploadZone.classList.add("drag-over");
    });

    uploadZone.addEventListener("dragleave", (e) => {
        e.preventDefault();
        uploadZone.classList.remove("drag-over");
    });

    uploadZone.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadZone.classList.remove("drag-over");
        if (e.dataTransfer.files.length) handleFileSelect(e.dataTransfer.files[0]);
    });

    fileRemove.addEventListener("click", resetUpload);

    // ── Processing Animation ───────────────────────────────────
    async function animateProcessing() {
        const steps = [
            { msg: "> Initiating extraction protocols...", progress: 20 },
            { msg: "> Decrypting semantic structure...", progress: 45 },
            { msg: "> Mapping named entities...", progress: 75 },
            { msg: "> Finalizing algorithmic analysis...", progress: 90 },
        ];

        for (const step of steps) {
            processingStatus.textContent = step.msg;
            progressFill.style.width = step.progress + "%";
            await sleep(700);
        }
    }

    function resetProcessingSteps() {
        processingStatus.textContent = "> Ready.";
        progressFill.style.width = "0%";
    }

    // ── Entity Rendering ───────────────────────────────────────
    const entityLabels = {
        persons: "👤 People",
        organizations: "🏢 Organizations",
        locations: "📍 Locations",
        dates: "📅 Dates",
        monetary_amounts: "💰 Amounts",
    };

    function renderEntities(entities) {
        entitiesGrid.innerHTML = "";

        for (const [key, label] of Object.entries(entityLabels)) {
            const items = entities[key] || [];
            const group = document.createElement("div");
            group.className = `entity-group ${key}`;

            const title = document.createElement("div");
            title.className = "entity-group-title";
            title.innerHTML = `${label} <span class="entity-count">${items.length}</span>`;
            group.appendChild(title);

            if (items.length > 0) {
                const tagsDiv = document.createElement("div");
                tagsDiv.className = "entity-tags";
                items.forEach((item) => {
                    const tag = document.createElement("span");
                    tag.className = "entity-tag";
                    tag.textContent = item;
                    tagsDiv.appendChild(tag);
                });
                group.appendChild(tagsDiv);
            } else {
                const empty = document.createElement("p");
                empty.className = "entity-empty";
                empty.textContent = "None found";
                group.appendChild(empty);
            }

            entitiesGrid.appendChild(group);
        }
    }

    // ── Results Rendering ──────────────────────────────────────
    function renderResults(data) {
        resultsFilename.textContent = data.filename;

        // Stats
        statWords.textContent = formatNumber(data.word_count);
        statChars.textContent = formatNumber(data.char_count);
        statType.textContent = data.file_type;
        statSentiment.textContent =
            data.sentiment.charAt(0).toUpperCase() + data.sentiment.slice(1);

        // Summary
        resultSummary.textContent = data.summary;

        // Sentiment
        sentimentBadge.textContent = data.sentiment;
        sentimentBadge.className = `sentiment-badge ${data.sentiment}`;
        resultSentimentExplanation.textContent = data.sentiment_explanation;

        // Entities
        renderEntities(data.entities);

        showSection(resultsSection);
    }

    // ── API Call ────────────────────────────────────────────────
    async function analyzeDocument() {
        if (!selectedFile) return;

        showSection(processingSection);
        resetProcessingSteps();

        const animationPromise = animateProcessing();

        // Build FormData
        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            const response = await fetch(`${API_BASE}/analyze`, {
                method: "POST",
                body: formData,
            });

            // Wait for animation to finish
            await animationPromise;

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const detail = errorData.detail;
                let msg = "Analysis failed. Please try again.";
                if (detail) {
                    msg = typeof detail === "object" ? detail.message || msg : String(detail);
                }
                throw new Error(msg);
            }

            const data = await response.json();

            // Complete step
            progressFill.style.width = "100%";
            processingStatus.textContent = "> Analysis complete.";
            await sleep(600);

            renderResults(data);
        } catch (err) {
            console.error("Analysis error:", err);
            errorMessage.textContent = err.message || "An unexpected error occurred.";
            showSection(errorSection);
        }
    }

    // ── Event Listeners ────────────────────────────────────────
    analyzeBtn.addEventListener("click", analyzeDocument);

    retryBtn.addEventListener("click", () => {
        resetUpload();
        showSection(heroSection);
    });

    newAnalysisBtn.addEventListener("click", () => {
        resetUpload();
        showSection(heroSection);
    });

    // Keyboard shortcut: Enter to analyze when file is selected
    document.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && selectedFile && heroSection.style.display !== "none") {
            analyzeDocument();
        }
    });
})();
