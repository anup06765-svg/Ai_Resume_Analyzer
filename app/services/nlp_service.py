import re
import spacy
from typing import Dict, List

# Load spaCy model only once
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None


class ResumeNLPService:

    SKILLS = {
        "python", "java", "c", "c++", "django", "fastapi", "flask",
        "html", "css", "javascript", "react", "node", "mysql",
        "postgresql", "mongodb", "sqlite", "git", "github",
        "docker", "kubernetes", "aws", "azure", "linux",
        "machine learning", "deep learning", "tensorflow",
        "pytorch", "opencv", "pandas", "numpy", "matplotlib",
        "sql", "rest api", "api", "data structures",
        "oop", "dbms"
    }

    EDUCATION = [
        "b.tech",
        "btech",
        "b.e",
        "be",
        "m.tech",
        "mtech",
        "bca",
        "mca",
        "b.sc",
        "msc",
        "computer science",
        "information technology",
        "engineering"
    ]

    PROJECT_KEYWORDS = [
        "project",
        "projects",
        "internship",
        "experience"
    ]

    def extract_email(self, text: str):

        pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

        match = re.search(pattern, text)

        return match.group(0) if match else None

    def extract_phone(self, text: str):

        pattern = r"(\+?\d[\d\s\-]{8,15}\d)"

        match = re.search(pattern, text)

        return match.group(0) if match else None

    def extract_name(self, text: str):

        if not nlp:
            return None

        doc = nlp(text)

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text

        return None

    def extract_skills(self, text: str):

        text_lower = text.lower()

        found = []

        for skill in self.SKILLS:
            if skill in text_lower:
                found.append(skill.title())

        return sorted(list(set(found)))

    def extract_education(self, text: str):

        text_lower = text.lower()

        education = []

        for item in self.EDUCATION:
            if item in text_lower:
                education.append(item.title())

        return sorted(list(set(education)))

    def extract_projects(self, text: str):

        lines = text.split("\n")

        projects = []

        for line in lines:

            line = line.strip()

            if len(line) < 4:
                continue

            for keyword in self.PROJECT_KEYWORDS:

                if keyword.lower() in line.lower():

                    projects.append(line)

        return list(set(projects))

    def extract_keywords(self, text: str):

        if not nlp:
            return []

        doc = nlp(text)

        keywords = []

        for token in doc:

            if token.is_stop:
                continue

            if token.is_punct:
                continue

            if len(token.text) < 3:
                continue

            keywords.append(token.text)

        return sorted(list(set(keywords)))

    def extract_experience(self, text: str):

        pattern = r"(\d+)\+?\s*(years|year|months|month)"

        matches = re.findall(pattern, text.lower())

        experience = []

        for item in matches:
            experience.append(" ".join(item))

        return experience

    def analyze_resume(self, text: str) -> Dict:

        return {
            "name": self.extract_name(text),
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "skills": self.extract_skills(text),
            "education": self.extract_education(text),
            "experience": self.extract_experience(text),
            "projects": self.extract_projects(text),
            "keywords": self.extract_keywords(text),
        }


resume_nlp_service = ResumeNLPService()