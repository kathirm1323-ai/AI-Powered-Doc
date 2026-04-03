/**
 * DocMind AI — Obsidian Intelligence App Logic
 */

(() => {
    "use strict";

    const API_BASE = window.location.origin;

    // DOM Elements
    const $ = (sel) => document.querySelector(sel);
    const canvasCard    = $("#canvas-card");
    const viewUpload    = $("#view-upload");
    const viewSelected  = $("#view-selected");
    const viewProcessing= $("#view-processing");
    const viewResults   = $("#view-results");

    const uploadZone    = $("#upload-zone");
    const fileInput     = $("#file-input");
    
    // File Selected State Elements
    const fileExt       = $("#file-ext");
    const fileName      = $("#file-name");
    const fileSize      = $("#file-size");
    const fileType      = $("#file-type");
    const analyzeBtn    = $("#analyze-btn");

    // Processing State Elements
    const terminalOutput = $("#terminal-output");
    const progressBar    = $("#progress-bar");

    // Results Elements
    const resultSummary   = $("#result-summary");
    const entitiesGrid    = $("#entities-grid");
    const sentimentBlock  = $("#sentiment-block");
    const sentimentWord   = $("#sentiment-word");
    const sentimentFill   = $("#sentiment-fill");
    const sentimentDesc   = $("#sentiment-desc");

    const statWords  = $("#stat-words");
    const statChars  = $("#stat-chars");
    const statFormat = $("#stat-format");
    const statTime   = $("#stat-time");

    const newBtn  = $("#new-btn");

    let selectedFile = null;
    let latestJsonResponse = null;

    // Utilities
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
        return (bytes / (1024 * 1024)).toFixed(2) + " MB";
    }

    function getFileExtension(name) {
        return name.split(".").pop().toLowerCase();
    }

    function sleep(ms) {
        return new Promise((r) => setTimeout(r, ms));
    }

    // View Switching
    function setCanvasView(viewId) {
        [viewUpload, viewSelected, viewProcessing].forEach(v => v.style.display = "none");
        $(viewId).style.display = "flex";
    }

    function resetApp() {
        selectedFile = null;
        fileInput.value = "";
        canvasCard.classList.remove("is-selected");
        setCanvasView("#view-upload");
        viewResults.classList.remove("visible");
        setTimeout(() => viewResults.style.display = "none", 500);
        terminalOutput.innerHTML = "";
        progressBar.style.width = "0%";
        sentimentFill.style.width = "0%";
    }

    // File Selection Logic
    function handleFile(file) {
        if (!file) return;
        selectedFile = file;
        const ext = getFileExtension(file.name).toUpperCase();
        
        fileExt.textContent = `[${ext}]`;
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        fileType.textContent = ext;

        canvasCard.classList.add("is-selected");
        setCanvasView("#view-selected");
    }

    // Event Listeners (Drag/Drop)
    uploadZone.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length) handleFile(e.target.files[0]);
    });

    canvasCard.addEventListener("dragover", (e) => {
        e.preventDefault();
        if(!selectedFile) {
            canvasCard.classList.add("drag-over");
            if (typeof setDragPhysics === 'function') setDragPhysics(true);
        }
    });
    canvasCard.addEventListener("dragleave", (e) => {
        e.preventDefault();
        canvasCard.classList.remove("drag-over");
        if (typeof setDragPhysics === 'function') setDragPhysics(false);
    });
    canvasCard.addEventListener("drop", (e) => {
        e.preventDefault();
        canvasCard.classList.remove("drag-over");
        if (typeof setDragPhysics === 'function') setDragPhysics(false);
        if (e.dataTransfer.files.length && !selectedFile) handleFile(e.dataTransfer.files[0]);
    });

    newBtn.addEventListener("click", resetApp);

    // Terminal Animation Logic
    async function runTerminalSequence() {
        const steps = [
            { text: "> Initializing document parser...", status: "✓", delay: 600 },
            { text: "> Extracting raw text layer...", status: "✓", delay: 800 },
            { text: "> Tokenizing content...", status: "[▓▓▓▓▓░░░░░]", delay: 700 },
            { text: "> Running entity recognition...", status: "—", delay: 900 },
            { text: "> Sentiment analysis...", status: "—", delay: 800 },
            { text: "> Generating summary...", status: "—", delay: 600 }
        ];

        terminalOutput.innerHTML = "";
        progressBar.style.width = "5%";

        let currentLine = null;
        for (let i = 0; i < steps.length; i++) {
            const step = steps[i];
            
            // Remove cursor from previous line
            if (currentLine) {
                const prevCursor = currentLine.querySelector('.term-cursor');
                if(prevCursor) prevCursor.remove();
                // If it was the tokenizing step, complete it visually
                if (steps[i-1].status.includes("▓")) {
                    currentLine.querySelector('.term-status').innerHTML = `<span class="term-check">✓</span>`;
                }
            }

            // Calculate overall progress
            progressBar.style.width = ((i+1) / steps.length * 90) + "%";

            currentLine = document.createElement("div");
            currentLine.className = "term-line";
            
            const textSpan = document.createElement("span");
            textSpan.className = "term-text";
            textSpan.innerHTML = `${step.text} <span class="term-cursor"></span>`;
            
            const statusSpan = document.createElement("span");
            statusSpan.className = "term-status";
            statusSpan.innerHTML = step.status === "✓" ? `<span class="term-check">✓</span>` : step.status;

            currentLine.appendChild(textSpan);
            currentLine.appendChild(statusSpan);
            terminalOutput.appendChild(currentLine);

            await sleep(step.delay);
        }

        // Finish up
        if(currentLine) {
            const finalCursor = currentLine.querySelector('.term-cursor');
            if(finalCursor) finalCursor.remove();
            
            // Turn all dashes to checks at the very end
            const allStatuses = terminalOutput.querySelectorAll('.term-status');
            allStatuses.forEach(s => s.innerHTML = `<span class="term-check">✓</span>`);
        }
        
        progressBar.style.width = "100%";
        await sleep(400);
    }

    // Number Counting Animation
    function animateNumber(el, target, duration = 1000) {
        const start = 0;
        const startTime = performance.now();
        
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // easeOutExpo
            const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
            
            const current = Math.floor(start + (target - start) * ease);
            el.textContent = current.toLocaleString('en-US');
            
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                el.textContent = target.toLocaleString('en-US');
            }
        }
        requestAnimationFrame(update);
    }

    // Generate Entities HTML
    function buildEntitiesTable(entities) {
        const map = {
            persons: "PERSONS",
            organizations: "ORGS",
            locations: "LOCATIONS",
            dates: "DATES",
            monetary_amounts: "AMOUNTS"
        };

        entitiesGrid.innerHTML = "";
        let pillIndex = 0;
        let totalEntitiesFound = 0;

        for (const [key, label] of Object.entries(map)) {
            const items = entities[key] || [];
            
            if (items.length > 0) {
                totalEntitiesFound += items.length;
                
                const row = document.createElement("div");
                row.className = "entity-row";
                
                const type = document.createElement("span");
                type.className = "ent-type";
                type.textContent = label;
                
                const line = document.createElement("div");
                line.className = "ent-line";
                
                const list = document.createElement("div");
                list.className = "ent-list";

                items.forEach((item) => {
                    const tag = document.createElement("span");
                    tag.className = "ent-pill";
                    tag.textContent = item;
                    list.appendChild(tag);
                    
                    setTimeout(() => { tag.classList.add("visible"); }, ~~(800 + (pillIndex * 50)));
                    pillIndex++;
                });

                row.appendChild(type);
                row.appendChild(line);
                row.appendChild(list);
                entitiesGrid.appendChild(row);
            }
        }
        
        const entitiesContainer = document.querySelector('.entities-block');
        if (totalEntitiesFound === 0) {
            entitiesContainer.style.display = 'none';
        } else {
            entitiesContainer.style.display = 'flex';
            entitiesContainer.style.flexDirection = 'column';
        }
    }

    // API Integration
    analyzeBtn.addEventListener("click", async () => {
        if (!selectedFile) return;

        setCanvasView("#view-processing");
        canvasCard.classList.remove("is-selected");

        const startTime = Date.now();
        const animationPromise = runTerminalSequence();

        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            const response = await fetch(`${API_BASE}/analyze`, {
                method: "POST",
                body: formData,
            });

            await animationPromise;

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const detail = errorData.detail;
                let msg = "API Exception";
                if (detail) {
                    msg = typeof detail === "object" ? detail.message || JSON.stringify(detail) : String(detail);
                }
                throw new Error(msg);
            }

            const data = await response.json();
            latestJsonResponse = data;
            
            const endTime = Date.now();
            const timeTaken = ((endTime - startTime) / 1000).toFixed(1);

            // Populate Results
            resultSummary.textContent = data.summary;
            
            buildEntitiesTable(data.entities);

            const sent = (data.sentiment || "neutral").toLowerCase();
            sentimentBlock.setAttribute("data-sentiment", sent);
            sentimentWord.textContent = sent.toUpperCase();
            sentimentDesc.textContent = data.sentiment_explanation;
            
            statFormat.textContent = data.file_type || getFileExtension(selectedFile.name).toUpperCase();
            statTime.textContent = timeTaken + "s";

            // Reveal Payoff
            viewResults.style.display = "block";
            // trigger reflow
            void viewResults.offsetWidth;
            viewResults.classList.add("visible");
            
            // Trigger sentiment bar fill
            setTimeout(() => {
                sentimentFill.style.width = "100%";
            }, 500);

            // Trigger number counters
            animateNumber(statWords, parseInt(data.word_count) || 0);
            animateNumber(statChars, parseInt(data.char_count) || 0);

        } catch (err) {
            console.error(err);
            terminalOutput.innerHTML += `<div class="term-line" style="color:var(--negative)">> EXCEPTION: ${err.message}</div>`;
            progressBar.style.background = "var(--negative)";
        }
    });

    // ── Three.js 3D Engine ─────────────────────────────────────
    const canvas = document.getElementById('three-canvas');
    if (canvas && typeof THREE !== 'undefined') {
        const scene = new THREE.Scene();
        let width = window.innerWidth;
        let height = window.innerHeight;
        
        const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        camera.position.z = 6;

        const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        // Use Octahedron for a geometric "Diamond" shape
        const geometry = new THREE.OctahedronGeometry(4, 0);
        const material = new THREE.MeshBasicMaterial({ 
            color: 0xc9a84c, wireframe: true, transparent: true, opacity: 0.15 
        });
        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        let mouseX = 0; let mouseY = 0;
        let targetRotationX = 0; let targetRotationY = 0;

        document.addEventListener('mousemove', (event) => {
            mouseX = (event.clientX - (width/2)) * 0.001;
            mouseY = (event.clientY - (height/2)) * 0.001;
        });

        let baseRotationSpeed = 0.0015;
        function animate3D() {
            requestAnimationFrame(animate3D);
            targetRotationX = mouseY * 0.5; targetRotationY = mouseX * 0.5;
            mesh.rotation.y += baseRotationSpeed + (targetRotationY - mesh.rotation.y) * 0.05;
            mesh.rotation.x += baseRotationSpeed + (targetRotationX - mesh.rotation.x) * 0.05;
            renderer.render(scene, camera);
        }
        animate3D();

        window.addEventListener('resize', () => {
            width = window.innerWidth;
            height = window.innerHeight;
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            renderer.setSize(width, height);
        });

        window.setDragPhysics = function(isDragging) {
            if(isDragging) { material.opacity = 0.5; baseRotationSpeed = 0.04; }
            else { material.opacity = 0.15; baseRotationSpeed = 0.0015; }
        };
    }

})();
