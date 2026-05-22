import os
import re
import random
import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# SQLite Database setup
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tickets.db")

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            email TEXT,
            issue TEXT,
            status TEXT DEFAULT 'Pending Review',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Stateful sessions memory simulator (In-memory dict for demonstration)
# Keeps track of user session state, e.g. ticket emails or issues
session_states = {}

# --------------------------------------------------------------------------
# Google Gemini AI Integration Config
# --------------------------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
has_gemini = False

if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        has_gemini = True
        print("Gemini AI API successfully configured on backend!")
    except Exception as e:
        print(f"Error configuring Gemini AI: {e}. Falling back to Rule Engine.")

# --------------------------------------------------------------------------
# Rule-Based Knowledge Base
# --------------------------------------------------------------------------
KNOWLEDGE_BASE = [
    {
        "keys": ["admission", "apply", "enrol", "enroll", "registration", "application"],
        "tags": ["admissions"],
        "response": """
            <h3>🎓 Admissions & Registration (Fall 2026)</h3>
            <p>Welcome! Applying to UniCampus is straightforward. Follow this path:</p>
            <ol>
                <li>Submit your online form at our <a href="#" onclick="window.sendQuery('Apply Link')">Admissions Portal</a></li>
                <li>Upload high school transcripts & test scores</li>
                <li>Provide 2 letters of recommendation & personal statement</li>
            </ol>
            <div class="chat-card">
                <span class="chat-card-title"><i class="fa-solid fa-bell"></i> Application Deadline</span>
                <span class="chat-card-content">Early Action: Nov 15 | Regular Decision: Jan 15</span>
                <div class="chat-card-actions">
                    <button class="chat-action-btn" onclick="window.sendQuery('Fees & Scholarships')">Check Tuition Fees</button>
                </div>
            </div>
        """,
        "replies": ["Apply Link", "Admission Deadlines", "Tuition Fees"]
    },
    {
        "keys": ["fee", "fees", "cost", "scholarship", "financial aid", "tuition", "payment"],
        "tags": ["fees"],
        "response": """
            <h3>💳 Tuition & Financial Support</h3>
            <p>UniCampus values affordable education. Annual costs before scholarships:</p>
            <ul>
                <li><strong>In-State Tuition:</strong> $9,500 / year</li>
                <li><strong>Out-of-State:</strong> $22,400 / year</li>
                <li><strong>Campus Housing:</strong> $6,800 / year (Double Room)</li>
            </ul>
            <p>Need-based & merit scholarships are open. Over 75% of our students receive aid!</p>
            <div class="chat-card font-size-12">
                <span class="chat-card-title"><i class="fa-solid fa-calculator"></i> Support Calculator</span>
                <span class="chat-card-content">Use our support calculator tool to gauge your monthly payment schedules.</span>
                <div class="chat-card-actions">
                    <button class="chat-action-btn" onclick="window.sendQuery('Scholarship Application')">Apply for Scholarships</button>
                </div>
            </div>
        """,
        "replies": ["Scholarships Info", "Payment Plans", "Housing Costs"]
    },
    {
        "keys": ["map", "location", "library", "gym", "dorm", "cafeteria", "directions", "where is", "navigate", "campus"],
        "tags": ["navigation"],
        "response": """
            <h3>📍 Interactive Campus Navigation</h3>
            <p>Finding your way around UniCampus is easy. Here is our interactive central campus layout:</p>
            
            <div class="svg-map-container">
                <svg viewBox="0 0 400 220" class="interactive-svg-map">
                    <!-- Background Grid / Path -->
                    <rect width="400" height="220" rx="8" fill="var(--bg-primary)" stroke="var(--border-color)" stroke-width="1.5"/>
                    
                    <!-- Campus Pathways / Roads -->
                    <path d="M 50 110 L 350 110 M 200 30 L 200 190" stroke="var(--border-color)" stroke-width="12" stroke-linecap="round" opacity="0.6"/>
                    <path d="M 50 110 L 350 110 M 200 30 L 200 190" stroke="var(--primary-light)" stroke-width="2" stroke-dasharray="4 4" stroke-linecap="round" opacity="0.4"/>
                    
                    <!-- Center Plaza -->
                    <circle cx="200" cy="110" r="22" fill="var(--bg-secondary)" stroke="var(--primary-color)" stroke-width="2"/>
                    <text x="200" y="113" font-size="8" fill="var(--text-primary)" text-anchor="middle" font-weight="bold">Plaza</text>
                    
                    <!-- Library (North) -->
                    <g class="map-building" onclick="window.sendQuery('Founder\'s Library')">
                        <rect x="150" y="15" width="100" height="35" rx="4" fill="rgba(99, 102, 241, 0.12)" stroke="var(--primary-color)" stroke-width="1.5"/>
                        <text x="200" y="36" font-size="9" fill="var(--text-primary)" text-anchor="middle" font-weight="600">📚 Library</text>
                    </g>
                    
                    <!-- Gym (West) -->
                    <g class="map-building" onclick="window.sendQuery('Apex Gym')">
                        <rect x="25" y="85" width="80" height="50" rx="4" fill="rgba(99, 102, 241, 0.12)" stroke="var(--primary-color)" stroke-width="1.5"/>
                        <text x="65" y="114" font-size="9" fill="var(--text-primary)" text-anchor="middle" font-weight="600">🏋️ Gym</text>
                    </g>
                    
                    <!-- Diner (East) -->
                    <g class="map-building" onclick="window.sendQuery('Lakeside Diner')">
                        <rect x="295" y="85" width="80" height="50" rx="4" fill="rgba(99, 102, 241, 0.12)" stroke="var(--primary-color)" stroke-width="1.5"/>
                        <text x="335" y="114" font-size="9" fill="var(--text-primary)" text-anchor="middle" font-weight="600">🍔 Diner</text>
                    </g>
                    
                    <!-- Dorms (South) -->
                    <g class="map-building" onclick="window.sendQuery('Student Dorms')">
                        <rect x="150" y="165" width="100" height="40" rx="4" fill="rgba(99, 102, 241, 0.12)" stroke="var(--primary-color)" stroke-width="1.5"/>
                        <text x="200" y="189" font-size="9" fill="var(--text-primary)" text-anchor="middle" font-weight="600">🏢 Dorms</text>
                    </g>
                </svg>
                <div class="map-overlay-hint">💡 Click any building on the map above to view its details!</div>
            </div>
            
            <p><strong>Popular Hotspots:</strong></p>
            <ul>
                <li><strong>Founder's Library:</strong> North end (Open 24/7 during finals)</li>
                <li><strong>Apex Recreation Center:</strong> West end next to Stadium</li>
                <li><strong>Lakeside Diner (Food Court):</strong> Next to Main Auditorium</li>
            </ul>
        """,
        "replies": ["Founder's Library", "Apex Gym", "Lakeside Diner", "Student Dorms"]
    },
    {
        "keys": ["exam", "exams", "test", "finals", "midterm", "calendar", "schedule", "holiday", "dates"],
        "tags": ["academic"],
        "response": """
            <h3>📅 Academic Calendar & Exam Schedule</h3>
            <p>Keep track of important academic checkposts for the 2026 Term:</p>
            <ul>
                <li><strong>Midterm Exams:</strong> October 12 – 18, 2026</li>
                <li><strong>Thanksgiving Holiday:</strong> November 25 – 29, 2026</li>
                <li><strong>Final Examinations:</strong> December 14 – 20, 2026</li>
            </ul>
            <div class="chat-card">
                <span class="chat-card-title"><i class="fa-solid fa-triangle-exclamation"></i> Exam Policy Notice</span>
                <span class="chat-card-content">Ensure to display your Student ID card. Makeup exams require dean's authorization.</span>
            </div>
        """,
        "replies": ["Exam Policy Details", "Dean's Contact Info", "Holiday List"]
    },
    {
        "keys": ["ticket", "support", "complain", "help", "contact", "support ticket", "raise ticket", "advisor"],
        "tags": ["support"],
        "response": """
            <h3>🛠️ Raise a Campus Support Ticket</h3>
            <p>Need direct help from a student advisor or registrar? Let's raise a ticket. Let's start with your email:</p>
            <div class="chat-card">
                <span class="chat-card-title"><i class="fa-solid fa-headset"></i> Support Desk Ticket Form</span>
                <div class="ticket-form" id="ticket-step-1">
                    <input type="email" placeholder="Enter student/applicant email" class="ticket-input" id="t-email" required>
                    <button class="ticket-submit-btn" onclick="submitTicketEmail()">Next <i class="fa-solid fa-arrow-right"></i></button>
                </div>
            </div>
        """,
        "replies": ["General Advising", "Contact Registrar", "Emergency Contacts"]
    }
]

