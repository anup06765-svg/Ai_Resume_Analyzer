"""
Universal ATS Scoring Service - Works for ALL profiles
"""

from typing import Dict
from app.services.nlp_service import NLPService


class ATSService:
    
    # Universal skills (sabhi ke liye zaroori)
    UNIVERSAL_SKILLS = [
        "git", "rest api", "oop", "data structures", "algorithms"
    ]
    
    # Profile-specific skills
    PROFILE_SKILLS = {
        "Frontend": {
            "required": ["react", "html5", "css3", "javascript", "typescript", "git", "rest api"],
            "bonus": ["next.js", "tailwind", "redux", "webpack", "jest"]
        },
        "Backend": {
            "required": ["python", "git", "rest api", "sql", "oop", "data structures"],
            "bonus": ["flask", "fastapi", "django", "postgresql", "mongodb"]
        },
        "Full-Stack": {
            "required": ["react", "python", "javascript", "git", "rest api", "sql", "oop"],
            "bonus": ["next.js", "flask", "django", "typescript", "docker"]
        },
        "Mobile": {
            "required": ["java", "kotlin", "swift", "react native", "git", "oop"],
            "bonus": ["firebase", "rest api", "ui design"]
        },
        "DevOps": {
            "required": ["git", "docker", "kubernetes", "linux", "rest api", "aws"],
            "bonus": ["jenkins", "terraform", "ci/cd"]
        },
        "Data Science": {
            "required": ["python", "sql", "data structures", "algorithms", "git"],
            "bonus": ["pandas", "numpy", "tensorflow", "machine learning"]
        }
    }

    @classmethod
    def detect_profile_type(cls, skills: list) -> str:
        """
        Automatically detect developer profile type
        """
        skills_lower = [s.lower() for s in skills]
        
        # Detection logic
        frontend_keywords = {"react", "next.js", "vue", "angular", "svelte", "html", "css", "tailwind", "typescript"}
        backend_keywords = {"python", "flask", "django", "fastapi", "node.js", "express", "java", "spring", "php", "laravel"}
        mobile_keywords = {"java", "kotlin", "swift", "react native", "flutter", "android", "ios"}
        devops_keywords = {"docker", "kubernetes", "jenkins", "terraform", "aws", "azure", "ci/cd"}
        data_keywords = {"pandas", "numpy", "tensorflow", "machine learning", "sklearn", "r", "sql"}
        
        frontend_count = sum(1 for s in skills_lower if s in frontend_keywords)
        backend_count = sum(1 for s in skills_lower if s in backend_keywords)
        mobile_count = sum(1 for s in skills_lower if s in mobile_keywords)
        devops_count = sum(1 for s in skills_lower if s in devops_keywords)
        data_count = sum(1 for s in skills_lower if s in data_keywords)
        
        counts = {
            "Frontend": frontend_count,
            "Backend": backend_count,
            "Mobile": mobile_count,
            "DevOps": devops_count,
            "Data Science": data_count
        }
        
        # If Frontend + Backend both high, it's Full-Stack
        if frontend_count > 0 and backend_count > 0 and frontend_count > 2 and backend_count > 2:
            return "Full-Stack"
        
        # Return highest match
        detected = max(counts, key=counts.get)
        return detected if counts[detected] > 0 else "General"

    @classmethod
    def _grade(cls, score: int) -> str:
        if score >= 90: return "A+"
        if score >= 80: return "A"
        if score >= 70: return "B"
        if score >= 60: return "C"
        if score >= 50: return "D"
        return "F"

    @classmethod
    def calculate(cls, resume_text: str) -> Dict:
        """
        Universal calculation for ANY profile type
        """
        if not resume_text:
            return {
                "ats_score": 0,
                "ats_grade": "F",
                "profile_type": "Unknown",
                "analysis": {},
                "matched_skills": [],
                "missing_skills": cls.UNIVERSAL_SKILLS,
                "suggestions": ["Resume text is empty."]
            }

        # Analyze resume
        analysis = NLPService.analyze_resume(resume_text)

        skills = analysis.get("skills", [])
        education = analysis.get("education", [])
        experience = analysis.get("experience", [])
        projects = analysis.get("projects", [])
        word_count = analysis.get("word_count", 0)

        # Detect profile type
        profile_type = cls.detect_profile_type(skills)

        # Get expected skills for this profile
        if profile_type in cls.PROFILE_SKILLS:
            required_skills = cls.PROFILE_SKILLS[profile_type]["required"]
            bonus_skills = cls.PROFILE_SKILLS[profile_type]["bonus"]
            all_expected = required_skills + bonus_skills
        else:
            required_skills = cls.UNIVERSAL_SKILLS
            bonus_skills = []
            all_expected = required_skills

        # Match skills
        skills_lower = [x.lower() for x in skills]
        matched = [s for s in all_expected if s in skills_lower]
        missing = [s for s in required_skills if s not in matched]

        score = 0
        suggestions = []

        # Skill matching score (40 points max)
        skill_score = min(40, int((len(matched) / len(all_expected)) * 40)) if all_expected else 0
        score += skill_score

        # Resume length score (20 points max)
        if word_count >= 500:
            score += 20
        elif word_count >= 350:
            score += 16
        elif word_count >= 250:
            score += 12
        elif word_count >= 150:
            score += 8
            suggestions.append("Increase resume length to 400-500 words.")
        else:
            score += 4
            suggestions.append("Resume is too short.")

        # Education (10 points)
        score += 10 if education else 0
        if not education:
            suggestions.append("Add education details.")

        # Projects (10 points)
        score += 10 if projects else 0
        if not projects:
            suggestions.append("Add project section with actual projects you built.")

        # Experience (10 points)
        score += 10 if experience else 0
        if not experience:
            suggestions.append("Add internship/work experience section.")

        # Contact info (10 points)
        contact = 0
        if analysis.get("email"):
            contact += 5
        else:
            suggestions.append("Email address not found.")
        if analysis.get("phone"):
            contact += 5
        else:
            suggestions.append("Phone number not found.")
        score += contact

        # Cap score at 100
        score = min(100, score)

        # Add missing skills suggestions
        if missing:
            missing_text = ", ".join(missing[:3])
            suggestions.append(f"Learn or improve: {missing_text}")

        return {
            "ats_score": score,
            "ats_grade": cls._grade(score),
            "profile_type": profile_type,
            "analysis": analysis,
            "word_count": word_count,
            "matched_skills": matched,
            "missing_skills": missing,
            "breakdown": {
                "skills": skill_score,
                "resume_length": 20 if word_count >= 500 else 16 if word_count >= 350 else 12 if word_count >= 250 else 8 if word_count >= 150 else 4,
                "education": 10 if education else 0,
                "projects": 10 if projects else 0,
                "experience": 10 if experience else 0,
                "contact": contact
            },
            "suggestions": suggestions
        }


ats_service = ATSService()