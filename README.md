# UniGuide: Intelligent College Campus Chatbot

UniGuide is a premium, modern college campus assistant chatbot built using a **Python Flask backend** and **Google Gemini AI** integration. It provides students, prospective applicants, and parents with instant answers to common questions about admissions, tuition fees, exam schedules, campus navigation, and support.

---

## 🌟 Key Features

* **Dual Response Processing**: Integrates Google Gemini AI for smart, freeform conversation, and a robust stateful offline rule engine when running without an API key.
* **Assistant Modes (Bot Personalities)**: A dropdown selector dynamically changes the bot's communication tone:
  - **Academic Advisor**: Professional, serious, focus on admissions and exams.
  - **Campus Tour Guide**: Casual, energetic, emoji-rich, focus on campus hotspots.
  - **IT Service Desk**: Direct, troubleshooting-focused step-by-step assistant.
* **Interactive Conversational UI**: Fully responsive frontend featuring premium glassmorphism styling, glowing hover effects, sound cues, and dark/light modes.
* **Interactive Student Tools**: Sidebar widgets calculating details on-the-fly:
  - **GPA Calculator**: Add courses, select grades, and input credit values to get real-time GPA estimates.
  - **Tuition Cost Estimator**: Check/uncheck options for state residency, campus housing, and meal plans to calculate customized cost profiles.
* **Admissions Portal**: Highlights application timelines and steps, and provides direct simulation links.
* **Interactive Campus Mapping**: Renders an inline SVG campus layout with glowing buildings. Clicking on any building automatically queries the chatbot for details.
* **Stateful Support Desk**: Initiates a session state machine to log support tickets directly to a local SQLite database (`tickets.db`), outputting confirmation codes (`TCK-XXXXXX`).
* **Message Utilities**: Hover overlays containing clipboard copying and Web Speech Synthesis (Text-to-Speech) readout features.
* **Ready-Made Reports**: Compiled Microsoft Word (`.docx`) and PDF (`.pdf`) submission documents.

---

## 📂 Project Structure

```text
Chatbot/
├── app.py                      # Flask Server and chatbot logic
├── requirements.txt            # Python dependencies
├── generate_docs.py            # Report generator script
├── templates/
│   └── index.html              # HTML Layout template
├── static/
│   ├── app.js                  # Frontend client controller
│   └── style.css               # Vanilla CSS design stylesheet
├── assets/                     # High-res screenshot mockups
│   ├── welcome_screen.png
│   ├── admission_faq.png
│   ├── navigation_flow.png
│   └── fallback_handling.png
├── UniGuide_Assignment_Submission.docx   # Compiled Word Report
├── UniGuide_Assignment_Submission.pdf    # Compiled PDF Report
└── tickets.db                  # Local SQLite Database (auto-generated)
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Varsharani31/Chatbot.git
cd Chatbot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
python app.py
```
By default, the server runs on **[http://localhost:5000](http://localhost:5000)**.

### 4. Enable Google Gemini AI (Optional)
To use live AI models instead of the offline rules matching, set your API key as an environment variable before launching the server:
* **Windows (Command Prompt)**:
  ```cmd
  set GEMINI_API_KEY=your_gemini_api_key_here
  python app.py
  ```
* **Windows (PowerShell)**:
  ```powershell
  $env:GEMINI_API_KEY="your_gemini_api_key_here"
  python app.py
  ```
* **Linux/macOS**:
  ```bash
  export GEMINI_API_KEY="your_gemini_api_key_here"
  python app.py
  ```

---

## 📊 Document Compilation
If you need to re-generate the assignment submission documents:
```bash
python generate_docs.py
```
This compiles `UniGuide_Assignment_Submission.docx` and `UniGuide_Assignment_Submission.pdf`.
