import json

from app.services.nlp_service import resume_nlp_service
from app.services.ats_services import ATSService


class AnalysisService:

    @staticmethod
    def analyze_resume(resume):

        resume_text = resume.parsed_text

        extracted_data = resume_nlp_service.analyze_resume(
            resume_text
        )

        ats_result = ATSService.calculate(
            resume_text
        )

        resume.ats_score = ats_result["ats_score"]

        resume.ats_grade = ats_result["ats_grade"]

        resume.analysis_result = json.dumps(
            ats_result,
            ensure_ascii=False
        )

        return {
            "resume": resume,
            "analysis": extracted_data,
            "ats": ats_result
        }