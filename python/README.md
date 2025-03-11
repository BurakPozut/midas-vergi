# Python API for PDF Table Extraction

This directory contains a Flask-based REST API that exposes the PDF table extraction functionality.

## Setup

1. Make sure you have Python 3.8+ installed
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the API

You can run the API using the following command:

```bash
python start_api.py
```

By default, the API will run on port 5000. You can change this by setting the `PORT` environment variable:

```bash
PORT=8000 python start_api.py
```

## API Endpoints

### Health Check

```
GET /health
```

Returns a simple health check response to verify the API is running.

### Extract Tables (File Upload)

```
POST /extract-tables
```

Extracts tables from a PDF file and saves the data to the database. This endpoint accepts a file upload.

**Request Parameters:**

- `file`: The PDF file to process (multipart/form-data)
- `user_id`: The ID of the user who uploaded the file

**Response:**

```json
{
  "success": true,
  "message": "Successfully processed PDF",
  "hasData": true
}
```

Or in case of an error:

```json
{
  "success": false,
  "error": "Error message",
  "hasData": false
}
```

### Process File (From Path)

```
POST /process-file
```

Processes a PDF file that already exists on the server and saves the data to the database.

**Request Body (JSON):**

```json
{
  "file_path": "/absolute/path/to/file.pdf",
  "user_id": "user123"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Successfully processed PDF",
  "hasData": true
}
```

Or in case of an error:

```json
{
  "success": false,
  "error": "Error message",
  "hasData": false
}
```

## Integration with Next.js

In your Next.js application, you need to set the `PYTHON_API_URL` environment variable to point to this API:

```
PYTHON_API_URL=http://localhost:5000
```

The upload route in Next.js will handle file uploads and then call the Python API to process the files.

## Deployment

For production deployment, it's recommended to use a production-ready WSGI server like Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 api:app
```

You can also use Docker to containerize the API:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api:app"]
```
