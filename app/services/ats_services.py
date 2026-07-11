"""
ATS Scoring Service
Production Level
"""

from typing import Dict
from app.services.nlp_service import NLPService


class ATSService:
    REQUIRED_SKILLS = [
        "python","django","fastapi","flask","html","css","javascript",
        "sql","mysql","mongodb","git","github","docker","linux","rest api"
    ]

    @classmethod
    def _grade(cls, score:int)->str:
        if score>=90: return "A+"
        if score>=80: return "A"
        if score>=70: return "B"
        if score>=60: return "C"
        if score>=50: return "D"
        return "F"

    @classmethod
    def calculate(cls, resume_text:str)->Dict:
        if not resume_text:
            return {
                "ats_score":0,
                "ats_grade":"F",
                "analysis":{},
                "matched_skills":[],
                "missing_skills":cls.REQUIRED_SKILLS,
                "suggestions":["Resume text is empty."]
            }

        analysis = NLPService.analyze_resume(resume_text)

        skills = analysis.get("skills",[])
        education = analysis.get("education",[])
        experience = analysis.get("experience",[])
        projects = analysis.get("projects",[])
        certificates = analysis.get("certificates",[])
        keywords = analysis.get("keywords",[])
        word_count = analysis.get("word_count",0)

        matched = [s for s in cls.REQUIRED_SKILLS if s in [x.lower() for x in skills]]
        missing = [s for s in cls.REQUIRED_SKILLS if s not in matched]

        score = 0
        suggestions = []

        score += min(40, int((len(matched)/len(cls.REQUIRED_SKILLS))*40))

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

        score += 10 if education else 0
        if not education:
            suggestions.append("Add education details.")

        score += 10 if projects else 0
        if not projects:
            suggestions.append("Add project section.")

        score += 10 if experience else 0
        if not experience:
            suggestions.append("Add internship/work experience.")

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

        score = min(100, score)

        return {
            "ats_score": score,
            "ats_grade": cls._grade(score),
            "analysis": analysis,
            "word_count": word_count,
            "matched_skills": matched,
            "missing_skills": missing,
            "breakdown": {
                "skills": min(40, int((len(matched)/len(cls.REQUIRED_SKILLS))*40)),
                "resume_length": 20 if word_count>=500 else 16 if word_count>=350 else 12 if word_count>=250 else 8 if word_count>=150 else 4,
                "education":10 if education else 0,
                "projects":10 if projects else 0,
                "experience":10 if experience else 0,
                "contact":contact
            },
            "suggestions": suggestions
        }


ats_service = ATSService()
