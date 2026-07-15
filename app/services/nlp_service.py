"""
NLP Service for Resume Analysis
Production Level
"""

import re
from typing import Dict, List
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")


class NLPService:
    SKILLS = [
        # Frontend
        "react", "next.js", "vue", "svelte", "angular",
        "html5", "css3", "tailwind", "typescript", "javascript",
        
        # State Management
        "redux", "zustand", "mobx", "context api",
        
        # Backend
        "python", "flask", "fastapi", "django", "node.js", "express",
        "java", "spring boot", "php", "laravel",
        
        # Databases
        "mongodb", "postgresql", "mysql", "firebase", "redis", "sql",
        
        # Tools & DevOps
        "git", "github", "docker", "kubernetes", "jenkins",
        "aws", "azure", "gcp", "vercel", "netlify",
        
        # Testing
        "jest", "cypress", "vitest",
        
        # Build Tools
        "webpack", "vite", "turborepo",
        
        # Concepts
        "rest api", "graphql", "oop", "data structures", "algorithms",
        "microservices", "machine learning", "artificial intelligence",
    ]

    @staticmethod
    def normalize_skill(skill: str) -> str:
        """
        Normalize skill names to handle variations
        """
        skill = skill.lower().strip()
        
        skill_mapping = {
            # API variations
            "api": "rest api",
            "apis": "rest api",
            "http api": "rest api",
            
            # OOP variations
            "oop": "oop",
            "object-oriented": "oop",
            "object oriented": "oop",
            "oops": "oop",
            
            # Data Science variations
            "ml": "machine learning",
            "ai": "artificial intelligence",
            
            # Frontend variations
            "js": "javascript",
            "ts": "typescript",
            "html": "html5",
            "css": "css3",
            
            # Backend variations
            "py": "python",
            "nodejs": "node.js",
            "node js": "node.js",
            
            # Database variations
            "db": "database",
            
            # DevOps variations
            "k8s": "kubernetes",
            "ci/cd": "ci/cd",
            "cicd": "ci/cd",
        }
        
        return skill_mapping.get(skill, skill)

    @staticmethod
    def analyze_resume(text: str) -> Dict:
        """
        Comprehensive resume analysis using spaCy NLP
        """
        
        if not text:
            return {
                "skills": [],
                "education": [],
                "experience": [],
                "projects": [],
                "certificates": [],
                "keywords": [],
                "email": None,
                "phone": None,
                "word_count": 0
            }

        # Process text with spaCy
        doc = nlp(text)

        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        email = emails[0] if emails else None

        # Extract phone
        phone_pattern = r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'
        phones = re.findall(phone_pattern, text)
        phone = ''.join(phones[0]) if phones else None

        # Extract skills
        unique_skills = set()
        text_lower = text.lower()
        for skill in NLPService.SKILLS:
            if skill.lower() in text_lower:
                unique_skills.add(skill)

        # Normalize skill names
        skills = [s.strip() for s in unique_skills]
        normalized_skills = [NLPService.normalize_skill(s) for s in skills]
        # Remove duplicates after normalization
        skills = list(set([s for s in normalized_skills if s]))

        # Extract education keywords
        education_keywords = ['bachelor', 'master', 'phd', 'btech', 'mtech', 
                            'bca', 'mca', 'diploma', 'degree', 'engineering',
                            'computer science', 'information technology']
        education = [keyword for keyword in education_keywords 
                    if keyword.lower() in text_lower]

        # Extract experience keywords
        experience_keywords = ['intern', 'developer', 'engineer', 'manager',
                              'analyst', 'consultant', 'senior', 'junior',
                              'associate', 'lead', 'architect']
        experience = [keyword for keyword in experience_keywords 
                     if keyword.lower() in text_lower]

        # Extract projects (simple heuristic)
        project_keywords = ['project', 'developed', 'built', 'created', 'designed']
        projects = [keyword for keyword in project_keywords 
                   if keyword.lower() in text_lower]

        # Extract certificates
        certificate_keywords = ['certification', 'certified', 'certificate',
                               'aws certified', 'google certified']
        certificates = [keyword for keyword in certificate_keywords 
                       if keyword.lower() in text_lower]

        # Extract keywords (simple noun extraction)
        keywords = []
        for token in doc:
            if token.pos_ == "NOUN" and len(token.text) > 3:
                keywords.append(token.text.lower())
        keywords = list(set(keywords))[:10]

        # Word count
        word_count = len(text.split())

        return {
            "skills": skills,
            "education": education,
            "experience": experience,
            "projects": projects,
            "certificates": certificates,
            "keywords": keywords,
            "email": email,
            "phone": phone,
            "word_count": word_count
        }


nlp_service = NLPService()
resume_nlp_service = NLPService()