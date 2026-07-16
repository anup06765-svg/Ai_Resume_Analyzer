# 🤖 AI Resume Analyzer

An AI-powered Resume Analyzer built using **FastAPI**, **HTML/CSS**, **SQLite**, and **Natural Language Processing (NLP)**. This application helps users upload resumes, analyze ATS compatibility, compare resumes with Job Descriptions, receive AI-generated improvement suggestions, and manage their profiles through a secure authentication system.

---

## 📌 Project Overview

The AI Resume Analyzer is designed to assist job seekers in improving their resumes before applying for jobs.

The system extracts information from uploaded PDF resumes, analyzes the content using NLP techniques, calculates an ATS (Applicant Tracking System) score, compares resumes against job descriptions, and provides AI-generated suggestions to improve resume quality.

The application also includes secure user authentication, password management, dashboards, report generation, and contact management.

---

# ✨ Features

## 🔐 User Authentication

- User Registration
- Secure Login
- Logout
- Password Hashing
- Change Password
- Forgot Password Support
- Protected Dashboard
- Session Management

---

## 📄 Resume Management

- Upload Resume (PDF)
- Store Uploaded Resume
- Resume Parsing
- Resume Information Extraction
- Resume Analysis
- Resume History

---

## 🤖 AI Resume Analysis

- Resume Content Analysis
- Skill Identification
- Keyword Extraction
- Missing Skills Detection
- Resume Strength Analysis
- Resume Weakness Analysis
- Professional Suggestions
- Resume Summary Generation

---

## 🎯 ATS Resume Score

The project calculates an ATS Score based on:

- Resume Structure
- Skills Matching
- Keywords
- Formatting
- Contact Information
- Experience Section
- Education Section
- Projects
- Certifications

Example:

```
ATS Score: 87/100
```

---

## 💼 Job Description Matching

Users can paste any Job Description.

The system compares:

- Skills
- Keywords
- Technologies
- Experience
- Responsibilities

Then displays:

- Matching Percentage
- Missing Keywords
- Suggested Improvements

---

## 💡 AI Suggestions

The application provides suggestions like:

- Add missing technical skills
- Improve project descriptions
- Include measurable achievements
- Improve formatting
- Add certifications
- Optimize keywords
- Improve ATS compatibility

---

## 📊 Dashboard

Dashboard contains:

- Total Uploaded Resumes
- ATS Score
- Resume Analysis
- AI Suggestions
- Job Matching Result
- User Profile
- Analysis History

---

## 👤 User Profile

Users can:

- Update Name
- Update Email
- Change Password
- View Analysis History

---

## 📬 Contact System

The project includes a contact module where users can submit:

- Name
- Email
- Subject
- Message

---

## 📑 Report Generation

Generate detailed reports including:

- ATS Score
- Resume Summary
- Missing Skills
- Suggested Improvements
- Job Matching Percentage

---

# 🛠 Tech Stack

## Backend

- FastAPI
- Python

## Frontend

- HTML5
- CSS3
- JavaScript

## Database

- SQLite
- SQLAlchemy ORM

## Authentication

- Password Hashing
- Session Authentication

## AI / NLP

- spaCy
- NLP Processing
- Resume Parsing
- Keyword Matching

## PDF Processing

- PyMuPDF
- PDF Text Extraction

---

# 📂 Project Structure

```
AI_Resume_Analyzer/
│
├── app/
│   ├── auth/
│   ├── core/
│   ├── crud/
│   ├── database/
│   ├── dependencies/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── static/
│   ├── templates/
│   ├── uploads/
│   └── main.py
│
├── alembic/
├── requirements.txt
├── run.py
├── runtime.txt
└── resume_analyzer.db
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/anup06765-svg/AI_Resume_Analyzer.git
```

---

## Move into Project

```bash
cd AI_Resume_Analyzer
```

---

## Create Virtual Environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run Server

```bash
python run.py
```

or

```bash
uvicorn app.main:app --reload
```

---

## Open Browser

```
http://127.0.0.1:8000
```

---

# 📸 Main Modules

- Home Page
- Register
- Login
- Dashboard
- Resume Upload
- Resume Analysis
- ATS Report
- AI Suggestions
- Job Description Matching
- Contact Page
- User Profile
- Change Password

---

# 📈 Workflow

```
User Registration
        │
        ▼
User Login
        │
        ▼
Upload Resume
        │
        ▼
Extract Resume Text
        │
        ▼
AI Resume Analysis
        │
        ▼
ATS Score Calculation
        │
        ▼
Job Description Matching
        │
        ▼
AI Suggestions
        │
        ▼
Dashboard & Reports
```

---

# 🔒 Security Features

- Password Hashing
- Secure Authentication
- Protected Routes
- Database Validation
- Form Validation
- Error Handling
- Session Protection

---

# 🎯 Future Improvements

- OpenAI Integration
- Gemini API Integration
- Multi-language Resume Support
- Resume Templates
- Cover Letter Generator
- Interview Question Generator
- Resume Ranking
- LinkedIn Profile Analyzer
- PDF Report Export
- Email Notification
- Admin Panel
- Cloud Deployment
- PostgreSQL Support

---

# 💼 Learning Outcomes

This project demonstrates knowledge of:

- FastAPI
- REST API Development
- SQLAlchemy ORM
- Authentication
- NLP
- Resume Parsing
- ATS Scoring
- AI-based Recommendation Systems
- File Upload Handling
- Database Management
- Web Application Development

---

# 👨‍💻 Author

**Anup Kumar**

- 🎓 B.Tech CSE Student
- 💻 Python Backend Developer
- 🌐 FastAPI Developer
- 🧠 AI & NLP Enthusiast

GitHub:
https://github.com/anup06765-svg

LinkedIn:
https://linkedin.com/in/anup32

---

# ⭐ Support

If you found this project helpful:

⭐ Star the repository

🍴 Fork the project

🛠 Contribute with new features

🐛 Report bugs

---

# 📜 License

This project is developed for educational and learning purposes.

Feel free to use and modify it for personal, academic, or portfolio projects.

---

## 🌟 Thank You

Thank you for visiting this project.

If you like this project, don't forget to ⭐ Star the repository.
