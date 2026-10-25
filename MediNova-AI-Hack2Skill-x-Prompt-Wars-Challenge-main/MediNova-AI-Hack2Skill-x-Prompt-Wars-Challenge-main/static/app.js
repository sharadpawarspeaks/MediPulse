document.addEventListener('DOMContentLoaded', () => {
    // Mobile menu toggle
    const hamburger = document.getElementById('hamburger');
    const mobileMenu = document.getElementById('mobile-menu');
    if(hamburger) {
        hamburger.addEventListener('click', () => {
            mobileMenu.classList.toggle('active');
        });
    }

    // Tabs logic for index.html
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {

        tabBtns.forEach(b => b.classList.remove("active"));

        tabPanes.forEach(p => {
            p.classList.remove("active");
            p.classList.add("hidden");
        });

        btn.classList.add("active");

        const target = document.getElementById(
            btn.dataset.target
        );

        target.classList.remove("hidden");
        target.classList.add("active");
        });
    });

    const renderMarkdown = (text) => {
        return typeof marked !== 'undefined' ? marked.parse(text) : text;
    };

    const buildResultHTML = (data) => {
        let html = '';
        
        // Confidence
        if(data.confidence) {
            html += `<span class="confidence-badge conf-${data.confidence}">AI Confidence: ${data.confidence}</span>`;
        }
        
        // Main Content
        html += `<div>${renderMarkdown(data.content)}</div>`;
        
        // Smart Follow Ups
        if(data.follow_up_questions && data.follow_up_questions.length > 0) {
            html += `<div class="follow-ups">
                        <h4>Intelligent Follow-up Questions:</h4>
                        <ul>`;
            data.follow_up_questions.forEach(q => {
                html += `<li>${q}</li>`;
            });
            html += `</ul></div>`;
        }

        // Sources
        if(data.sources && data.sources.length > 0) {
            html += `<div class="sources-list">
                        <h4>Sources/Citations:</h4>
                        <ul>`;
            data.sources.forEach(s => {
                html += `<li>${s}</li>`;
            });
            html += `</ul></div>`;
        }
        
        return html;
    };

    const checkEmergency = async (symptoms) => {
        try {
            const res = await fetch('/api/lifealert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symptoms })
            });
            const data = await res.json();
            const banner = document.getElementById('global-emergency-banner');
            const textEl = document.getElementById('emergency-text');
            
            if(data.is_emergency && banner) {
                textEl.innerText = `${data.warning_message} - ${data.recommendation}`;
                banner.classList.remove('hidden');
            } else if(banner) {
                banner.classList.add('hidden');
            }
        } catch(e) {
            console.error("Emergency check failed", e);
        }
    };

    const handleAIFetch = async (url, body, resultId, loaderId, formId) => {
        const resultBox = document.getElementById(resultId);
        const loader = document.getElementById(loaderId);
        const form = document.getElementById(formId);
        const submitBtn = form.querySelector('button');
        
        resultBox.classList.add("hidden");
        // loader.classList.add("hidden");
        submitBtn.disabled = true;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            
            if(!response.ok) throw new Error("Server response was not ok");
            
            const data = await response.json();
            resultBox.innerHTML = buildResultHTML(data);
            resultBox.classList.remove('hidden');
        } catch(error) {
            resultBox.innerHTML = `<p style="color:red;">Error: Failed to process request. Please ensure the server is running and try again.</p>`;
            resultBox.classList.remove('hidden');
        } finally {
            // loader.classList.remove("hidden");
            submitBtn.disabled = false;
        }
    };

    const hsForm = document.getElementById('healthsense-form');
    if(hsForm) {
        hsForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const symptoms = document.getElementById('hs-symptoms').value;
            checkEmergency(symptoms); // Run lifealert in parallel
            handleAIFetch('/api/healthsense', { symptoms }, 'hs-result', 'hs-loader', 'healthsense-form');
        });
    }

    const preventForm = document.getElementById('prevent-form');
    if(preventForm) {
        preventForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const focus = document.getElementById('prevent-focus').value;
            handleAIFetch('/api/prevent', { focus_area: focus }, 'prevent-result', 'prevent-loader', 'prevent-form');
        });
    }

    const truthForm = document.getElementById('truthcheck-form');
    if(truthForm) {
        truthForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const query = document.getElementById('truth-query').value;
            handleAIFetch('/api/truthcheck', { query }, 'truth-result', 'truth-loader', 'truthcheck-form');
        });
    }

    const medisafeForm = document.getElementById('medisafe-form');
    if(medisafeForm) {
        medisafeForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const medicine = document.getElementById('medicine-name').value;
            handleAIFetch('/api/medisafe', { medicine }, 'medisafe-result', 'medisafe-loader', 'medisafe-form');
        });
    }

    const doctorForm = document.getElementById('doctorlens-form');
    if(doctorForm) {
        doctorForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const name = document.getElementById('doctor-name').value;
            handleAIFetch('/api/doctorlens', { doctor_name: name }, 'doctor-result', 'doctor-loader', 'doctorlens-form');
        });
    }

    const careForm = document.getElementById('carefinder-form');
    if(careForm) {
        careForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const symptoms = document.getElementById('care-symptoms').value;
            handleAIFetch('/api/carefinder', { symptoms }, 'care-result', 'care-loader', 'carefinder-form');
        });
    }

    const clinicForm = document.getElementById('clinicscope-form');
    if(clinicForm) {
        clinicForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const url = document.getElementById('clinic-url').value;
            handleAIFetch('/api/clinicscope', { url }, 'clinic-result', 'clinic-loader', 'clinicscope-form');
        });
    }

    const chatForm = document.getElementById('healthgpt-form');
    const chatMessages = document.getElementById('chat-messages');
    let chatHistory = "";

    if(chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const inputEl = document.getElementById('chat-input');
            const message = inputEl.value.trim();
            if(!message) return;

            // Render User Message
            const userDiv = document.createElement('div');
            userDiv.className = 'message msg-user';
            userDiv.textContent = message;
            chatMessages.appendChild(userDiv);
            
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            inputEl.value = '';
            document.getElementById('chat-loader').classList.remove('hidden');

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ history: chatHistory, input: message })
                });
                const data = await res.json();
                
                // Render AI Message
                const aiDiv = document.createElement('div');
                aiDiv.className = 'message msg-ai';
                aiDiv.innerHTML = renderMarkdown(data.content);
                chatMessages.appendChild(aiDiv);
                
                // Append to history
                chatHistory += `User: ${message}\nAI: ${data.content}\n`;
                
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } catch(e) {
                console.error("Chat error", e);
                const errorDiv = document.createElement('div');
                errorDiv.className = 'message msg-ai';
                errorDiv.style.color = 'red';
                errorDiv.textContent = "Connection error. Please try again.";
                chatMessages.appendChild(errorDiv);
            } finally {
                document.getElementById('chat-loader').classList.add('hidden');
            }
        });
    }
});