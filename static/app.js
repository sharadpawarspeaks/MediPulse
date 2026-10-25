/**
 * MediPulse Frontend Application Logic
 * PWA Service Worker, Local Context, Form Handlers, and Demo Scenarios
 */

document.addEventListener('DOMContentLoaded', () => {

    /* ==========================================================================
       1. PWA Service Worker & Install Prompt Registration
       ========================================================================== */
    let deferredInstallPrompt = null;
    const installBtn = document.getElementById('pwa-install-btn');

    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/sw.js')
                .then((registration) => {
                    console.log('[MediPulse PWA] Service Worker registered with scope:', registration.scope);
                })
                .catch((error) => {
                    console.warn('[MediPulse PWA] Service Worker registration failed:', error);
                });
        });
    }

    window.addEventListener('beforeinstallprompt', (e) => {
        // Prevent default mini-infobar on mobile Android
        e.preventDefault();
        deferredInstallPrompt = e;
        if (installBtn) {
            installBtn.classList.remove('hidden');
        }
    });

    if (installBtn) {
        // Keep install button accessible on Android & PWA-compatible environments
        installBtn.classList.remove('hidden');

        installBtn.addEventListener('click', async () => {
            if (deferredInstallPrompt) {
                deferredInstallPrompt.prompt();
                const { outcome } = await deferredInstallPrompt.userChoice;
                console.log('[MediPulse PWA] User install choice:', outcome);
                if (outcome === 'accepted') {
                    installBtn.classList.add('hidden');
                }
                deferredInstallPrompt = null;
            } else {
                // If browser has not fired beforeinstallprompt or is already in browser
                alert('📱 Install MediPulse as an Android App:\n\n1. In Chrome, tap the three dots menu (⋮) in the top-right corner.\n2. Tap "Install app" or "Add to Home screen".\n3. MediPulse will install directly onto your device with offline support!');
            }
        });
    }

    /* ==========================================================================
       2. Mobile Navigation & Drawer Toggle
       ========================================================================== */
    const hamburger = document.getElementById('hamburger');
    const mobileMenu = document.getElementById('mobile-menu');

    if (hamburger && mobileMenu) {
        hamburger.addEventListener('click', () => {
            const isExpanded = hamburger.getAttribute('aria-expanded') === 'true';
            hamburger.setAttribute('aria-expanded', !isExpanded);
            mobileMenu.classList.toggle('active');
        });
    }

    /* ==========================================================================
       3. Privacy Profile Context Management (LocalStorage)
       ========================================================================== */
    const profileModal = document.getElementById('profile-modal');
    const profileBtn = document.getElementById('profile-modal-btn');
    const mobileProfileBtn = document.getElementById('mobile-profile-btn');
    const profileCloseBtn = document.getElementById('profile-modal-close');
    const profileForm = document.getElementById('health-context-form');
    const clearProfileBtn = document.getElementById('clear-profile-btn');

    const openProfileModal = () => {
        // Load saved state
        const saved = JSON.parse(localStorage.getItem('medipulse_profile') || '{}');
        if (saved.age) document.getElementById('ctx-age').value = saved.age;
        if (saved.conditions) document.getElementById('ctx-conditions').value = saved.conditions;
        if (saved.language) document.getElementById('ctx-language').value = saved.language;
        profileModal.classList.remove('hidden');
    };

    const closeProfileModal = () => {
        profileModal.classList.add('hidden');
    };

    if (profileBtn) profileBtn.addEventListener('click', openProfileModal);
    if (mobileProfileBtn) mobileProfileBtn.addEventListener('click', () => {
        mobileMenu.classList.remove('active');
        openProfileModal();
    });
    if (profileCloseBtn) profileCloseBtn.addEventListener('click', closeProfileModal);

    if (profileForm) {
        profileForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const profile = {
                age: document.getElementById('ctx-age').value,
                conditions: document.getElementById('ctx-conditions').value.trim(),
                language: document.getElementById('ctx-language').value
            };
            localStorage.setItem('medipulse_profile', JSON.stringify(profile));
            closeProfileModal();
            alert('Your private health context has been saved to your browser.');
        });
    }

    if (clearProfileBtn) {
        clearProfileBtn.addEventListener('click', () => {
            localStorage.removeItem('medipulse_profile');
            document.getElementById('ctx-age').value = '';
            document.getElementById('ctx-conditions').value = '';
            document.getElementById('ctx-language').value = 'en';
            closeProfileModal();
            alert('Local health context cleared.');
        });
    }

    const getStoredHealthContext = () => {
        try {
            const saved = JSON.parse(localStorage.getItem('medipulse_profile') || '{}');
            const parts = [];
            if (saved.age) parts.push(`Age: ${saved.age}`);
            if (saved.conditions) parts.push(`Known Conditions: ${saved.conditions}`);
            return parts.join(', ');
        } catch {
            return '';
        }
    };

    /* ==========================================================================
       4. Tab Navigation
       ========================================================================== */
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const androidNavItems = document.querySelectorAll('.android-nav-item');

    const switchTab = (targetId) => {
        // Sync desktop sidebar tabs
        tabBtns.forEach(b => {
            const isMatch = b.dataset.target === targetId;
            b.classList.toggle('active', isMatch);
            b.setAttribute('aria-selected', isMatch);
        });

        // Sync Android bottom navigation bar
        androidNavItems.forEach(item => {
            if (item.dataset.tab) {
                const isMatch = item.dataset.tab === targetId;
                item.classList.toggle('active', isMatch);
            }
        });

        tabPanes.forEach(pane => {
            if (pane.id === targetId) {
                pane.classList.remove('hidden');
                pane.classList.add('active');
            } else {
                pane.classList.add('hidden');
                pane.classList.remove('active');
            }
        });

        if (window.location.hash !== `#${targetId}`) {
            window.location.hash = targetId;
        }
    };

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.target));
    });

    // Android Bottom Navigation 1-tap tab switching
    androidNavItems.forEach(item => {
        const tabTarget = item.dataset.tab;
        if (tabTarget && (window.location.pathname === '/' || window.location.pathname === '')) {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                switchTab(tabTarget);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }
    });

    // Check hash on load
    if (window.location.hash) {
        const hashTarget = window.location.hash.substring(1);
        if (document.getElementById(hashTarget)) {
            switchTab(hashTarget);
        }
    }

    /* ==========================================================================
       5. Markdown Rendering with Sanitization
       ========================================================================== */
    const safeRenderMarkdown = (rawMarkdown) => {
        if (!rawMarkdown) return '';
        let parsed = '';
        if (typeof marked !== 'undefined') {
            parsed = marked.parse(rawMarkdown);
        } else {
            parsed = rawMarkdown.replace(/\n/g, '<br>');
        }
        if (typeof DOMPurify !== 'undefined') {
            return DOMPurify.sanitize(parsed);
        }
        return parsed;
    };

    /* ==========================================================================
       6. HTML Result Card Builder
       ========================================================================== */
    const buildResultHTML = (data) => {
        let html = '';

        // Confidence Pill
        if (data.confidence) {
            html += `<span class="confidence-pill conf-${data.confidence}">Evidence Confidence: ${data.confidence}</span>`;
        }

        // Biomarker Table for LabLens if present
        if (data.detected_markers && data.detected_markers.length > 0) {
            html += `<table class="biomarker-table">
                        <thead>
                            <tr>
                                <th>Test Parameter</th>
                                <th>Observed Value</th>
                                <th>Reference Range</th>
                                <th>Clinical Purpose</th>
                            </tr>
                        </thead>
                        <tbody>`;
            data.detected_markers.forEach(m => {
                html += `<tr>
                            <td><strong>${m.test_name}</strong></td>
                            <td><span style="color:#0284c7;font-weight:700;">${m.observed_value}</span></td>
                            <td>${m.typical_range}</td>
                            <td><small>${m.plain_explanation}</small></td>
                         </tr>`;
            });
            html += `</tbody></table>`;
        }

        // Main Content Body
        html += `<div class="markdown-body">${safeRenderMarkdown(data.content || data.markdown || '')}</div>`;

        // Follow-Up Questions (Interactive chips that can be clicked to ask)
        if (data.follow_up_questions && data.follow_up_questions.length > 0) {
            html += `<div class="follow-ups-section">
                        <h4>Explore Further & Bull; Suggested Questions:</h4>
                        <div class="chips-list">`;
            data.follow_up_questions.forEach(q => {
                html += `<button type="button" class="chip-btn follow-up-chip" data-question="${q.replace(/"/g, '&quot;')}">${q}</button>`;
            });
            html += `   </div>
                     </div>`;
        }

        // Citations & Sourced Facts
        if (data.sources && data.sources.length > 0) {
            html += `<div class="sources-card">
                        <h4>Authoritative Medical Sources & Evidence:</h4>
                        <ul>`;
            data.sources.forEach(s => {
                const urlMatch = s.match(/https?:\/\/[^\s\)]+/);
                if (urlMatch) {
                    html += `<li>🔗 <a href="${urlMatch[0]}" target="_blank" rel="noopener noreferrer">${s}</a></li>`;
                } else {
                    html += `<li>📚 ${s}</li>`;
                }
            });
            html += `   </ul>
                     </div>`;
        }

        // Transparency Panel (Innovation H)
        if (data.transparency) {
            const t = data.transparency;
            html += `<div class="transparency-panel">
                        <div class="transparency-badges">
                            <span class="tech-badge">Model: ${t.model_used}</span>
                            <span class="tech-badge">${t.is_mock ? 'Mock Mode' : 'Live Inference'}</span>
                            <span class="tech-badge">Latency: ${t.latency_ms}ms</span>
                        </div>
                        <div>
                            <span>Evidence: <strong>${t.evidence_level}</strong></span>
                        </div>
                     </div>`;
        }

        return html;
    };

    /* ==========================================================================
       7. Emergency Red-Flag Detection (LifeAlert)
       ========================================================================== */
    const banner = document.getElementById('global-emergency-banner');
    const emergencyText = document.getElementById('emergency-text');
    const emergencyClose = document.getElementById('emergency-close-btn');

    if (emergencyClose && banner) {
        emergencyClose.addEventListener('click', () => banner.classList.add('hidden'));
    }

    const checkEmergencySafety = async (symptoms) => {
        try {
            const res = await fetch('/api/lifealert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symptoms })
            });
            const data = await res.json();
            if (data.is_emergency && banner) {
                emergencyText.innerText = `${data.warning_message} — ${data.recommendation}`;
                banner.classList.remove('hidden');
                banner.scrollIntoView({ behavior: 'smooth' });
            } else if (banner) {
                banner.classList.add('hidden');
            }
        } catch (e) {
            console.warn('LifeAlert check warning:', e);
        }
    };

    /* ==========================================================================
       8. Generic AI Request Handler
       ========================================================================== */
    const handleAIPost = async (url, payload, resultId, loaderId, formId) => {
        const resultBox = document.getElementById(resultId);
        const loader = document.getElementById(loaderId);
        const form = document.getElementById(formId);
        const submitBtn = form ? form.querySelector('button[type="submit"]') : null;

        if (resultBox) resultBox.classList.add('hidden');
        if (loader) loader.classList.remove('hidden');
        if (submitBtn) submitBtn.disabled = true;

        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.error || 'Server returned an error response.');
            }

            if (resultBox) {
                resultBox.innerHTML = buildResultHTML(data);
                resultBox.classList.remove('hidden');

                // Attach click listeners to chips
                resultBox.querySelectorAll('.follow-up-chip').forEach(chip => {
                    chip.addEventListener('click', () => {
                        const question = chip.dataset.question;
                        switchTab('healthgpt-tab');
                        const chatInput = document.getElementById('chat-input');
                        if (chatInput) {
                            chatInput.value = question;
                            chatInput.focus();
                        }
                    });
                });
            }
        } catch (err) {
            if (resultBox) {
                resultBox.innerHTML = `<div style="color:var(--danger-crimson);padding:1rem;background:var(--danger-light);border-radius:8px;">
                    <strong>Notice:</strong> ${err.message || 'Unable to complete request. Please verify network or server status.'}
                </div>`;
                resultBox.classList.remove('hidden');
            }
        } finally {
            if (loader) loader.classList.add('hidden');
            if (submitBtn) submitBtn.disabled = false;
        }
    };

    /* ==========================================================================
       9. Form Listeners
       ========================================================================== */

    // HealthSense Form
    const hsForm = document.getElementById('healthsense-form');
    if (hsForm) {
        hsForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const symptoms = document.getElementById('hs-symptoms').value.trim();
            const readingLevel = document.getElementById('hs-reading-level').value;
            const language = document.getElementById('hs-language').value;

            checkEmergencySafety(symptoms);
            handleAIPost('/api/healthsense', {
                symptoms,
                reading_level: readingLevel,
                language
            }, 'hs-result', 'hs-loader', 'healthsense-form');
        });
    }

    // HealthGPT Form
    const chatForm = document.getElementById('healthgpt-form');
    const chatMessages = document.getElementById('chat-messages');
    let chatHistory = '';

    if (chatForm && chatMessages) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const inputEl = document.getElementById('chat-input');
            const message = inputEl.value.trim();
            if (!message) return;

            // Render User Message
            const userDiv = document.createElement('div');
            userDiv.className = 'message msg-user';
            userDiv.textContent = message;
            chatMessages.appendChild(userDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            inputEl.value = '';
            document.getElementById('chat-loader').classList.remove('hidden');

            // Parallel safety check
            checkEmergencySafety(message);

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        input: message,
                        history: chatHistory,
                        health_context: getStoredHealthContext()
                    })
                });

                const data = await res.json();
                const aiDiv = document.createElement('div');
                aiDiv.className = 'message msg-ai';
                aiDiv.innerHTML = safeRenderMarkdown(data.content);
                chatMessages.appendChild(aiDiv);

                chatHistory += `User: ${message}\nAI: ${data.content}\n`;
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } catch (err) {
                const errDiv = document.createElement('div');
                errDiv.className = 'message msg-ai';
                errDiv.style.color = 'var(--danger-crimson)';
                errDiv.textContent = 'Connection issue. Please verify server status.';
                chatMessages.appendChild(errDiv);
            } finally {
                document.getElementById('chat-loader').classList.add('hidden');
            }
        });
    }

    // Prevent360 Form
    const preventForm = document.getElementById('prevent-form');
    if (preventForm) {
        preventForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const focus = document.getElementById('prevent-focus').value.trim();
            handleAIPost('/api/prevent', { focus_area: focus }, 'prevent-result', 'prevent-loader', 'prevent-form');
        });
    }

    // TruthCheck Form
    const truthForm = document.getElementById('truthcheck-form');
    if (truthForm) {
        truthForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const query = document.getElementById('truth-query').value.trim();
            handleAIPost('/api/truthcheck', { query }, 'truth-result', 'truth-loader', 'truthcheck-form');
        });
    }

    // MediSafe Form
    const medisafeForm = document.getElementById('medisafe-form');
    if (medisafeForm) {
        medisafeForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const medicine = document.getElementById('medicine-name').value.trim();
            handleAIPost('/api/medisafe', { medicine }, 'medisafe-result', 'medisafe-loader', 'medisafe-form');
        });
    }

    // DoctorLens Form
    const doctorForm = document.getElementById('doctorlens-form');
    if (doctorForm) {
        doctorForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const doctorName = document.getElementById('doctor-name').value.trim();
            const location = document.getElementById('doctor-location') ? document.getElementById('doctor-location').value.trim() : '';
            handleAIPost('/api/doctorlens', { doctor_name: doctorName, location }, 'doctor-result', 'doctor-loader', 'doctorlens-form');
        });
    }

    // CareFinder Form
    const careForm = document.getElementById('carefinder-form');
    if (careForm) {
        careForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const symptoms = document.getElementById('care-symptoms').value.trim();
            const location = document.getElementById('care-location').value.trim();
            const specialty = document.getElementById('care-specialty') ? document.getElementById('care-specialty').value : '';
            checkEmergencySafety(symptoms);
            handleAIPost('/api/carefinder', { symptoms, location, specialty }, 'care-result', 'care-loader', 'carefinder-form');
        });
    }

    // ClinicScope Form
    const clinicForm = document.getElementById('clinicscope-form');
    if (clinicForm) {
        clinicForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const url = document.getElementById('clinic-url').value.trim();
            handleAIPost('/api/clinicscope', { url }, 'clinic-result', 'clinic-loader', 'clinicscope-form');
        });
    }

    // Sample URL chips on ClinicScope page
    document.querySelectorAll('.sample-urls-bar .chip-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const urlInput = document.getElementById('clinic-url');
            if (urlInput) {
                urlInput.value = btn.dataset.url;
            }
        });
    });

    // LabLens Report Forms (Dashboard tab & Standalone page)
    const setupReportForm = (formId, fileInputId, textInputId, resultId, loaderId, sampleBtnId) => {
        const form = document.getElementById(formId);
        const sampleBtn = document.getElementById(sampleBtnId);
        const textInput = document.getElementById(textInputId);

        if (sampleBtn && textInput) {
            sampleBtn.addEventListener('click', () => {
                textInput.value = "Complete Blood Count & Metabolic Panel:\nHemoglobin: 11.2 g/dL\nFasting Blood Sugar: 146 mg/dL\nHbA1c: 7.1%\nPlatelets: 195000 /mcL\nTotal Cholesterol: 224 mg/dL\nSerum Creatinine: 1.0 mg/dL";
            });
        }

        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const fileInput = document.getElementById(fileInputId);
                const resultBox = document.getElementById(resultId);
                const loader = document.getElementById(loaderId);
                const submitBtn = form.querySelector('button[type="submit"]');

                if (resultBox) resultBox.classList.add('hidden');
                if (loader) loader.classList.remove('hidden');
                if (submitBtn) submitBtn.disabled = true;

                try {
                    let res;
                    if (fileInput && fileInput.files && fileInput.files[0]) {
                        const formData = new FormData();
                        formData.append('file', fileInput.files[0]);
                        res = await fetch('/api/report_analyze', { method: 'POST', body: formData });
                    } else {
                        const reportText = textInput ? textInput.value.trim() : '';
                        if (!reportText) {
                            throw new Error('Please upload a PDF report or paste report text.');
                        }
                        res = await fetch('/api/report_analyze', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ report_text: reportText })
                        });
                    }

                    const data = await res.json();
                    if (!res.ok) throw new Error(data.error || 'Report analysis failed.');

                    if (resultBox) {
                        resultBox.innerHTML = buildResultHTML(data);
                        resultBox.classList.remove('hidden');
                    }
                } catch (err) {
                    if (resultBox) {
                        resultBox.innerHTML = `<div style="color:var(--danger-crimson);padding:1rem;background:var(--danger-light);border-radius:8px;">
                            <strong>Report Notice:</strong> ${err.message}
                        </div>`;
                        resultBox.classList.remove('hidden');
                    }
                } finally {
                    if (loader) loader.classList.add('hidden');
                    if (submitBtn) submitBtn.disabled = false;
                }
            });
        }
    };

    setupReportForm('lablens-form', 'report-file-input', 'report-text-input', 'report-result', 'report-loader', 'load-sample-report-btn');
    setupReportForm('standalone-report-form', 'report-file', 'report-text', 'standalone-report-result', 'standalone-report-loader', 'standalone-sample-btn');

    // CarePrep Doctor Visit Forms (Dashboard tab & Standalone page)
    const setupCarePrepForm = (formId, concernId, timelineId, specialtyId, medsId, allergiesId, questionsId, resultId, loaderId) => {
        const form = document.getElementById(formId);
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                chief_complaint: document.getElementById(concernId).value.trim(),
                timeline: document.getElementById(timelineId) ? document.getElementById(timelineId).value.trim() : '',
                specialty: document.getElementById(specialtyId) ? document.getElementById(specialtyId).value.trim() : '',
                medications: document.getElementById(medsId) ? document.getElementById(medsId).value.trim() : '',
                allergies: document.getElementById(allergiesId) ? document.getElementById(allergiesId).value.trim() : '',
                questions: document.getElementById(questionsId) ? document.getElementById(questionsId).value.trim() : ''
            };

            const resultBox = document.getElementById(resultId);
            const loader = document.getElementById(loaderId);
            const submitBtn = form.querySelector('button[type="submit"]');

            if (resultBox) resultBox.classList.add('hidden');
            if (loader) loader.classList.remove('hidden');
            if (submitBtn) submitBtn.disabled = true;

            try {
                const res = await fetch('/api/visit_prep', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.error || 'Failed to generate visit sheet.');

                if (resultBox) {
                    let html = `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
                        <span class="badge-dot" style="background:#0284c7;"></span>
                        <button type="button" class="primary-btn btn-sm" onclick="window.print()">🖨️ Print / Save as PDF</button>
                    </div>`;
                    html += buildResultHTML(data);
                    resultBox.innerHTML = html;
                    resultBox.classList.remove('hidden');
                }
            } catch (err) {
                if (resultBox) {
                    resultBox.innerHTML = `<div style="color:var(--danger-crimson);">${err.message}</div>`;
                    resultBox.classList.remove('hidden');
                }
            } finally {
                if (loader) loader.classList.add('hidden');
                if (submitBtn) submitBtn.disabled = false;
            }
        });
    };

    setupCarePrepForm('careprep-form', 'prep-concern', 'prep-timeline', 'prep-specialty', 'prep-meds', 'prep-allergies', 'prep-questions', 'careprep-result', 'careprep-loader');
    setupCarePrepForm('standalone-prep-form', 'vp-concern', 'vp-timeline', 'vp-specialty', 'vp-meds', 'vp-allergies', 'vp-questions', 'standalone-prep-result', 'standalone-prep-loader');

    /* ==========================================================================
       10. Interactive 1-Click Guided Demo Scenarios for Judges
       ========================================================================== */
    const demoButtons = document.querySelectorAll('.demo-scenario-btn');
    demoButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const scenario = btn.dataset.scenario;

            if (scenario === 'emergency') {
                switchTab('healthsense-tab');
                const symptomsInput = document.getElementById('hs-symptoms');
                symptomsInput.value = 'Sudden crushing chest pain radiating to left arm and jaw, sweating profusely and dizzy';
                hsForm.dispatchEvent(new Event('submit'));
            } else if (scenario === 'truthcheck') {
                switchTab('truthcheck-tab');
                const truthInput = document.getElementById('truth-query');
                truthInput.value = 'Does cold winter air cause viral colds and fever?';
                truthForm.dispatchEvent(new Event('submit'));
            } else if (scenario === 'medisafe') {
                switchTab('medisafe-tab');
                const medInput = document.getElementById('medicine-name');
                medInput.value = 'Paracetamol';
                medisafeForm.dispatchEvent(new Event('submit'));
            } else if (scenario === 'lablens') {
                switchTab('lablens-tab');
                const reportInput = document.getElementById('report-text-input');
                reportInput.value = "Complete Blood Count:\nHemoglobin: 11.2 g/dL\nFasting Blood Sugar: 145 mg/dL\nHbA1c: 7.2%\nPlatelets: 185000 /mcL\nTotal Cholesterol: 218 mg/dL\nSerum Creatinine: 1.1 mg/dL";
                const labForm = document.getElementById('lablens-form');
                if (labForm) labForm.dispatchEvent(new Event('submit'));
            }
        });
    });

});