DEFAULT_REPLIES = ["Admissions", "Tuition Fees", "Campus Map", "Exam Schedule", "Raise Support Ticket"]

# --------------------------------------------------------------------------
# Helper functions for Offline Engine
# --------------------------------------------------------------------------
def get_offline_response(user_msg, session_id, personality="advisor"):
    clean_msg = user_msg.lower().strip()
    state = session_states.get(session_id, {"step": None, "email": "", "issue": ""})

    # SQLite Ticket Lookup Logic
    ticket_match = re.search(r"tck-\d{6}", clean_msg)
    if ticket_match or "lookup" in clean_msg or "status" in clean_msg:
        search_id = ticket_match.group(0).upper() if ticket_match else None
        if not search_id:
            num_match = re.search(r"\b\d{6}\b", clean_msg)
            if num_match:
                search_id = f"TCK-{num_match.group(0)}"
        
        if search_id:
            try:
                conn = sqlite3.connect(DATABASE)
                cursor = conn.cursor()
                cursor.execute("SELECT email, issue, status, created_at FROM tickets WHERE ticket_id = ?", (search_id,))
                row = cursor.fetchone()
                conn.close()
                if row:
                    email_reg, issue_reg, status_reg, created_reg = row
                    return {
                        "response": f"""
                            <h3>🔍 Support Ticket Found</h3>
                            <div class="chat-card">
                                <span class="chat-card-title"><i class="fa-solid fa-ticket"></i> {search_id}</span>
                                <span class="chat-card-content">
                                    <strong>Registered Email:</strong> {email_reg}<br>
                                    <strong>Status:</strong> <span style="color: var(--accent-color); font-weight: bold;">{status_reg}</span><br>
                                    <strong>Created At:</strong> {created_reg}<br>
                                    <strong>Details:</strong> "{issue_reg}"
                                </span>
                            </div>
                        """,
                        "replies": DEFAULT_REPLIES
                    }
                else:
                    return {
                        "response": f"""
                            <h3>❌ Ticket Not Found</h3>
                            <p>We couldn't find a support ticket with ID <strong>{search_id}</strong> in our database.</p>
                            <p>Please double check the ticket ID or try raising a new support request.</p>
                        """,
                        "replies": ["Raise Support Ticket"] + DEFAULT_REPLIES
                    }
            except Exception as e:
                print(f"Database query error: {e}")

    # Specific Campus Buildings Flow
    if "library" in clean_msg:
        return {
            "response": """
                <h3>📚 Founder's Library</h3>
                <p>Located on the <strong>North side</strong> of the Central Plaza.</p>
                <ul>
                    <li><strong>Hours:</strong> Open 24/7 during midterm and final exam weeks. Otherwise, 7:00 AM – 11:00 PM.</li>
                    <li><strong>Resources:</strong> Silent study floors (3rd & 4th), group discussion hubs (1st & 2nd), IT Helpdesk inside, and Lakeside coffee cart.</li>
                </ul>
            """,
            "replies": ["Campus Map", "Exam Schedule"]
        }
    if "gym" in clean_msg or "apex" in clean_msg:
        return {
            "response": """
                <h3>🏋️ Apex Recreation Center (Gym)</h3>
                <p>Located on the <strong>West side</strong> of the Central Plaza, adjacent to the Lakeside Football Stadium.</p>
                <ul>
                    <li><strong>Hours:</strong> 6:00 AM – 10:00 PM (Monday – Sunday).</li>
                    <li><strong>Features:</strong> Olympic swimming pool, indoor basketball courts, climbing wall, and personal training rooms. Student entry is free with a valid Student ID card.</li>
                </ul>
            """,
            "replies": ["Campus Map", "Raise Support Ticket"]
        }
    if "diner" in clean_msg or "cafeteria" in clean_msg or "food" in clean_msg:
        return {
            "response": """
                <h3>🍔 Lakeside Diner & Food Court</h3>
                <p>Located on the <strong>East side</strong> of the Central Plaza, right next to the Main Auditorium.</p>
                <ul>
                    <li><strong>Hours:</strong> 8:00 AM – 9:00 PM.</li>
                    <li><strong>Vendors:</strong> Pizza Parlor, Fresh Salads Co., Sushi Express, and Vegan Bites. Meal plans are accepted here.</li>
                </ul>
            """,
            "replies": ["Campus Map", "Tuition Fees"]
        }
    if "dorm" in clean_msg or "dorms" in clean_msg or "housing" in clean_msg:
        return {
            "response": """
                <h3>🏢 Student Dormitories</h3>
                <p>Located on the <strong>South side</strong> of the Central Plaza.</p>
                <ul>
                    <li><strong>Options:</strong> Double Room ($6,800/yr) and Single Suite ($8,500/yr).</li>
                    <li><strong>Amenities:</strong> High-speed Wi-Fi, shared kitchens, self-service laundry rooms, and student lounges with TVs.</li>
                </ul>
            """,
            "replies": ["Campus Map", "Tuition Fees"]
        }

    # Step-by-step Ticketing State Machine
    if state["step"] == "WAITING_EMAIL":
        email_regex = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        if re.match(email_regex, clean_msg):
            state["email"] = user_msg
            state["step"] = "WAITING_ISSUE"
            session_states[session_id] = state
            return {
                "response": f"""
                    <p>Got it: <code>{user_msg}</code>. Excellent.</p>
                    <p>Now, <strong>please describe the issue</strong> or details of the request you would like to raise:</p>
                    <div class="chat-card">
                        <div class="ticket-form">
                            <input type="text" placeholder="Explain your support query..." class="ticket-input" id="t-issue" required>
                            <button class="ticket-submit-btn" onclick="submitTicketIssue()">Submit Ticket</button>
                        </div>
                    </div>
                """,
                "replies": ["Cancel Support Request"]
            }
        else:
            return {
                "response": """
                    <p><i class="fa-solid fa-triangle-exclamation" style="color: var(--accent-color);"></i> <strong>Invalid Email Address.</strong></p>
                    <p>Please enter a valid student email address (e.g., <code>student@campus.edu</code>) to proceed with raising your ticket:</p>
                """,
                "replies": ["Cancel Support Request"]
            }

    if state["step"] == "WAITING_ISSUE":
        if clean_msg in ["cancel support request", "cancel"]:
            session_states[session_id] = {"step": None, "email": "", "issue": ""}
            return {
                "response": "<p>Ticket creation has been cancelled. What else can I assist you with?</p>",
                "replies": DEFAULT_REPLIES
            }
        
        ticket_id = f"TCK-{random.randint(100000, 999999)}"
        email_registered = state["email"]
        session_states[session_id] = {"step": None, "email": "", "issue": ""} # reset
        
        # Save to SQLite Database
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tickets (ticket_id, email, issue, status) VALUES (?, ?, ?, ?)",
                (ticket_id, email_registered, user_msg, "Pending Review")
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"SQLite insertion error: {e}")

        return {
            "response": f"""
                <h3>✅ Ticket Raised Successfully!</h3>
                <p>Your request has been logged into our secure SQLite database.</p>
                <div class="chat-card">
                    <span class="chat-card-title"><i class="fa-solid fa-ticket"></i> Ticket ID: {ticket_id}</span>
                    <span class="chat-card-content">
                        <strong>Registered Email:</strong> {email_registered}<br>
                        <strong>Issue:</strong> "{user_msg}"<br>
                        <strong>Status:</strong> <span style="color: var(--accent-color); font-weight: bold;">Pending Review</span>
                    </span>
                    <span class="chat-card-content" style="margin-top: 4px; font-size: 11px; color: var(--accent-color);">
                        Use ticket code <code>{ticket_id}</code> at any time to lookup this ticket's status.
                    </span>
                </div>
            """,
            "replies": DEFAULT_REPLIES
        }

    # Match Knowledge Base Keywords
    for item in KNOWLEDGE_BASE:
        for key in item["keys"]:
            if key in clean_msg:
                if "support" in item["tags"]:
                    state["step"] = "WAITING_EMAIL"
                    session_states[session_id] = state
                return {
                    "response": item["response"],
                    "replies": item["replies"]
                }

    # Custom Specific Dialog Items
    if clean_msg in ["apply link", "apply"]:
        return {
            "response": """
                <h3>🔗 Online Application Portal</h3>
                <p>Please complete your application via the online admissions form:</p>
                <p><a href="#" onclick="alert('Navigating to Secure Application Form Mockup')"><strong>👉 Secure Admission Form (Simulation Portal)</strong></a></p>
                <p>Make sure you have scanned PDF copies of your identification document, academic transcript records, and recommendation letters handy.</p>
            """,
            "replies": ["Admission Deadlines", "Tuition Fees", "Go Back"]
        }

    if clean_msg in ["scholarship application", "scholarships info"]:
        return {
            "response": """
                <h3>🏆 Scholarships & Aid Applications</h3>
                <p>We host several merit-based scholarships which waive up to 100% of academic fees:</p>
                <ul>
                    <li><strong>Presidential Excellence Award:</strong> For GPA 3.9+ (Full waive)</li>
                    <li><strong>STEM Innovator Grant:</strong> For engineering/CS major (Partial waiver)</li>
                    <li><strong>Lakeside Athletic Grant:</strong> Focuses on team sports and athletes</li>
                </ul>
                <p>Forms must be filled before <strong>Feb 15, 2026</strong>. Late submissions are not evaluated.</p>
            """,
            "replies": ["Tuition Fees", "Admissions Requirements", "Go Back"]
        }

    if clean_msg in ["cancel support request", "go back", "back"]:
        session_states[session_id] = {"step": None, "email": "", "issue": ""}
        return {
            "response": "<p>Returning to home options. Let me know what you would like to explore next!</p>",
            "replies": DEFAULT_REPLIES
        }

    # Fallback response
    return {
        "response": f"""
            <h3>🔍 Unrecognized Query</h3>
            <p>I couldn't quite find exact answers for "<em>{user_msg}</em>" in our current database.</p>
            <p>Could you clarify or select from one of our popular topics below?</p>
            <div class="chat-card">
                <span class="chat-card-title"><i class="fa-solid fa-lightbulb"></i> Recommendations</span>
                <span class="chat-card-content">
                    • Use simpler terms (e.g. <em>"fees"</em> instead of <em>"how much is the tuition fee"</em>)<br>
                    • Inquire about <strong>campus map</strong> or <strong>exams schedule</strong><br>
                    • Type <code>lookup TCK-XXXXXX</code> to check a support ticket<br>
                    • Click one of the quick replies below.
                </span>
            </div>
        """,
        "replies": DEFAULT_REPLIES
    }

