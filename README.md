# UniGuide: Intelligent College Campus Chatbot

UniGuide is a premium, modern college campus assistant chatbot built using a **Python Flask backend** and **Google Gemini AI** integration. It provides students, prospective applicants, and parents with instant answers to common questions about admissions, tuition fees, exam schedules, campus navigation, and support.

---

## 🌟 Key Features

* **Dual response processing**: Integrates Google Gemini AI for smart, freeform conversation, and a robust fallback rule engine when running offline.
* **Interactive Conversational UI**: Responsive design featuring glassmorphism, glowing accents, sound effects, and dark/light themes.
* **Admissions Portal**: Highlights application timelines and steps, and provides direct simulation links.
* **Interactive Navigation**: Renders a top-down simulated campus map with locator pins.
* **Stateful Support Desk**: Allows users to raise a student support ticket, collecting emails, descriptions, and logging a ticket ID.
* **Ready-Made Reports**: Compiled Microsoft Word (`.docx`) and PDF (`.pdf`) submission documents.

---

## 📂 Project Structure

```text
UniGuide-Chatbot/
├── app.py                      # Flask Server and NLP logic
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
├── UniGuide_Assignment_Submission.docx   # Word Report
└── UniGuide_Assignment_Submission.pdf    # PDF Report
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
