import os
import requests
from flask import current_app

class AIService:
    @classmethod
    def enhance_content(cls, prompt_type, text_input, context=None):
        """Generates or improves career text content using AI or structured rule generators."""
        api_key = current_app.config.get('AI_API_KEY')
        provider = current_app.config.get('AI_PROVIDER')

        # If OpenAI key is provided, perform direct API completion
        if api_key and provider == 'openai':
            try:
                headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
                prompt = cls._build_prompt(prompt_type, text_input, context)
                payload = {
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "system", "content": "You are a professional executive resume writer and career expert."},
                                 {"role": "user", "content": prompt}],
                    "temperature": 0.7
                }
                res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=12)
                if res.status_code == 200:
                    return res.json()['choices'][0]['message']['content'].strip()
            except Exception as e:
                current_app.logger.warning(f"AI API request failed, falling back to smart rules engine: {e}")

        # Smart fallback generator engine
        return cls._smart_fallback(prompt_type, text_input, context)

    @staticmethod
    def _build_prompt(prompt_type, text_input, context):
        if prompt_type == 'summary':
            return f"Rewrite and polish this professional summary for a resume/CV to sound high-impact, articulate, and executive: '{text_input}'"
        elif prompt_type == 'cover_letter':
            return f"Generate a compelling, professional cover letter based on job title '{context.get('position')}' at '{context.get('company')}'. Experience details: '{text_input}'"
        elif prompt_type == 'linkedin':
            return f"Create a punchy, SEO-optimized LinkedIn Headline and About section for a '{context.get('position')}' with skills: '{text_input}'"
        return f"Improve this career content professionally: '{text_input}'"

    @staticmethod
    def _smart_fallback(prompt_type, text_input, context=None):
        context = context or {}
        text = text_input.strip() if text_input else ""

        if prompt_type == 'summary':
            return (
                f"Results-oriented {context.get('title', 'Professional')} with a proven track record of driving strategic operational growth "
                f"and delivering high-value project outcomes. Adept at leveraging core skills in {text if text else 'leadership and communication'} "
                f"to optimize workflows, foster cross-functional collaboration, and exceed organizational key performance metrics."
            )
        elif prompt_type == 'cover_letter':
            pos = context.get('position', 'the open role')
            comp = context.get('company', 'your esteemed organization')
            return (
                f"Dear Hiring Manager,\n\n"
                f"I am writing to express my enthusiastic interest in the {pos} position at {comp}. "
                f"With a solid background in delivering measurable operational performance and key business growth, "
                f"I am confident in my capability to make an immediate impact within your team.\n\n"
                f"Throughout my background, I have consistently demonstrated expertise in {text if text else 'strategic planning, problem-solving, and executing complex projects'}. "
                f"My approach combines analytical precision with proactive collaboration, ensuring projects succeed predictably and efficiently.\n\n"
                f"I look forward to discussing how my experience and skill set align with the vision at {comp}.\n\n"
                f"Sincerely,\n{context.get('name', 'Applicant')}"
            )
        elif prompt_type == 'application_letter':
            return (
                f"Dear Selection Committee,\n\n"
                f"Please accept this letter as my formal application for the {context.get('position', 'Position')} opening at {context.get('company', 'Organization')}. "
                f"Having developed robust expertise in {text if text else 'my domain'}, I possess the qualifications required to drive success in this role.\n\n"
                f"Key strengths I bring include strategic problem-solving, leadership, and a proven target-driven mindset. "
                f"I welcome the opportunity to interview and share more about my career journey.\n\n"
                f"Respectfully submitted,\n{context.get('name', 'Applicant')}"
            )
        elif prompt_type == 'linkedin':
            pos = context.get('position', 'Professional')
            return (
                f"=== OPTIMIZED HEADLINE ===\n"
                f"{pos} | Driving Strategic Results & Technical Innovation | Continuous Improvement Enthusiast\n\n"
                f"=== ABOUT SECTION ===\n"
                f"I am an accomplished {pos} passionate about transforming complex challenges into efficient, scalable solutions. "
                f"Over my career, I have cultivated deep expertise across {text if text else 'project execution, operational leadership, and team development'}.\n\n"
                f"CORE COMPETENCIES:\n"
                f"• Strategic Vision & Execution\n"
                f"• Cross-functional Collaboration\n"
                f"• Performance Optimization"
            )
        return text or "Enhanced professional content generated successfully."