"""
Gemini AI Service - Core AI Integration
Handles all interactions with Google Gemini API
"""

import google.generativeai as genai
import json
import re
import logging
from typing import Optional
from models.schemas import GeminiAnalysisResult, ProgrammingLanguage
from utils.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


# ─── Prompt Templates ─────────────────────────────────────────────────────────

SYSTEM_CONTEXT = """You are an expert Senior Software Engineer and Code Security Analyst with 15+ years of experience. 
You specialize in code review, security auditing, performance optimization, and software architecture.
You must always respond with valid JSON only — no markdown, no explanation outside JSON."""


def build_review_prompt(code: str, language: str) -> str:
    """
    Advanced prompt engineering template for code analysis.
    Instructs Gemini to return structured JSON with all required fields.
    """
    language_guidelines = {
        "python": "PEP 8 style guide, type hints, proper exception handling, virtual environments",
        "java": "Java naming conventions, SOLID principles, proper null handling, exception hierarchy",
        "javascript": "ESLint standards, async/await patterns, prototype chain, XSS prevention",
        "cpp": "Memory management, RAII, smart pointers, undefined behavior, buffer overflows",
        "c": "Memory leaks, buffer overflows, pointer arithmetic, null pointer dereferences, integer overflow"
    }

    lang_lower = language.lower()
    guidelines = language_guidelines.get(lang_lower, "general best practices")

    prompt = f"""
You are an expert code reviewer. Analyze the following {language.upper()} code comprehensively.

## CODE TO REVIEW:
```{lang_lower}
{code}
```

## YOUR ANALYSIS TASK:
Perform a thorough code review covering ALL of the following dimensions:

1. **BUGS** - Logic errors, off-by-one errors, null pointer issues, incorrect algorithms
2. **SECURITY VULNERABILITIES** - SQL injection, XSS, buffer overflows, hardcoded credentials, insecure dependencies, input validation issues
3. **PERFORMANCE ISSUES** - Inefficient algorithms, unnecessary loops, memory leaks, blocking operations, time complexity
4. **CODE SMELLS** - Dead code, duplicate logic, long methods, magic numbers, poor naming
5. **CODING STANDARDS** - {guidelines}
6. **MAINTAINABILITY** - Documentation, coupling, cohesion, testability, modularity

## SCORING RUBRIC (0-100):
- **Overall Score**: Weighted average of all dimensions
- **Security Score**: Based on vulnerabilities found (critical bugs reduce this heavily)
- **Performance Score**: Based on algorithmic efficiency and resource usage
- **Maintainability Score**: Based on readability, documentation, structure

## SEVERITY LEVELS:
- **High**: Must fix immediately - security risks, crashes, data corruption
- **Medium**: Should fix soon - performance degradation, potential bugs
- **Low**: Nice to fix - style issues, minor improvements

## RESPONSE FORMAT:
You MUST respond with ONLY a valid JSON object. No text before or after. Use this exact structure:

{{
  "overall_score": <integer 0-100>,
  "security_score": <integer 0-100>,
  "performance_score": <integer 0-100>,
  "maintainability_score": <integer 0-100>,
  "summary": "<2-3 sentence overall assessment>",
  "issues": [
    {{
      "severity": "<High|Medium|Low>",
      "category": "<Security|Performance|Bug|Code Smell|Maintainability|Coding Standards>",
      "description": "<clear description of the specific problem found in this code>",
      "fix": "<specific actionable fix with corrected code snippet if applicable>",
      "line_number": <line number or null>
    }}
  ],
  "improved_code": "<complete rewritten version of the code with ALL issues fixed, well-commented>"
}}

IMPORTANT RULES:
- If code is excellent, give high scores but still find improvements
- Be SPECIFIC to this exact code — no generic advice
- The improved_code MUST be a complete, working version
- Include at least 3 issues even for good code (there's always room to improve)
- Escape all special characters in JSON strings properly
- Do NOT wrap response in markdown code blocks
"""
    return prompt


# ─── Gemini Service Class ─────────────────────────────────────────────────────

class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config={
                "temperature": 0.3,        # Lower = more consistent/deterministic
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 8192,
            },
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
        )

    def _clean_json_response(self, text: str) -> str:
        """Extract clean JSON from Gemini response"""
        # Remove markdown code blocks if present
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()

        # Find JSON object boundaries
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end + 1]

        return text

    def _parse_response(self, raw_text: str) -> dict:
        """Parse and validate Gemini JSON response"""
        cleaned = self._clean_json_response(raw_text)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}\nRaw: {cleaned[:500]}")
            # Return fallback structure
            data = self._fallback_response()

        # Validate and clamp scores
        for score_key in ["overall_score", "security_score", "performance_score", "maintainability_score"]:
            if score_key not in data:
                data[score_key] = 50
            data[score_key] = max(0, min(100, int(data.get(score_key, 50))))

        # Ensure issues list exists
        if "issues" not in data or not isinstance(data["issues"], list):
            data["issues"] = []

        # Validate each issue
        valid_severities = {"High", "Medium", "Low"}
        valid_categories = {"Security", "Performance", "Bug", "Code Smell", "Maintainability", "Coding Standards"}

        cleaned_issues = []
        for issue in data["issues"]:
            if not isinstance(issue, dict):
                continue
            cleaned_issue = {
                "severity": issue.get("severity", "Medium") if issue.get("severity") in valid_severities else "Medium",
                "category": issue.get("category", "Code Smell") if issue.get("category") in valid_categories else "Code Smell",
                "description": str(issue.get("description", "Issue detected")),
                "fix": str(issue.get("fix", "Review and refactor this section")),
                "line_number": issue.get("line_number")
            }
            cleaned_issues.append(cleaned_issue)

        data["issues"] = cleaned_issues

        if "improved_code" not in data or not data["improved_code"]:
            data["improved_code"] = "# Improved code could not be generated. Please review the issues above."

        if "summary" not in data:
            data["summary"] = "Code review completed. See issues below for details."

        return data

    def _fallback_response(self) -> dict:
        """Fallback when Gemini fails to return valid JSON"""
        return {
            "overall_score": 50,
            "security_score": 50,
            "performance_score": 50,
            "maintainability_score": 50,
            "summary": "Analysis completed with limited results due to parsing error.",
            "issues": [
                {
                    "severity": "Medium",
                    "category": "Maintainability",
                    "description": "Code review was performed but detailed parsing failed. Please try again.",
                    "fix": "Resubmit the code for a fresh analysis.",
                    "line_number": None
                }
            ],
            "improved_code": "# Please resubmit for improved code generation."
        }

    async def analyze_code(self, code: str, language: str) -> dict:
        """
        Main method: Send code to Gemini and return structured analysis
        """
        logger.info(f"Analyzing {language} code ({len(code)} chars)")

        prompt = build_review_prompt(code, language)

        try:
            # Add system context as part of the prompt
            full_prompt = f"{SYSTEM_CONTEXT}\n\n{prompt}"

            response = self.model.generate_content(full_prompt)
            raw_text = response.text

            logger.info(f"Received Gemini response ({len(raw_text)} chars)")

            parsed = self._parse_response(raw_text)
            parsed["raw_response"] = raw_text

            return parsed

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise ValueError(f"AI analysis failed: {str(e)}")


# Singleton instance
gemini_service = GeminiService()
