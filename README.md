# Google LSA Grading

Run sentiment analysis on phone call (conversaion) transcripts.
    
**Minimum Viable Product (MVP)**

1. **input:** phone numbers
2. fetch transcripts from [Podium](https://www.podium.com/about-us/)
3. sentiment analysis on transcripts
4. **output:** graded transcripts
5. broswer agent performs actions based on output.

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