import json
from typing import Any, Type
from pydantic import BaseModel
from .base import BaseAIProvider

class DemoProvider(BaseAIProvider):
    def __init__(self):
        pass


    async def generate_structured(self, prompt: str, schema: Type[BaseModel]) -> Any:
        import re
        topic = "AI-Assisted Workflow"
        source_match = re.search(r'Source Material:\s*([^\n]+)', prompt)
        if source_match and source_match.group(1).strip():
            extracted = source_match.group(1).strip()
            if len(extracted) > 50:
                if "Antigravity" in extracted:
                    topic = "Antigravity Code Editor"
                elif "JavaScript" in extracted:
                    topic = "JavaScript Fundamentals"
                else:
                    topic = extracted[:30] + "..."
            else:
                topic = extracted
        else:
            title_match = re.search(r'Title:\s*([^\n]+)', prompt)
            if title_match and title_match.group(1).strip():
                topic = title_match.group(1).strip()[:100]
            else:
                obj_match = re.search(r'Objective:\s*([^\n]+)', prompt)
                if obj_match and obj_match.group(1).strip():
                    topic = obj_match.group(1).strip()[:100]

        def recursively_replace_topic(obj, topic_str):
            if isinstance(obj, dict):
                return {k: recursively_replace_topic(v, topic_str) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [recursively_replace_topic(x, topic_str) for x in obj]
            elif isinstance(obj, str):
                s = obj
                s = s.replace("The Developer's New Workflow", topic_str)
                s = s.replace("AI coding assistants", topic_str)
                s = s.replace("AI coding tools", topic_str)
                s = s.replace("JavaScript Fundamentals", topic_str)
                s = s.replace("From Typist to Architect", topic_str)
                s = s.replace("JS Basics", topic_str)
                s = s.replace("AI Developer Workflow", topic_str)
                return s
            return obj

        result = await self._generate_structured_internal(prompt, schema)
        if result:
            dump = result.model_dump()
            modified = recursively_replace_topic(dump, topic)
            return schema(**modified)
        return result

    async def _generate_structured_internal(self, prompt: str, schema: Type[BaseModel]) -> Any:
        is_js = "javascript" in prompt.lower() or "mozilla" in prompt.lower()
        is_youtube = "youtube" in prompt.lower()
        is_twitter = "twitter" in prompt.lower()
        is_twitter = "twitter" in prompt.lower()
        
        # Check if an approved type was injected into the prompt
        approved_type = "Carousel" # default
        if "approved the Content Type: \"Video\"" in prompt or "Target Content Type: Video" in prompt:
            approved_type = "Video"
        elif "approved the Content Type: \"Article\"" in prompt or "Target Content Type: Article" in prompt:
            approved_type = "Article"
        elif "approved the Content Type: \"Carousel\"" in prompt or "Target Content Type: Carousel" in prompt:
            approved_type = "Carousel"
        elif "approved the Content Type: \"Social Post\"" in prompt or "Target Content Type: Social Post" in prompt:
            approved_type = "Social Post"
        elif "approved the Content Type: \"Image\"" in prompt or "Target Content Type: Image" in prompt:
            approved_type = "Image"
        elif "approved the Content Type: \"Newsletter\"" in prompt or "Target Content Type: Newsletter" in prompt:
            approved_type = "Newsletter"
            
        platform_name = "YouTube" if is_youtube else ("Twitter" if is_twitter else "LinkedIn")
        platform_format = "Video" if is_youtube else ("Thread" if is_twitter else "Carousel")
        
        # Override format if specifically requested
        if approved_type == "Carousel":
            platform_format = "Carousel"
        elif approved_type == "Video":
            platform_format = "Video"
        elif approved_type == "Article":
            platform_format = "Article"

        if is_js:
            if schema.__name__ == "ContentPlanOutput":
                return schema(**{
                    "summary": "Educational content plan for JS",
                    "audience": "Developers",
                    "key_points": ["JS is cool", "JS is fast"],
                    "suggested_angles": ["JS Basics"]
                })
            elif schema.__name__ == "ContentTypeOutput":
                return schema(**{
                    "recommendation": {
                        "recommendedType": approved_type if approved_type else "Carousel",
                        "alternatives": ["Article", "Social Post"],
                        "reasoning": "JS concepts are easily explained with visuals.",
                        "sourceSignals": ["technical", "educational"]
                    }
                })
            elif schema.__name__ == "ContentSelectionOutput":
                gen_type = approved_type if approved_type else "Carousel"
                return schema(**{
                    "opportunities": [{
                        "id": "opt-js-1",
                        "content_type": gen_type,
                        "platform": "LinkedIn",
                        "title": f"JavaScript Fundamentals ({gen_type})",
                        "summary": "Overview of JS concepts",
                        "whyInteresting": "JS is popular.",
                        "keyPoints": ["JS is single threaded", "Event loop"],
                        "potentialAudience": "Developers",
                        "estimatedValue": "High"
                    }, {
                        "id": "opt-js-2",
                        "content_type": gen_type,
                        "platform": "YouTube",
                        "title": f"JS Basics - Visual Guide ({gen_type})",
                        "summary": "Quick visual overview of JS concepts",
                        "whyInteresting": "Visual learners engage well.",
                        "keyPoints": ["Event loop animation"],
                        "potentialAudience": "Beginner Developers",
                        "estimatedValue": "High reach"
                    }]
                })
            elif schema.__name__ == "PlatformStrategyOutput":
                return schema(**{
                    "recommendations": [{
                        "id": "plat-js", "projectId": "demo", "platform": "LinkedIn",
                        "suitability": 90, "reasoning": "Good reach",
                        "recommendedFormat": "Post", "recommendedLength": "Short",
                        "audience": "Devs", "tone": "Educational", "priority": "High"
                    }, {
                        "id": "plat-js-yt", "projectId": "demo", "platform": "YouTube",
                        "suitability": 85, "reasoning": "Great for visual tutorials",
                        "recommendedFormat": "Shorts", "recommendedLength": "60 seconds",
                        "audience": "Beginners", "tone": "Engaging", "priority": "Medium"
                    }, {
                        "id": "plat-js-tw", "projectId": "demo", "platform": "Twitter",
                        "suitability": 80, "reasoning": "Good for quick tips",
                        "recommendedFormat": "Thread", "recommendedLength": "5 tweets",
                        "audience": "Tech Community", "tone": "Informative", "priority": "Medium"
                    }]
                })
            elif schema.__name__ == "TopicAngleOutput":
                return schema(**{
                    "angles": [{
                        "id": "ang-js", "projectId": "demo", "title": f"JS Basics ({platform_name})",
                        "angle": "Educational", "hook": "Learn JS", "description": "JS is cool",
                        "targetAudience": "Devs", "corePromise": "Master JS", "differentiation": "Simple",
                        "supportingPoints": ["Event Loop"], "recommendedPlatforms": [platform_name]
                    }]
                })
            elif schema.__name__ == "ContentStrategyOutput":
                return schema(**{
                    "strategy": {
                        "id": "strat-js", "projectId": "demo", "objective": "Teach JS",
                        "targetAudience": "Devs", "coreMessage": "JS is essential",
                        "valueProposition": "Clear concepts", "tone": "Educational",
                        "format": platform_format, "hookStrategy": "Question",
                        "keyTalkingPoints": ["Event loop"], "callToAction": "Follow",
                        "contentStructure": "Intro, Body, Outro", "platformAdaptations": [{
                            "platform": platform_name,
                            "format": platform_format,
                            "notes": "Ensure high visual contrast."
                        }]
                    }
                })
            elif schema.__name__ == "StoryboardOutput":
                return schema(**{
                    "storyboard": {
                        "id": "sb-js", "projectId": "demo", "title": f"JS Basics ({platform_name} {platform_format})",
                        "objective": "Teach JS", "status": "Draft",
                        "scenes": [{
                            "id": "scene-1", "order": 1, "title": "Intro", "purpose": "Hook",
                            "narration": "JS is awesome", "visualDirection": "Code snippet",
                            "onScreenText": "JS", "transition": "Fade", "estimatedDuration": "N/A"
                        }]
                    }
                })
            elif schema.__name__ == "ScriptOutput":
                return schema(**{
                    "script": {
                        "id": "script-js", "projectId": "demo", "title": f"JS Post ({platform_name})",
                        "platform": platform_name, "format": platform_format, "hook": "Learn JS",
                        "conclusion": "Master JS", "callToAction": "Follow",
                        "estimatedDuration": "N/A", "status": "Draft",
                        "sections": [{
                            "id": "sec-1", "order": 1, "title": "Intro", "narration": "JS is awesome",
                            "visualNotes": "Code", "onScreenText": "JS", "estimatedDuration": "N/A"
                        }]
                    }
                })
            return schema()

        # Mock logic based on schema
        if schema.__name__ == "ContentPlanOutput":
            mock_data = {
                "summary": "Educational content plan focused on the workflow shift introduced by AI coding assistants.",
                "audience": "Software Engineers and Technical Leads",
                "key_points": ["The workflow shift", "Prompting as a skill", "Practical use cases"],
                "suggested_angles": ["The Workflow Shift", "From Typist to Architect"]
            }
            return schema(**mock_data)

        if schema.__name__ == "ContentTypeOutput":
            return schema(**{
                "recommendation": {
                    "recommendedType": "Carousel",
                    "alternatives": ["Article", "Social Post"],
                    "reasoning": "The source material contains several educational concepts that can be broken into concise visual sections.",
                    "sourceSignals": ["multiple distinct concepts", "educational structure", "step-by-step workflow"]
                }
            })
            
        if schema.__name__ == "ContentSelectionOutput":
            gen_type = approved_type if approved_type else "Carousel"
            platform_1 = "LinkedIn" if gen_type in ["Carousel", "Article", "Social Post", "Image"] else "YouTube"
            platform_2 = "Twitter" if gen_type in ["Social Post", "Image"] else "Instagram"
            platform_3 = "Substack" if gen_type == "Newsletter" else "TikTok"
            
            mock_data = {
                "opportunities": [
                    {
                        "id": f"opt-{gen_type.lower()}-1",
                        "content_type": gen_type,
                        "platform": platform_1,
                        "title": f"{platform_1} {gen_type}: The Developer's New Workflow",
                        "summary": f"A comprehensive {gen_type.lower()} detailing how AI coding assistants are changing the daily workflow of software engineers.",
                        "whyInteresting": f"{gen_type}s perform exceptionally well for educational content.",
                        "keyPoints": [
                            "AI coding tools help reduce repetitive boilerplate tasks",
                            "The shift from 'writing code' to 'reviewing AI-generated code'"
                        ],
                        "potentialAudience": "Software engineers, tech leads",
                        "estimatedValue": "High reach and educational value"
                    },
                    {
                        "id": f"opt-{gen_type.lower()}-2",
                        "content_type": gen_type,
                        "platform": platform_2,
                        "title": f"{platform_2} {gen_type}: From Typist to Architect",
                        "summary": f"A thought leadership {gen_type.lower()} exploring the evolution of software engineering in the age of AI.",
                        "whyInteresting": "Opinion pieces spark discussion and position the author as an industry leader.",
                        "keyPoints": ["The changing role of the developer", "Why prompt engineering is crucial"],
                        "potentialAudience": "Tech community and engineering managers",
                        "estimatedValue": "High engagement and shares"
                    },
                    {
                        "id": f"opt-{gen_type.lower()}-3",
                        "content_type": gen_type,
                        "platform": platform_3,
                        "title": f"{platform_3} {gen_type}: Top 3 AI Coding Tips",
                        "summary": f"A quick, punchy {gen_type.lower()} sharing immediate actionable advice for developers using AI tools.",
                        "whyInteresting": "Bite-sized content drives immediate engagement and is highly shareable.",
                        "keyPoints": ["Be specific", "Provide context", "Iterate quickly"],
                        "potentialAudience": "Developers scrolling on social media",
                        "estimatedValue": "High virality potential"
                    }
                ]
            }
            return schema(**mock_data)
            
        if schema.__name__ == "PlatformStrategyOutput":
            mock_data = {
                "recommendations": [
                    {
                        "id": "plat-linkedin-1",
                        "projectId": "demo-project",
                        "platform": "LinkedIn",
                        "suitability": 95,
                        "reasoning": "The professional networking context is ideal for career-focused discussions on how AI is changing development workflows.",
                        "recommendedFormat": "Carousel",
                        "recommendedLength": "7 slides",
                        "audience": "Software Engineers and Tech Leads",
                        "tone": "Professional, Educational, and Pragmatic",
                        "priority": "Recommended"
                    },
                    {
                        "id": "plat-youtube-1",
                        "projectId": "demo-project",
                        "platform": "YouTube",
                        "suitability": 90,
                        "reasoning": "Allows for long-form video tutorials which are highly requested by developers.",
                        "recommendedFormat": "Video",
                        "recommendedLength": "10 minutes",
                        "audience": "Developers of all levels",
                        "tone": "Informative and engaging",
                        "priority": "Recommended"
                    },
                    {
                        "id": "plat-twitter-1",
                        "projectId": "demo-project",
                        "platform": "Twitter",
                        "suitability": 85,
                        "reasoning": "Excellent for quick thought leadership and engaging the tech community.",
                        "recommendedFormat": "Thread",
                        "recommendedLength": "5-7 tweets",
                        "audience": "Tech Community",
                        "tone": "Conversational and punchy",
                        "priority": "Medium"
                    }
                ]
            }
            return schema(**mock_data)
            
        if schema.__name__ == "TopicAngleOutput":
            mock_data = {
                "angles": [
                    {
                        "id": "ang-workflow-shift",
                        "projectId": "demo-project",
                        "title": f"From Typist to Architect ({platform_name})",
                        "angle": "The Workflow Shift",
                        "hook": "AI isn't replacing developers; it's promoting them to architects.",
                        "description": "An educational breakdown of how daily development tasks change when using AI assistants.",
                        "targetAudience": "Developers adapting to AI tools",
                        "corePromise": "Understand exactly which skills matter most in an AI-assisted workflow.",
                        "differentiation": "Focuses on practical skill evolution rather than hype or doom-saying.",
                        "supportingPoints": [
                            "Less time on boilerplate, more time on system design.",
                            "Reviewing code is becoming more critical than writing it.",
                            "Prompt engineering is the new syntax."
                        ],
                        "recommendedPlatforms": [platform_name]
                    }
                ]
            }
            return schema(**mock_data)
            
        if schema.__name__ == "ContentStrategyOutput":
            mock_data = {
                "strategy": {
                    "id": "strat-carousel-1",
                    "projectId": "demo-project",
                    "objective": "Educate software engineers on the practical workflow shift caused by AI coding assistants.",
                    "targetAudience": "Software Engineers and Technical Leads",
                    "coreMessage": "AI coding assistants elevate developers from typists to systems architects by reducing repetitive tasks.",
                    "valueProposition": "Clear, pragmatic insight into the evolving skillset required for modern development.",
                    "tone": "Professional, pragmatic, and educational",
                    "format": platform_format,
                    "hookStrategy": "Start with a relatable observation about time spent on boilerplate versus system design.",
                    "keyTalkingPoints": [
                        "Reduction of boilerplate coding",
                        "The rise of code review as a primary skill",
                        "Architectural thinking over syntax memorization"
                    ],
                    "callToAction": "Follow for more insights on AI engineering and developer productivity.",
                    "contentStructure": "Slide 1: Hook, Slide 2: The Old Way, Slide 3: The New Way, Slide 4: Key Skill 1, Slide 5: Key Skill 2, Slide 6: The Takeaway, Slide 7: CTA",
                    "platformAdaptations": [
                        {
                            "platform": platform_name,
                            "format": platform_format,
                            "notes": "Ensure high visual contrast and brief, impactful text on each slide."
                        }
                    ]
                }
            }
            return schema(**mock_data)

        if schema.__name__ == "StoryboardOutput":
            mock_data = {
                "storyboard": {
                    "id": "sb-carousel-1",
                    "projectId": "demo-project",
                    "title": f"The AI Developer Workflow ({platform_name} {platform_format})",
                    "objective": "Guide developers through the mindset shift required to effectively leverage AI coding tools.",
                    "status": "Draft",
                    "scenes": [
                        {
                            "id": "slide-1",
                            "order": 1,
                            "title": "Scene 1: Hook",
                            "purpose": "Grab attention with a bold statement about the changing role of developers.",
                            "narration": "AI isn't replacing software engineers. It's promoting them to architects.",
                            "visualDirection": "Bold title text centered on a dark background with a subtle gradient.",
                            "onScreenText": "AI isn't replacing developers. It's promoting them to architects.",
                            "transition": "Swipe",
                            "estimatedDuration": "N/A"
                        },
                        {
                            "id": "slide-2",
                            "order": 2,
                            "title": "Scene 2: The Problem",
                            "purpose": "Highlight the inefficiency of the traditional workflow.",
                            "narration": "Traditionally, we spent hours writing boilerplate, fixing typos, and searching for syntax.",
                            "visualDirection": "Split layout: an hourglass icon on the left, bullet points on the right.",
                            "onScreenText": "The Old Way:\n- Writing boilerplate\n- Fixing syntax typos\n- Memorizing APIs",
                            "transition": "Swipe",
                            "estimatedDuration": "N/A"
                        },
                        {
                            "id": "slide-3",
                            "order": 3,
                            "title": "Scene 3: The Shift",
                            "purpose": "Introduce how AI changes the distribution of effort.",
                            "narration": "With AI assistants, the execution is automated. The value is now in the direction.",
                            "visualDirection": "A flowchart showing 'Idea -> AI Execution -> Developer Review'.",
                            "onScreenText": "The New Way:\nYour value is in the direction, not the typing.",
                            "transition": "Swipe",
                            "estimatedDuration": "N/A"
                        },
                        {
                            "id": "slide-4",
                            "order": 4,
                            "title": "Scene 4: Skill 1 - Prompting",
                            "purpose": "Define the first key skill in the new stack.",
                            "narration": "Skill 1: Contextual Prompting. You need to explain the 'why' and 'how' clearly to the AI.",
                            "visualDirection": "A graphic of a chat interface showing a well-structured prompt.",
                            "onScreenText": "Skill 1: Contextual Prompting\nClear instructions yield clean code.",
                            "transition": "Swipe",
                            "estimatedDuration": "N/A"
                        },
                        {
                            "id": "slide-5",
                            "order": 5,
                            "title": "Scene 5: Skill 2 - Code Review",
                            "purpose": "Define the second key skill in the new stack.",
                            "narration": "Skill 2: High-Speed Code Review. You must be able to spot edge cases and security flaws in AI-generated code.",
                            "visualDirection": "A magnifying glass over a block of code with highlighted syntax.",
                            "onScreenText": "Skill 2: Advanced Code Review\nTrust, but rigorously verify.",
                            "transition": "Swipe",
                            "estimatedDuration": "N/A"
                        },
                        {
                            "id": "slide-6",
                            "order": 6,
                            "title": "Scene 6: The Takeaway",
                            "purpose": "Summarize the core message.",
                            "narration": "The best developers of tomorrow will think in systems, not just lines of code.",
                            "visualDirection": "A structural blueprint graphic transitioning into a modern tech stack logo.",
                            "onScreenText": "Think in systems, not just syntax.",
                            "transition": "Swipe",
                            "estimatedDuration": "N/A"
                        },
                        {
                            "id": "slide-7",
                            "order": 7,
                            "title": "Scene 7: Call to Action",
                            "purpose": "Encourage engagement and follows.",
                            "narration": "How has AI changed your daily workflow? Let me know in the comments.",
                            "visualDirection": "Profile picture, name, and a prominent 'Follow' button.",
                            "onScreenText": "How has AI changed your workflow?\n\nFollow for more insights on modern software engineering.",
                            "transition": "Swipe",
                            "estimatedDuration": "N/A"
                        }
                    ]
                }
            }
            return schema(**mock_data)

        if schema.__name__ == "ScriptOutput":
            mock_data = {
                "script": {
                    "id": "script-carousel-1",
                    "projectId": "demo-project",
                    "title": f"{platform_name} {platform_format}: The AI Developer Workflow",
                    "platform": platform_name,
                    "format": platform_format,
                    "hook": "AI isn't replacing software engineers. It's promoting them to architects.",
                    "conclusion": "Think in systems, not just syntax.",
                    "callToAction": "Follow for more insights on modern software engineering.",
                    "estimatedDuration": "N/A",
                    "status": "Draft",
                    "sections": [
                        {
                            "id": "sec-slide-1",
                            "order": 1,
                            "title": "Section 1: Hook",
                            "narration": "AI isn't replacing developers. It's promoting them to architects.",
                            "visualNotes": "Bold title text centered on a dark background with a subtle gradient.",
                            "onScreenText": "AI isn't replacing developers. It's promoting them to architects.",
                            "estimatedDuration": "N/A"
                        },
                        {
                            "id": "sec-slide-2",
                            "order": 2,
                            "title": "Section 2: The Problem",
                            "narration": "The Old Way:\n- Writing boilerplate\n- Fixing syntax typos\n- Memorizing APIs",
                            "visualNotes": "Split layout: an hourglass icon on the left, bullet points on the right.",
                            "onScreenText": "The Old Way:\n- Writing boilerplate\n- Fixing syntax typos\n- Memorizing APIs",
                            "estimatedDuration": "N/A"
                        },
                        {
                            "id": "sec-slide-3",
                            "order": 3,
                            "title": "Section 3: The Shift",
                            "narration": "The New Way:\nYour value is in the direction, not the typing.",
                            "visualNotes": "A flowchart showing 'Idea -> AI Execution -> Developer Review'.",
                            "onScreenText": "The New Way:\nYour value is in the direction, not the typing.",
                            "estimatedDuration": "N/A"
                        },
                        {
                            "id": "sec-slide-4",
                            "order": 4,
                            "title": "Section 4: Skill 1 - Prompting",
                            "narration": "Skill 1: Contextual Prompting\nClear instructions yield clean code.",
                            "visualNotes": "A graphic of a chat interface showing a well-structured prompt.",
                            "onScreenText": "Skill 1: Contextual Prompting\nClear instructions yield clean code.",
                            "estimatedDuration": "N/A"
                        },
                        {
                            "id": "sec-slide-5",
                            "order": 5,
                            "title": "Section 5: Skill 2 - Code Review",
                            "narration": "Skill 2: Advanced Code Review\nTrust, but rigorously verify.",
                            "visualNotes": "A magnifying glass over a block of code with highlighted syntax.",
                            "onScreenText": "Skill 2: Advanced Code Review\nTrust, but rigorously verify.",
                            "estimatedDuration": "N/A"
                        },
                        {
                            "id": "sec-slide-6",
                            "order": 6,
                            "title": "Section 6: The Takeaway",
                            "narration": "Think in systems, not just syntax.",
                            "visualNotes": "A structural blueprint graphic transitioning into a modern tech stack logo.",
                            "onScreenText": "Think in systems, not just syntax.",
                            "estimatedDuration": "N/A"
                        },
                        {
                            "id": "sec-slide-7",
                            "order": 7,
                            "title": "Section 7: Call to Action",
                            "narration": "How has AI changed your workflow?\n\nFollow for more insights on modern software engineering.",
                            "visualNotes": "Profile picture, name, and a prominent 'Follow' button.",
                            "onScreenText": "How has AI changed your workflow?\n\nFollow for more insights on modern software engineering.",
                            "estimatedDuration": "N/A"
                        }
                    ]
                }
            }
            return schema(**mock_data)

        # Generic fallback mock
        return schema()

    async def generate_text(self, prompt: str) -> str:
        import re
        topic = "the provided subject"
        source_match = re.search(r'Source Material:\s*([^\n]+)', prompt)
        if source_match and source_match.group(1).strip():
            topic = source_match.group(1).strip()[:100]
        return f"Automatically completed. The AI extracted context based on the input: {topic}."
