# 📄 Intellewings Assessments – Affidavit Data Extraction System

This project automatically **extracts user information and PAN details from affidavit PDFs** using **OCR + Gemini AI**, stores the structured data in **MySQL**, and displays the output on a **React frontend**.

It is fully **containerized using Docker**, so setup is reproducible.

---

## 🚀 What This Project Does

- Accepts **affidavit PDFs** from users
- Uses **Tesseract OCR (Hindi + English)** to extract raw text
- Uses **Gemini 2.5 Flash** to convert unstructured text into clean JSON
- Detects and extracts:
  - Name
  - Age
  - Phone
  - Address
  - PAN number
- Stores extracted data automatically in **MySQL**
- Displays the extracted JSON on a **React (Vite) frontend**

---

## 📂 Project Structure

```
Intellewings assesments/
│
├── venv/                    # Local virtual environment (not used in Docker)
├── sample_pdfs/             # Sample/input affidavit PDFs
├── backend/                 
│   ├── app.py               # Backend entry point
|   ├── functions.py         # OCR+Gemini and all importand functions
│   ├── Dockerfile           # Installs Python deps + Tesseract
│   ├── .env                 # Gemini API key
│   └── requirements.txt
│
├── frontend/                # React (Vite) frontend
│   ├── src/
│      ├── App.jsx           # User Interface
│   └── package.json
│
├── .env                     # MySQL environment variables
├── docker-compose.yml       # Orchestrates backend + MySQL
├── .gitignore
└── README.md
```

---

## 🛠️ Prerequisites

Make sure you have the following installed:

- **Docker Desktop** (must be running)
- **npm**

You do **NOT** need to install:

- Python
- MySQL
- Tesseract

Docker handles all of that.

---

## 🔐 Environment Variables Setup

### 1️⃣ Root `.env` file

Create a `.env` file in the **root directory**.

⚠️ **Important clarification about MySQL password**:

- This password is **NOT** your local system's MySQL password.
- It is a password **only for the MySQL Docker container**.
- You can choose **any password you like**.

Create the file as shown below:

```
MYSQL_ROOT_PASSWORD=tiger
MYSQL_DATABASE=affidavit_db
```

This is used by the **MySQL container**.

---

### 2️⃣ Backend `.env` file

Create a `.env` file inside the `backend/` folder:

```
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
```

⚠️ **Important**:

- Gemini model used: **gemini-2.5-flash**

---

## 🐳 Docker Setup (Backend + MySQL)

### Step 1: Start Docker Desktop

Make sure Docker Desktop is running before proceeding.

---

### Step 2: Build & Run Containers

From the **root directory**:

```
docker compose up --build
```

This will:

- Build the backend image
- Install Tesseract OCR inside the container
- Start MySQL
- Auto-create database & tables

Backend will run on:

```
http://localhost:8000
```

---

## 🗄️ Database Details

- Database: `affidavit_db`
- Tables are **auto-created** on startup

### Table: `extracted_data`

```
id          INT (PK, auto increment)
name        VARCHAR(255)
age         INT
phone       VARCHAR(20)
pan         VARCHAR(20)
address     TEXT
created_at  TIMESTAMP (auto-generated)
```

No manual SQL execution required.

---

## 🌐 Frontend Setup (React + Vite)

### Step 1: Navigate to frontend

```
cd frontend
```

### Step 2: Install dependencies

```
npm install
```

### Step 3: Start frontend

```
npm run dev
```

Frontend will be available at:

```
http://localhost:5173
```

The frontend sends PDFs to:

```
POST http://localhost:8000/extract
```

---

## 📥 Input & 📤 Output

### Input

- **PDF files only**
- Must contain affidavit content and PAN card

### Output

- JSON response shown on frontend
- Same data stored in MySQL

Example response:

```
{
  "name": "Rajeev Ranjan",
  "age": 26,
  "phone": "73197029",
  "pan": "CHCPR9394A",
  "address": "ग्राम पोस्ट करमा..."
}
```

---

## 🧠 OCR & AI Pipeline

1. PDF uploaded from frontend
2. Flask backend receives file
3. PDF converted to images
4. Tesseract OCR extracts Hindi + English text
5. Logic detects the pages where user and pan details are mentioned
6. Gemini fetches, cleans & structures data
7. Data validated
8. Stored in MySQL
9. JSON returned to frontend

---

## 🧯 Common Issues & Fixes

### ❌ MySQL connection error

- Ensure `.env` exists in root
- Ensure Docker Desktop is running

### ❌ Gemini API error

- Check API key validity
- Ensure backend `.env` file exists

##

---

## 🧑‍💻 Author

**Pranjal Raghuvanshi**

---

## ⭐ Final Notes

- One command backend setup
- Zero manual DB work
- Production-ready architecture
- Resume & interview friendly project

If it runs in Docker, it runs everywhere. 🚀

