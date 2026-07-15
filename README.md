# 🚀 AI Resume Analyzer

An AI-powered Resume Analyzer built with **FastAPI** that helps job seekers analyze their resumes, improve ATS compatibility, receive AI-based suggestions, and match resumes against job descriptions.

Designed with a clean architecture, secure authentication, and modern backend practices, this project demonstrates real-world FastAPI development using SQLAlchemy, Alembic, Jinja2 Templates, and AI/NLP techniques.

---

## 📌 Project Overview

Recruiters receive thousands of resumes every day. Many resumes are rejected before reaching human recruiters because they fail Applicant Tracking System (ATS) screening.

AI Resume Analyzer helps users:

- Upload resumes
- Analyze ATS compatibility
- Extract resume information
- Compare resumes with job descriptions
- Generate AI-powered improvement suggestions
- Maintain resume history
- Manage user profiles securely

---

# ✨ Features

## 👤 User Authentication

- User Registration
- Secure Login
- Logout
- Password Hashing
- Change Password
- Session Authentication

---

## 📄 Resume Management

- Upload PDF Resume
- Resume Parsing
- Resume History
- Resume Storage
- Resume Details

---

## 🤖 AI Resume Analysis

- ATS Score Generation
- Resume Evaluation
- Skill Extraction
- Resume Insights
- Resume Quality Analysis
- Improvement Suggestions

---

## 🎯 Job Matching

- Compare Resume with Job Description
- Skill Matching
- ATS Compatibility Analysis
- Job Recommendation Support

---

## 📊 Dashboard

- User Dashboard
- Resume History
- Analysis Reports
- ATS Reports

---

## 👤 User Profile

- View Profile
- Edit Profile
- Update Password
- Manage Personal Information

---

## 📧 Contact Module

- Contact Form
- Email Service Integration

---

## 🔒 Security

- Password Hashing
- Session Authentication
- Protected Routes
- Input Validation
- Rate Limiting (SlowAPI)

---

# 🛠 Tech Stack

## Backend

- FastAPI
- Python

## Database

- SQLAlchemy ORM
- Alembic
- SQLite
- PostgreSQL (Production Ready)

## Frontend

- HTML5
- CSS3
- JavaScript
- Jinja2 Templates

## Authentication

- Session Authentication
- Passlib
- Bcrypt

## AI / NLP

- Resume Parsing
- ATS Analysis
- Keyword Matching
- AI Suggestions

## File Processing

- PDF Upload
- Resume Parsing

---

# 📁 Project Structure

```
AI_Resume_Analyzer
│
├── alembic/
├── app/
│   ├── core/
│   ├── database/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── templates/
│   ├── static/
│   ├── uploads/
│   └── main.py
│
├── requirements.txt
├── alembic.ini
├── README.md
└── .gitignore
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/anup06765-svg/Ai_Resume_Analyzer.git

cd Ai_Resume_Analyzer
```

---

## Create Virtual Environment

```bash
python -m venv .venv
```

Activate

Windows

```bash
.venv\Scripts\activate
```

Linux / Mac

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run Database Migration

```bash
alembic upgrade head
```

---

## Run Server

```bash
uvicorn app.main:app --reload
```

Open

```
http://127.0.0.1:8000
```

---

# 🗄 Database

Development

- SQLite

Production

- PostgreSQL

Migration Tool

- Alembic

---

# 📌 Main Modules

- Authentication
- Dashboard
- Resume Upload
- Resume Parsing
- ATS Report
- AI Suggestions
- Job Matching
- Resume History
- User Profile
- Contact

---

# 📊 ATS Analysis

The system evaluates resumes using multiple parameters such as:

- Resume Structure
- Skills
- Keywords
- Experience
- Education
- Projects
- Technical Skills
- Job Description Matching

---

# 🔐 Security Features

- Password Hashing
- Session Management
- Protected Routes
- Rate Limiting
- Input Validation

---

# 🚀 Deployment

Recommended Platforms

- Render
- Railway
- Azure
- AWS
- Google Cloud

---

# 📸 Screenshots

Add screenshots here

- Home Page
- Login
- Dashboard
- Resume Upload
- ATS Report
- AI Suggestions
- Job Matching
- User Profile

---

# 🔮 Future Improvements

- AI Chat Assistant
- Resume Builder
- Cover Letter Generator
- Multiple Resume Comparison
- Interview Question Generator
- Resume Version Control
- Email Notifications
- Resume Templates
- Admin Dashboard
- Analytics Dashboard

---

# 👨‍💻 Author

**Anup Kumar**

GitHub

https://github.com/anup06765-svg

LinkedIn

https://linkedin.com/in/anup32

---

# 📜 License

This project is developed for educational and portfolio purposes.

---

# ⭐ Support

If you like this project,

⭐ Star the repository

🍴 Fork the repository

🐛 Report issues

🤝 Contribute improvements
