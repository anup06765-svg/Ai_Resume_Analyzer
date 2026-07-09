"""
ATS Scoring Service
Production Level
"""

from typing import Dict, List


class ATSScorer:
    """
    Calculates ATS Score based on extracted resume data.
    """

    def __init__(self):

        self.weights = {

            "contact": 10,
            "skills": 25,
            "education": 15,
            "experience": 20,
            "projects": 10,
            "certificates": 10,
            "keywords": 10

        }

    # -----------------------------------------
    # Main Function
    # -----------------------------------------

    def calculate_score(self, data: Dict) -> Dict:

        scores = {}

        scores["contact"] = self.contact_score(data)

        scores["skills"] = self.skills_score(data)

        scores["education"] = self.education_score(data)

        scores["experience"] = self.experience_score(data)

        scores["projects"] = self.projects_score(data)

        scores["certificates"] = self.certificates_score(data)

        scores["keywords"] = self.keyword_score(data)

        total = sum(scores.values())

        if total > 100:
            total = 100

        return {

            "ats_score": total,

            "breakdown": scores,

            "grade": self.grade(total)

        }

    # -----------------------------------------
    # Contact
    # -----------------------------------------

    def contact_score(self, data):

        score = 0

        if data.get("name"):
            score += 2

        if data.get("email"):
            score += 4

        if data.get("phone"):
            score += 4

        return score

    # -----------------------------------------
    # Skills
    # -----------------------------------------

    def skills_score(self, data):

        skills = data.get("skills", [])

        count = len(skills)

        if count >= 15:
            return 25

        elif count >= 10:
            return 20

        elif count >= 5:
            return 15

        elif count >= 3:
            return 10

        return 5

    # -----------------------------------------
    # Education
    # -----------------------------------------

    def education_score(self, data):

        education = data.get("education", [])

        if len(education) >= 2:
            return 15

        elif len(education) == 1:
            return 10

        return 0

    # -----------------------------------------
    # Experience
    # -----------------------------------------

    def experience_score(self, data):

        experience = data.get("experience", [])

        if len(experience) >= 3:
            return 20

        elif len(experience) == 2:
            return 15

        elif len(experience) == 1:
            return 10

        return 0

    # -----------------------------------------
    # Projects
    # -----------------------------------------

    def projects_score(self, data):

        projects = data.get("projects", [])

        if len(projects) >= 4:
            return 10

        elif len(projects) >= 2:
            return 8

        elif len(projects) == 1:
            return 5

        return 0

    # -----------------------------------------
    # Certificates
    # -----------------------------------------

    def certificates_score(self, data):

        certificates = data.get("certificates", [])

        if len(certificates) >= 3:
            return 10

        elif len(certificates) >= 1:
            return 7

        return 0

    # -----------------------------------------
    # Keywords
    # -----------------------------------------

    def keyword_score(self, data):

        keywords = data.get("keywords", [])

        count = len(keywords)

        if count >= 20:
            return 10

        elif count >= 10:
            return 8

        elif count >= 5:
            return 5

        return 0

    # -----------------------------------------
    # Grade
    # -----------------------------------------

    def grade(self, score):

        if score >= 90:
            return "A+"

        elif score >= 80:
            return "A"

        elif score >= 70:
            return "B"

        elif score >= 60:
            return "C"

        return "Needs Improvement"