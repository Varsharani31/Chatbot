/**
 * UniGuide Chatbot - Flask Client-Side Logic
 * Interfaces with Flask backend `/api/chat` using Fetch API
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const chatMessages = document.getElementById("chat-messages");
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const themeToggleBtn = document.getElementById("theme-toggle");
    const clearChatBtn = document.getElementById("clear-chat");
    const volumeToggleBtn = document.getElementById("volume-toggle");
    const campusTimeVal = document.getElementById("campus-time");
    const botTypingStatus = document.getElementById("bot-typing");
    const quickRepliesBar = document.getElementById("quick-replies-bar");
    const soundReceive = document.getElementById("sound-msg-receive");
    const soundSend = document.getElementById("sound-msg-send");

    // Session ID generation to keep session memory on Flask server
    const sessionId = "session_" + Math.floor(Math.random() * 10000000);

    // App State Variables
    let soundEnabled = true;
    let isTyping = false;

    // --------------------------------------------------------------------------
    // 1. Time & UI Setup
    // --------------------------------------------------------------------------
    function updateCampusTime() {
        const now = new Date();
        let hours = now.getHours();
        let minutes = now.getMinutes();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12;
        minutes = minutes < 10 ? '0' + minutes : minutes;
        campusTimeVal.textContent = `${hours}:${minutes} ${ampm}`;
    }
    updateCampusTime();
    setInterval(updateCampusTime, 60000);

    // Sound Helpers
    function playAudio(audioEl) {
        if (soundEnabled && audioEl) {
            audioEl.currentTime = 0;
            audioEl.play().catch(err => console.log("Audio play blocked by browser policy."));
        }
    }

    // Theme Switcher
    themeToggleBtn.addEventListener("click", () => {
        const currentTheme = document.documentElement.getAttribute("data-theme");
        const newTheme = currentTheme === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", newTheme);
        
        const themeIcon = themeToggleBtn.querySelector("i");
        if (newTheme === "light") {
            themeIcon.className = "fa-solid fa-sun";
        } else {
            themeIcon.className = "fa-solid fa-moon";
        }
    });

    // Volume Switcher
    volumeToggleBtn.addEventListener("click", () => {
        soundEnabled = !soundEnabled;
        const volIcon = volumeToggleBtn.querySelector("i");
        if (soundEnabled) {
            volIcon.className = "fa-solid fa-volume-high";
            volumeToggleBtn.title = "Mute Sounds";
        } else {
            volIcon.className = "fa-solid fa-volume-xmark";
            volumeToggleBtn.title = "Unmute Sounds";
        }
    });

    // --------------------------------------------------------------------------
    // 2. Chat Rendering Helpers
    // --------------------------------------------------------------------------
    function appendMessage(sender, htmlContent) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `message ${sender}`;

        const avatarImg = document.createElement("img");
        avatarImg.className = "msg-avatar";
        if (sender === "bot") {
            avatarImg.src = "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=UniGuide";
            avatarImg.alt = "UniGuide Bot";
        } else {
            avatarImg.src = "https://api.dicebear.com/7.x/adventurer-neutral/svg?seed=Student";
            avatarImg.alt = "User Avatar";
        }

        const bodyDiv = document.createElement("div");
        bodyDiv.className = "msg-body";

        const bubbleDiv = document.createElement("div");
        bubbleDiv.className = "msg-bubble";

        const timeSpan = document.createElement("span");
        timeSpan.className = "msg-time";
        const now = new Date();
        timeSpan.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        bodyDiv.appendChild(bubbleDiv);
        bodyDiv.appendChild(timeSpan);
        msgDiv.appendChild(avatarImg);
        msgDiv.appendChild(bodyDiv);

        chatMessages.appendChild(msgDiv);

        if (sender === "bot") {
            // Safe HTML Typewriter effect
            let i = 0;
            const speed = 4; // Fast character printing speed (ms)
            function typeStep() {
                if (i < htmlContent.length) {
                    if (htmlContent[i] === '<') {
                        let closeIdx = htmlContent.indexOf('>', i);
                        if (closeIdx !== -1) {
                            bubbleDiv.innerHTML += htmlContent.slice(i, closeIdx + 1);
                            i = closeIdx + 1;
                        } else {
                            bubbleDiv.innerHTML += htmlContent[i];
                            i++;
                        }
                    } else {
                        bubbleDiv.innerHTML += htmlContent[i];
                        i++;
                    }
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                    setTimeout(typeStep, speed);
                } else {
                    // Typewriter done: render clipboard copy and speak read-aloud buttons
                    injectMessageActions(bubbleDiv);
                }
            }
            typeStep();
            playAudio(soundReceive);
        } else {
            bubbleDiv.innerHTML = htmlContent;
            playAudio(soundSend);
        }
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function injectMessageActions(bubbleDiv) {
        // Prevent action list duplication
        if (bubbleDiv.querySelector(".msg-actions")) return;

        const actionsDiv = document.createElement("div");
        actionsDiv.className = "msg-actions";
        
        const copyBtn = document.createElement("button");
        copyBtn.className = "msg-action-btn";
        copyBtn.title = "Copy message";
        copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i>';
        copyBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            // Get text and filter out the button text itself
            let textToCopy = bubbleDiv.innerText.replace(/[\r\n]+/g, '\n').trim();
            navigator.clipboard.writeText(textToCopy).then(() => {
                copyBtn.innerHTML = '<i class="fa-solid fa-check" style="color: #10b981;"></i>';
                setTimeout(() => { copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i>'; }, 1500);
            });
        });

        const speakBtn = document.createElement("button");
        speakBtn.className = "msg-action-btn";
        speakBtn.title = "Read aloud";
        speakBtn.innerHTML = '<i class="fa-solid fa-volume-high"></i>';
        
        let isSpeaking = false;
        speakBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            if (isSpeaking) {
                window.speechSynthesis.cancel();
                isSpeaking = false;
                speakBtn.innerHTML = '<i class="fa-solid fa-volume-high"></i>';
            } else {
                let textToSpeak = bubbleDiv.innerText.trim();
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(textToSpeak);
                utterance.onend = () => {
                    isSpeaking = false;
                    speakBtn.innerHTML = '<i class="fa-solid fa-volume-high"></i>';
                };
                utterance.onerror = () => {
                    isSpeaking = false;
                    speakBtn.innerHTML = '<i class="fa-solid fa-volume-high"></i>';
                };
                speakBtn.innerHTML = '<i class="fa-solid fa-stop" style="color: #ef4444;"></i>';
                isSpeaking = true;
                window.speechSynthesis.speak(utterance);
            }
        });

        actionsDiv.appendChild(copyBtn);
        actionsDiv.appendChild(speakBtn);
        bubbleDiv.appendChild(actionsDiv);
    }

    function showTypingIndicator() {
        if (isTyping) return;
        isTyping = true;
        botTypingStatus.textContent = "UniGuide AI is thinking...";
        
        const indicatorDiv = document.createElement("div");
        indicatorDiv.className = "message bot typing-indicator-wrapper";
        indicatorDiv.id = "typing-indicator";
        
        indicatorDiv.innerHTML = `
            <img class="msg-avatar" src="https://api.dicebear.com/7.x/bottts-neutral/svg?seed=UniGuide" alt="UniGuide Bot">
            <div class="msg-body">
                <div class="msg-bubble" style="padding: 10px 16px;">
                    <div class="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;
        chatMessages.appendChild(indicatorDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeTypingIndicator() {
        if (!isTyping) return;
        isTyping = false;
        botTypingStatus.textContent = "Ready to assist you";
        const indicator = document.getElementById("typing-indicator");
        if (indicator) {
            indicator.remove();
        }
    }

    const defaultReplies = ["Admissions", "Tuition Fees", "Campus Map", "Exam Schedule", "Raise Support Ticket"];

    // --------------------------------------------------------------------------
    // 3. API Communication
    // --------------------------------------------------------------------------
    function handleUserMessage(msgText) {
        if (!msgText.trim()) return;

        // Render User Message
        appendMessage("user", escapeHTML(msgText));
        userInput.value = "";

        // Trigger Typing Effect
        showTypingIndicator();
        
        const personalityVal = document.getElementById("personality-select").value;

        // POST to Flask Backend API
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: msgText,
                session_id: sessionId,
                personality: personalityVal
            })
        })
        .then(res => {
            if (!res.ok) throw new Error("HTTP Status " + res.status);
            return res.json();
        })
        .then(data => {
            removeTypingIndicator();
            appendMessage("bot", data.response);
            renderQuickReplies(data.replies);
        })
        .catch(err => {
            console.error("Flask Server connection error:", err);
            setTimeout(() => {
                removeTypingIndicator();
                appendMessage("bot", `
                    <p><i class="fa-solid fa-triangle-exclamation" style="color: var(--accent-color);"></i> <strong>Flask API Connection Failure.</strong></p>
                    <p>Failed to connect to the Flask server endpoint. Please verify that the Flask server is running locally on port 5000.</p>
                `);
                renderQuickReplies(["Retry request", "Admissions Requirements", "Campus Map"]);
            }, 800);
        });
    }

    // Helper for security
    function escapeHTML(str) {
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }

    // Quick Replies pill rendering
    function renderQuickReplies(replies) {
        quickRepliesBar.innerHTML = "";
        replies.forEach(reply => {
            const pill = document.createElement("button");
            pill.className = "quick-reply-pill";
            pill.textContent = reply;
            pill.addEventListener("click", () => {
                handleUserMessage(reply);
            });
            quickRepliesBar.appendChild(pill);
        });
    }

    // --------------------------------------------------------------------------
    // 4. Action Handlers & Event Listeners
    // --------------------------------------------------------------------------
    
    // Form callbacks bound globally for HTML click overrides
    window.submitTicketEmail = () => {
        const emailVal = document.getElementById("t-email").value;
        handleUserMessage(emailVal);
    };

    window.submitTicketIssue = () => {
        const issueVal = document.getElementById("t-issue").value;
        handleUserMessage(issueVal);
    };

    window.sendQuery = (queryText) => {
        handleUserMessage(queryText);
    };

    // Chat Form Submit
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = userInput.value;
        handleUserMessage(text);
    });

    // Clear conversation
    clearChatBtn.addEventListener("click", () => {
        if (confirm("Reset current Flask session?")) {
            chatMessages.innerHTML = "";
            window.speechSynthesis.cancel();
            // Notify server reset
            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: "back", session_id: sessionId })
            }).then(() => {
                sendGreeting();
            });
        }
    });

    // Sidebar Shortcut buttons
    document.querySelectorAll(".menu-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const query = btn.getAttribute("data-query");
            handleUserMessage(query);
        });
    });

    // Compass Shortcut
    const navShortcutBtn = document.getElementById("nav-shortcut-btn");
    navShortcutBtn.addEventListener("click", () => {
        handleUserMessage("Campus Map");
    });

    // Personality Selection Listener
    const personalitySelect = document.getElementById("personality-select");
    personalitySelect.addEventListener("change", () => {
        const modeText = personalitySelect.options[personalitySelect.selectedIndex].text;
        appendMessage("bot", `<p>🤖 <em>System: Personality has switched to <strong>${modeText}</strong> mode.</em></p>`);
    });

    // Accordion UI Logic
    const gpaHeader = document.getElementById("gpa-accordion-header");
    const tuitionHeader = document.getElementById("tuition-accordion-header");

    function setupAccordion(header, contentId) {
        header.addEventListener("click", () => {
            const content = document.getElementById(contentId);
            
            // Close other accordions
            document.querySelectorAll(".accordion-content").forEach(el => {
                if (el.id !== contentId) {
                    el.classList.remove("show");
                    el.style.maxHeight = null;
                    el.previousElementSibling.classList.remove("active");
                }
            });
            
            header.classList.toggle("active");
            content.classList.toggle("show");
            if (content.classList.contains("show")) {
                content.style.maxHeight = content.scrollHeight + 30 + "px";
            } else {
                content.style.maxHeight = null;
            }
        });
    }

    setupAccordion(gpaHeader, "gpa-calc-content");
    setupAccordion(tuitionHeader, "tuition-calc-content");

    // GPA Calculator Logic
    function calculateGPA() {
        const rows = document.querySelectorAll(".gpa-row");
        let totalPoints = 0;
        let totalCredits = 0;
        
        rows.forEach(row => {
            const gradeVal = parseFloat(row.querySelector(".gpa-grade").value);
            const creditsVal = parseFloat(row.querySelector(".gpa-credits").value) || 0;
            totalPoints += (gradeVal * creditsVal);
            totalCredits += creditsVal;
        });
        
        const gpaVal = totalCredits > 0 ? (totalPoints / totalCredits).toFixed(2) : "0.00";
        document.getElementById("gpa-display").textContent = gpaVal;
    }

    window.addGpaRow = () => {
        const container = document.getElementById("gpa-rows-container");
        const row = document.createElement("div");
        row.className = "gpa-row";
        row.innerHTML = `
            <select class="gpa-grade">
                <option value="4.0">A (4.0)</option>
                <option value="3.0">B (3.0)</option>
                <option value="2.0">C (2.0)</option>
                <option value="1.0">D (1.0)</option>
                <option value="0.0">F (0.0)</option>
            </select>
            <input type="number" class="gpa-credits" value="3" min="1" max="6">
        `;
        container.appendChild(row);
        
        // Attach change listeners to new row inputs
        row.querySelector(".gpa-grade").addEventListener("change", calculateGPA);
        row.querySelector(".gpa-credits").addEventListener("input", calculateGPA);
        
        calculateGPA();
        const content = document.getElementById("gpa-calc-content");
        content.style.maxHeight = content.scrollHeight + 30 + "px";
    };

    // Bind initial listeners for GPA inputs
    document.querySelectorAll(".gpa-grade").forEach(el => el.addEventListener("change", calculateGPA));
    document.querySelectorAll(".gpa-credits").forEach(el => el.addEventListener("input", calculateGPA));
    document.getElementById("add-gpa-row-btn").addEventListener("click", window.addGpaRow);

    // Tuition Calculator Logic
    function calculateTuition() {
        const outOfState = document.getElementById("tuition-out-of-state").checked;
        const housing = document.getElementById("tuition-housing").checked;
        const mealPlan = document.getElementById("tuition-meal-plan").checked;
        
        let cost = 0;
        if (outOfState) {
            cost += 22400;
        } else {
            cost += 9500;
        }
        
        if (housing) {
            cost += 6800;
        }
        
        if (mealPlan) {
            cost += 2500;
        }
        
        document.getElementById("tuition-display").textContent = "$" + cost.toLocaleString();
    }
    
    document.getElementById("tuition-out-of-state").addEventListener("change", calculateTuition);
    document.getElementById("tuition-housing").addEventListener("change", calculateTuition);
    document.getElementById("tuition-meal-plan").addEventListener("change", calculateTuition);

    // Run initial calculations
    calculateGPA();
    calculateTuition();

    // Initial greeting load
    function sendGreeting() {
        showTypingIndicator();
        setTimeout(() => {
            removeTypingIndicator();
            const welcomeText = `
                <h3>👋 Hello! Welcome to UniCampus</h3>
                <p>I am your smart student assistant <strong>UniGuide</strong> running on a Python Flask AI server. I'm here to help you navigate campus life, admissions, exam calendars, tuition payments, and support desk tickets.</p>
                <p>How can I help you today? You can write a query or select a topic from the sidebar and quick replies.</p>
            `;
            appendMessage("bot", welcomeText);
            renderQuickReplies(defaultReplies);
        }, 500);
    }

    sendGreeting();
});
