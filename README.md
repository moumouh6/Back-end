# Platform Backend

This is the backend service for the platform, built with FastAPI.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
- Copy `.env.example` to `.env`
- Update the values in `.env` as needed

## Running the Application

To start the development server:
```bash
python main.py
```

The server will start at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

- `main.py`: Main application file
- `requirements.txt`: Project dependencies
- `.env`: Environment variables
- `models/`: Database models
- `routes/`: API routes
- `services/`: Business logic
- `utils/`: Utility functions 