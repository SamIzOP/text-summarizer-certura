# Flask Text Summarizer

A simple web application that summarizes text using Flask and spaCy.

## Installation

1. Install dependencies:
```bash
pip install flask spacy
python -m spacy download en_core_web_sm
```

2. Run the application:
```bash
python app.py
```

3. Open http://localhost:5000 in your browser

## Usage

- Paste text in the input area
- Choose number of sentences for summary
- Click "Analyze with spaCy" button
- View the generated summary and statistics

## API

**POST /api/summarize**
```json
{
    "text": "Your text here",
    "num_sentences": 3
}
```

**GET /api/examples/{type}**
- Available types: ai, climate, space

**GET /health**
- Check if the application is running

## Files

- `app.py` - Main Flask application
- `templates/index.html` - Web interface

## Requirements

- Python 3.7+
- Flask
- spaCy with English model