def apply_personality_tone(text, personality):
    if personality == "guide":
        # Make the rule engine replies sound super energetic and use plenty of emojis!
        text = text.replace("<h3>🎓 Admissions & Registration (Fall 2026)</h3>", "<h3>🎓 Hey there! Welcome to Admissions (Fall 2026) 🌟</h3>")
        text = text.replace("<h3>💳 Tuition & Financial Support</h3>", "<h3>💳 Tuition & Awesome Scholarships! 💸</h3>")
        text = text.replace("<h3>📍 Interactive Campus Navigation</h3>", "<h3>📍 Let's Explore our Beautiful Campus! 🗺️</h3>")
        text = text.replace("<h3>📅 Academic Calendar & Exam Schedule</h3>", "<h3>📅 Academic Calendar & Finals Countdown! 🗓️</h3>")
        text = text.replace("<h3>🛠️ Raise a Campus Support Ticket</h3>", "<h3>🛠️ Let's get you some help! Raise a Ticket 🤝</h3>")
        text = text.replace("<p>Welcome! Applying to UniCampus is straightforward. Follow this path:</p>", "<p>Yay! We are so excited to have you join us. Applying is super simple! Just do these things:</p>")
        text = text.replace("<p>UniCampus values affordable education. Annual costs before scholarships:</p>", "<p>We want to help you get the best education ever without breaking the bank! Check this out:</p>")
    elif personality == "support":
        # Make it sound like a formal IT helpdesk ticketing system
        text = text.replace("<h3>🎓 Admissions & Registration (Fall 2026)</h3>", "<h3>🎓 Admissions Registration Desk</h3>")
        text = text.replace("<h3>💳 Tuition & Financial Support</h3>", "<h3>💳 Billing and Financial Accounts</h3>")
        text = text.replace("<h3>📍 Interactive Campus Navigation</h3>", "<h3>📍 Campus Location Services</h3>")
        text = text.replace("<h3>📅 Academic Calendar & Exam Schedule</h3>", "<h3>📅 System Schedule: Academic Term</h3>")
        text = text.replace("<h3>🛠️ Raise a Campus Support Ticket</h3>", "<h3>🛠️ UniCampus IT Service Desk (L1 Support)</h3>")
        text = text.replace("<p>Welcome! Applying to UniCampus is straightforward. Follow this path:</p>", "<p>Admissions application processing instructions:</p>")
    return text

