# Google LSA Grading

Run sentiment analysis on phone call (conversaion) transcripts.
    
**Minimum Viable Product (MVP)**

1. **input:** phone numbers
2. fetch transcripts from [Podium](https://www.podium.com/about-us/)
3. sentiment analysis on transcripts
4. **output:** graded transcripts
5. output used to fill out glsa forms

## 1. Running Application

Hosting on Replit

```bash
python app.py
```

## 2. Developer Notes

### 2.1 Running Individual Scripts

Run  `podium.py`, to web scrape a list of phone numbers from podium, e.g.,

```bash
python podium.py uploaded_09JUN2025.json
```

### 2.2 Virtual Enviornment
Setup
```bash
python -m venv glsag_app_env
```
Activate: Command Prompt (cmd)
```bash
glsag_app_env\Scripts\activate
```
Activate: Powershell (ps)
```bash
.\glsag_app_env\Scripts\Activate.ps1
```
Install Dependancies
```bash
pip install -r requirements.txt
```
Deactivate
```bash
deactivate
```

## **Architecture**

```
GoogleLSAGrading/
│
├── main.py                          # Entry point (Replit runs this)
├── config.py                        # Configuration settings
├── requirements.txt                 # Python dependencies
├── .gitignore
├── README.md
│
├── app/
│   ├── __init__.py                 # App factory, db initialization
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── job.py                  # PipelineJob model
│   │   ├── customer.py             # CustomerRecord model
│   │   └── log.py                  # ProgressLog model
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── dashboard.py            # Main UI routes (/, /upload, /jobs)
│   │   ├── jobs.py                 # Job detail routes (/job/<id>)
│   │   └── api.py                  # API/webhook endpoints
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── csv_processor.py        # Parse and validate CSV files
│   │   ├── podium_client.py        # Podium API integration
│   │   ├── sentiment_analyzer.py   # OpenAI sentiment analysis
│   │   └── google_forms.py         # Google Forms/Sheets submission
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── pipeline.py             # Main pipeline orchestration
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── auth.py                 # API credential management
│   │   ├── validators.py           # Input validation helpers
│   │   └── logger.py               # Logging configuration
│   │
│   ├── templates/
│   │   ├── base.html               # Master template (navbar, footer, common structure)
│   │   │
│   │   ├── components/             # Reusable template pieces
│   │   │   ├── navbar.html
│   │   │   ├── footer.html
│   │   │   ├── job_card.html
│   │   │   └── alert.html
│   │   │
│   │   ├── dashboard/
│   │   │   ├── index.html          # Main dashboard (extends base.html)
│   │   │   └── upload.html         # CSV upload page
│   │   │
│   │   ├── jobs/
│   │   │   ├── list.html           # All jobs listing
│   │   │   ├── detail.html         # Job details page
│   │   │   └── progress.html       # Real-time progress view (SSE)
│   │   │
│   │   └── errors/
│   │       ├── 404.html
│   │       └── 500.html
│   │
│   └── static/
│       ├── css/
│       │   ├── main.css            # Single consolidated stylesheet
│       │   └── animations.css      # Page transition animations
│       │
│       ├── js/
│       │   ├── main.js             # Shared JavaScript
│       │   ├── progress.js         # SSE progress tracking
│       │   └── upload.js           # CSV upload handling
│       │
│       └── images/
│           └── logo.png
│
├── uploads/                        # Temporary CSV storage (gitignored)
├── logs/                           # Application logs (gitignored)
└── instance/
    └── pipeline.db                 # SQLite database (gitignored)
```