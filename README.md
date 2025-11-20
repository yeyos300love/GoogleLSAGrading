# Google LSA Grading

Run sentiment analysis on phone call (conversaion) transcripts.
    
**Minimum Viable Product (MVP)**

1. **Input:** Monthly GLSA lead CSV
2. Add or fetch transcripts from [Podium](https://www.podium.com/about-us/)
3. Run sentiment analysis on transcripts
4. Fill out GLSA forms based on grade

## 1. Running Application

Hosting on Replit

```bash
python main.py
```

## 2. Developer Notes

### 2.1 Virtual Enviornment
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
```bash
playwright install
```
Deactivate
```bash
deactivate
```

### 2.2 Architecture

```
GoogleLSAGrading/
│
├── main.py                          # entry point
├── config.py                        # configuration settings
├── requirements.txt                 # python dependencies
├── .gitignore
├── README.md
│
├── .replit                          # replit run configuration
├── replit.nix                       # replit environment packages
│
├── app/
│   ├── __init__.py                 # app factory, db initialization
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── job.py                  # PipelineJob db model
│   │   ├── lead.py                 # Lead db model
│   │   └── prompt.py               # Prompt db model
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── dashboard.py            # main page UI routes (/, /upload)
│   │   ├── jobs.py                 # job detail routes (/job/<id>)
│   │   └── settings.py             # app setting routes (get_prompt)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── browser_agent.py        # browser-use agent
│   │   ├── browser_utils.py        # common browser functions
│   │   ├── csv_processor.py        # parse CSV files
│   │   ├── glsa_client.py          # Fill out GLSA forms
│   │   ├── podium_client.py        # Podium automation
│   │   └── sentiment_analyzer.py   # OpenAI sentiment analysis
│   │
│   ├── templates/
│   │   ├── base.html               # master template common structure
│   │   │
│   │   ├── components/             # reusable template pieces
│   │   │   └── navbar.html
│   │   │
│   │   ├── dashboard/
│   │   │   ├── index.html           # main dashboard
│   │   │   └── loading.html         # display loading streams
│   │   │
│   │   ├── jobs/
│   │   │   ├── list.html           # all jobs listing
│   │   │   ├── detail.html         # job details page
│   │   │   ├── glsa.html           # GLSA login page
│   │   │   └── podium.html         # Podium login
│   │   │    
│   │   ├── settings/
│   │   │   ├── options.html        # all settings
│   │   │
│   │   └── errors/
│   │       ├── 404.html
│   │       └── 500.html
│   │
│   └── static/
│       ├── css/
│       │   ├── main.css            # single consolidated stylesheet
│       │   └── animations.css      # loading robot animations
│       │
│       └── js/
│           ├── 2fa.js              # handle podium 2fa code
│           ├── edit-prompt.js      # handle pompt edits
│           ├── grade-dropdown.js   # dropdown menu logic
│           ├── grade-save.js       # save all grade changes
│           ├── loading.js          # display stream message
│           ├── modal.js            # transcript popup
│           ├── turing-test.js      # handle glsa login
│           └── upload.js           # CSV upload handling
│
├── uploads/                        # temporary CSV storage (gitignored)
└── instance/
    └── pipeline.db                 # SQLite database (gitignored)
```