# --------------------------------------------------------------------------
# Gemini LLM Response Generator (System Prompt Guided)
# --------------------------------------------------------------------------
def get_gemini_response(user_msg, personality="advisor"):
    personality_instructions = {
        "advisor": "You are UniGuide AI, a professional, structured, and helpful Academic Advisor for UniCampus. Focus on terms, requirements, and policy documents.",
        "guide": "You are UniGuide AI, a friendly, energetic, and casual campus tour guide for UniCampus. Use emojis frequently, talk enthusiastically about campus events, hot spots, food courts, and library life.",
        "support": "You are UniGuide AI, a polite, direct, and troubleshooting-oriented IT support specialist. Focus on answering step-by-step help procedures and tracking tickets."
    }
    system_instruction = personality_instructions.get(personality, personality_instructions["advisor"])

    prompt = f"""
    {system_instruction}
    
    Guidelines for responding:
    1. Respond in clean HTML format. Use tags like <h3>, <p>, <ul>, <li>, and <strong>. Avoid raw markdown symbols (*, #).
    2. Answer the student's question accurately. The student asked: "{user_msg}"
    3. Keep responses concise and engaging. 
    4. If relevant, tell them they can also click the buttons in the sidebar or raise a ticket.
    5. Knowledge Context:
       - Tuition: In-state: $9,500/yr, Out-of-state: $22,400/yr, Housing: $6,800/yr.
       - Admissions: Fall 2026 early action is Nov 15, Regular decision is Jan 15. Apply online.
       - Campus landmarks: Founder's Library (North), Apex Gym (West), Lakeside Diner (next to Auditorium).
       - Exams: Midterms are Oct 12-18, Finals are Dec 14-20, 2026.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        text = response.text
        # Clean up code blocks if Gemini returns them
        text = text.replace("```html", "").replace("```", "").strip()
        return {
            "response": text,
            "replies": DEFAULT_REPLIES
        }
    except Exception as e:
        print(f"Gemini generation error: {e}. Falling back to Rule Matcher.")
        return None

# --------------------------------------------------------------------------
# Server Endpoints
# --------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "")
    session_id = data.get("session_id", "default_session")
    personality = data.get("personality", "advisor")

    # Step-by-step ticketing and specific overrides must run on rules engine
    state = session_states.get(session_id, {"step": None, "email": "", "issue": ""})
    is_stateful = state["step"] is not None
    is_direct_override = message.lower().strip() in ["apply link", "apply", "scholarship application", "scholarships info", "cancel support request", "go back", "back"] or "library" in message.lower() or "gym" in message.lower() or "diner" in message.lower() or "dorm" in message.lower() or "lookup" in message.lower() or "tck-" in message.lower()

    if has_gemini and not is_stateful and not is_direct_override:
        # Query Gemini API
        res = get_gemini_response(message, personality)
        if res:
            return jsonify(res)

    # Fallback to local rule engine
    res = get_offline_response(message, session_id, personality)
    # Apply personality transformations to rule engine responses
    res["response"] = apply_personality_tone(res["response"], personality)
    return jsonify(res)

if __name__ == "__main__":
    # Start Flask Server
    app.run(host="0.0.0.0", port=5000, debug=True)
