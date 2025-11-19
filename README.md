# Promotia Niche Classifier

A web-based system for classifying product images into niches using Google Cloud Vision API.

## Setup

1.  Create a virtual environment: `python3 -m venv venv`
2.  Activate it: `source venv/bin/activate`
3.  Install dependencies: `pip install -r requirements.txt`
4.  Set up Google Cloud Vision credentials (see `.env.example`).
5.  Run the backend: `uvicorn backend.main:app --reload`
