"""
NLP Service
Production Level Resume Information Extractor

Features:
- Name extraction
- Email extraction
- Phone extraction
- Skills extraction
- Education extraction
- Experience extraction
- Project extraction
- Certificate extraction
- Keyword extraction
- Word count
"""

import re
from typing import Dict, List

try:
    import spacy

    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        nlp = None

except ImportError:
    nlp = None


class NLPService:

    # ----------------------------------------
    # Skills Database
    # ----------------------------------------

    SKILLS = {

        "python",
        "java",
        "c",
        "c++",

        "html",
        "css",
        "javascript",
        "typescript",

        "django",
        "fastapi",
        "flask",

        "react",
        "node",

        "mysql",
        "postgresql",
        "mongodb",
        "sqlite",

        "git",
        "github",

        "docker",
        "kubernetes",

        "linux",

        "aws",
        "azure",

        "machine learning",
        "deep learning",
        "natural language processing",
        "nlp",

        "tensorflow",
        "pytorch",

        "opencv",

        "numpy",
        "pandas",
        "matplotlib",

        "sql",

        "rest api",
        "api",

        "data structures",
        "algorithms",

        "oop",
        "dbms"

    }


    # ----------------------------------------
    # Education Keywords
    # ----------------------------------------

    EDUCATION_KEYWORDS = [

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

        "bachelor",
        "master",

        "computer science",
        "information technology",

        "engineering",

        "university",
        "college"

    ]


    # ----------------------------------------
    # Certificate Keywords
    # ----------------------------------------

    CERTIFICATE_KEYWORDS = [

        "certificate",
        "certification",

        "hackerrank",
        "coursera",
        "udemy",
        "nptel",

        "aws certified"

    ]


    # ----------------------------------------
    # Clean Text
    # ----------------------------------------

    @staticmethod
    def clean_text(text: str) -> str:

        if not text:
            return ""

        text = text.lower()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()


    # ----------------------------------------
    # Name Extraction
    # ----------------------------------------

    @staticmethod
    def extract_name(text: str):

        if nlp:

            try:

                doc = nlp(text)

                for entity in doc.ents:

                    if entity.label_ == "PERSON":

                        return entity.text

            except Exception:
                pass


        lines = text.split("\n")


        for line in lines:

            line = line.strip()


            if (
                len(line) > 3
                and len(line.split()) <= 4
                and not "resume" in line.lower()
            ):

                return line


        return ""


    # ----------------------------------------
    # Email Extraction
    # ----------------------------------------

    @staticmethod
    def extract_email(text: str):

        pattern = (
            r"[A-Za-z0-9._%+-]+"
            r"@[A-Za-z0-9.-]+"
            r"\.[A-Za-z]{2,}"
        )


        match = re.search(
            pattern,
            text
        )


        return match.group(0) if match else ""


    # ----------------------------------------
    # Phone Extraction
    # ----------------------------------------

    @staticmethod
    def extract_phone(text: str):

        pattern = (
            r"(\+91[\-\s]?)?"
            r"[6-9]\d{9}"
        )


        match = re.search(
            pattern,
            text
        )


        return match.group(0) if match else ""


    # ----------------------------------------
    # Skills Extraction
    # ----------------------------------------

    @classmethod
    def extract_skills(cls, text: str):

        cleaned = cls.clean_text(text)

        skills = []


        for skill in cls.SKILLS:

            if skill in cleaned:

                skills.append(skill)


        return sorted(
            list(set(skills))
        )


    # ----------------------------------------
    # Education Extraction
    # ----------------------------------------

    @classmethod
    def extract_education(cls, text: str):

        cleaned = cls.clean_text(text)

        education = []


        for item in cls.EDUCATION_KEYWORDS:

            if item in cleaned:

                education.append(item)


        return sorted(
            list(set(education))
        )


    # ----------------------------------------
    # Experience Extraction
    # ----------------------------------------

    @staticmethod
    def extract_experience(text: str):

        experience = []


        pattern = (
            r"\d+\+?\s*"
            r"(year|years|month|months)"
        )


        matches = re.findall(
            pattern,
            text.lower()
        )


        for item in matches:

            experience.append(item)


        keywords = [

            "internship",
            "intern",
            "developer",
            "engineer",
            "worked",
            "experience"

        ]


        lower = text.lower()


        for word in keywords:

            if word in lower:

                experience.append(word)


        return sorted(
            list(set(experience))
        )


    # ----------------------------------------
    # Projects Extraction
    # ----------------------------------------

    @staticmethod
    def extract_projects(text: str):

        projects = []


        keywords = [

            "project",
            "projects",
            "developed",
            "built",
            "github"

        ]


        lines = text.split("\n")


        for line in lines:

            for keyword in keywords:

                if keyword in line.lower():

                    projects.append(
                        line.strip()
                    )


        return list(
            set(projects)
        )


    # ----------------------------------------
    # Certificates
    # ----------------------------------------

    @classmethod
    def extract_certificates(cls, text: str):

        cleaned = cls.clean_text(text)

        certificates = []


        for item in cls.CERTIFICATE_KEYWORDS:

            if item in cleaned:

                certificates.append(item)


        return sorted(
            list(set(certificates))
        )


    # ----------------------------------------
    # Keyword Extraction
    # ----------------------------------------

    @staticmethod
    def extract_keywords(text: str):

        words = re.findall(
            r"[a-zA-Z]{3,}",
            text.lower()
        )


        return sorted(
            list(set(words))
        )


    # ----------------------------------------
    # Word Count
    # ----------------------------------------

    @staticmethod
    def word_count(text: str):

        return len(
            text.split()
        )


    # ----------------------------------------
    # Complete Resume Analysis
    # ----------------------------------------

    @classmethod
    def analyze_resume(
        cls,
        text: str
    ) -> Dict:


        return {

            "name":
                cls.extract_name(text),

            "email":
                cls.extract_email(text),

            "phone":
                cls.extract_phone(text),

            "skills":
                cls.extract_skills(text),

            "education":
                cls.extract_education(text),

            "experience":
                cls.extract_experience(text),

            "projects":
                cls.extract_projects(text),

            "certificates":
                cls.extract_certificates(text),

            "keywords":
                cls.extract_keywords(text),

            "word_count":
                cls.word_count(text)

        }


# Service Object
nlp_service = NLPService()

# Backward compatibility
resume_nlp_service = NLPService()

