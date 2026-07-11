import re
from typing import Dict, List, Set

from app.services.nlp_service import ResumeNLPService


class JDMatchingService:
    """
    Production-level Job Description Matching Service
    """

    def __init__(self):
        self.resume_nlp = ResumeNLPService()
        self.available_skills = {
            skill.lower()
            for skill in self.resume_nlp.SKILLS
        }

    def extract_jd_skills(self, jd_text: str) -> List[str]:
        """
        Extract skills from Job Description.
        """

        jd_lower = jd_text.lower()

        skills = []

        for skill in self.available_skills:

            pattern = r"\b" + re.escape(skill) + r"\b"

            if re.search(pattern, jd_lower):
                skills.append(skill.title())

        return sorted(list(set(skills)))

    def calculate_match(
        self,
        resume_skills: List[str],
        jd_skills: List[str],
    ) -> Dict:

        resume_set: Set[str] = {
            skill.lower()
            for skill in resume_skills
        }

        jd_set: Set[str] = {
            skill.lower()
            for skill in jd_skills
        }

        matched = sorted(resume_set & jd_set)

        missing = sorted(jd_set - resume_set)

        extra = sorted(resume_set - jd_set)

        if len(jd_set) == 0:
            percentage = 0
        else:
            percentage = round(
                (len(matched) / len(jd_set)) * 100,
                2
            )

        return {

            "matching_score": percentage,

            "skill_match_percentage": percentage,

            "matched_skills": [
                s.title() for s in matched
            ],

            "missing_skills": [
                s.title() for s in missing
            ],

            "extra_skills": [
                s.title() for s in extra
            ]
        }

    def generate_ai_suggestions(
        self,
        missing_skills: List[str]
    ) -> List[str]:

        suggestions = []

        if not missing_skills:

            suggestions.append(
                "Excellent! Your resume already covers all major skills required for this job."
            )

            return suggestions

        for skill in missing_skills:

            suggestions.append(
                f"Add practical experience or projects related to {skill}."
            )

        suggestions.append(
            "Customize your resume according to this Job Description."
        )

        suggestions.append(
            "Include measurable achievements and relevant keywords."
        )

        return suggestions

    def analyze(
        self,
        resume_skills: List[str],
        jd_text: str
    ) -> Dict:

        jd_skills = self.extract_jd_skills(
            jd_text
        )

        result = self.calculate_match(
            resume_skills,
            jd_skills
        )

        result["jd_skills"] = jd_skills

        result["ai_suggestions"] = (
            self.generate_ai_suggestions(
                result["missing_skills"]
            )
        )

        return result


jd_matching_service = JDMatchingService()