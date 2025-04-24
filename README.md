# Google LSA Grading

Run sentiment analysis on phone call (conversaion) transcripts.
    
**Minimum Viable Product (MVP)**

1. **input:** phone numbers
2. fetch transcripts from [Podium](https://www.podium.com/about-us/)
3. sentiment analysis on transcripts
4. **output:** graded transcripts

## 1. Running Application

### 1.1 All: Docker

Containerizing application for deployment & scalability.

Running Container(s)
```bash
docker compose up
```
Build Image: `yeyos_projs`
```bash
docker build -t yeyos_projs:GLSA_grading .
```
Run Container
```bash
docker run -p 8080:5001 yeyos_projs:GLSA_grading
```
View Containers
```bash
docker ps -a
```

## 2. Developer Notes

### 2.1 Test Mode

Application has two modes, determined by the `TestDataUse` class in `app.py`.

- **Test Data Mode**: When `TestDataUse` is set to `True`, the application will use predefined test data found in `sample_data`.

- **Production Mode**: When `TestDataUse` class is set to `False`, the application will expect either user-uploaded data (e.g., from a CSV file) or correctly fetched data.

### 2.2 Running Individual Scripts

Run  `podium.py`, to web scrape a list of phone numbers from podium, e.g.,

```bash
python podium.py '(971) 998-9211', '(509) 637-5941'
```

### 2.3 Virtual Enviornment
```bash
python -m venv glsag_app_env
```
```bash
glsag_app_env\Scripts\activate
```
```bash
pip install -r requirements.txt
```
```bash
deactivate
```