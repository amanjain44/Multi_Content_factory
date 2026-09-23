from typing import List, Optional, TypedDict, Literal
from pydantic import BaseModel, Field

ContentTypeEnum = Literal["Video", "Image", "Carousel", "Article", "Newsletter", "Social Post"]

class ContentTypeRecommendation(BaseModel):
    recommendedType: ContentTypeEnum = Field(description="The primary recommended content type")
    alternatives: List[ContentTypeEnum] = Field(description="Alternative content types")
    reasoning: str = Field(description="Why this format was recommended")
    sourceSignals: List[str] = Field(description="Signals from the source text")

class ContentTypeOutput(BaseModel):
    recommendation: ContentTypeRecommendation

class ContentPlanOutput(BaseModel):
    summary: str = Field(description="A brief summary of the content plan")
    audience: str = Field(description="The target audience for the content")
    key_points: List[str] = Field(description="List of key points to cover")
    suggested_angles: List[str] = Field(description="Suggested unique angles or perspectives")

class ContentOpportunity(BaseModel):
    id: str = Field(description="A unique identifier for this opportunity, e.g., an alphanumeric string")
    title: str = Field(description="The title of the content format")
    summary: str = Field(description="A short description of the content")
    whyInteresting: str = Field(description="Why this content is valuable or interesting to the audience")
    keyPoints: List[str] = Field(description="Key points this content will cover")
    potentialAudience: str = Field(description="The specific target audience for this format")
    estimatedValue: Optional[str] = Field(default=None, description="The estimated value or impact of this content")

class ContentSelectionOutput(BaseModel):
    opportunities: List[ContentOpportunity] = Field(description="A list of generated content opportunities based on the source")

class PlatformRecommendation(BaseModel):
    id: str = Field(description="A unique identifier for this recommendation")
    projectId: str = Field(description="The project ID this belongs to")
    platform: str = Field(description="The platform name (e.g., LinkedIn, YouTube, Twitter)")
    suitability: int = Field(description="A score from 0 to 100 indicating how suitable the platform is")
    reasoning: str = Field(description="Why this platform is a good fit")
    recommendedFormat: str = Field(description="The recommended format for the platform")
    recommendedLength: str = Field(description="The recommended length or duration")
    audience: str = Field(description="The target audience on this platform")
    tone: str = Field(description="The recommended tone of voice")
    priority: str = Field(description="Priority label (e.g., 'Recommended' or 'Optional')")

class PlatformStrategyOutput(BaseModel):
    recommendations: List[PlatformRecommendation] = Field(description="A list of platform recommendations")

class TopicAngle(BaseModel):
    id: str = Field(description="A unique identifier for this angle")
    projectId: str = Field(description="The project ID this belongs to")
    title: str = Field(description="The working title for this content")
    angle: str = Field(description="The specific angle or perspective (e.g., 'Contrarian', 'Educational')")
    hook: str = Field(description="The opening hook to grab attention")
    description: str = Field(description="A brief description of the content")
    targetAudience: str = Field(description="The specific target audience for this angle")
    corePromise: str = Field(description="The core value or takeaway for the audience")
    differentiation: str = Field(description="Why this angle is unique or stands out")
    supportingPoints: List[str] = Field(description="List of supporting points to cover")
    recommendedPlatforms: List[str] = Field(description="List of platform names this angle is suited for")

class TopicAngleOutput(BaseModel):
    angles: List[TopicAngle] = Field(description="A list of generated topic angles")

class PlatformAdaptation(BaseModel):
    platform: str = Field(description="The name of the platform")
    format: str = Field(description="The specific format for this platform (e.g. 'Thread', 'Long-form post')")
    notes: str = Field(description="Specific notes on how to adapt the content for this platform")

class ContentStrategy(BaseModel):
    id: str = Field(description="A unique identifier for this strategy")
    projectId: str = Field(description="The project ID this belongs to")
    objective: str = Field(description="The primary objective of the content")
    targetAudience: str = Field(description="The target audience")
    coreMessage: str = Field(description="The single core message to convey")
    valueProposition: str = Field(description="The value the audience gets from this content")
    tone: str = Field(description="The tone of voice (e.g. 'Authoritative, accessible')")
    format: str = Field(description="The overarching format (e.g. 'Multi-platform campaign')")
    hookStrategy: str = Field(description="How to hook the reader/viewer")
    keyTalkingPoints: List[str] = Field(description="List of key talking points")
    callToAction: str = Field(description="The call to action (CTA)")
    contentStructure: str = Field(description="The structure/outline of the content")
    platformAdaptations: List[PlatformAdaptation] = Field(description="How to adapt for specific platforms")

class ContentStrategyOutput(BaseModel):
    strategy: ContentStrategy = Field(description="The generated content strategy")

class StoryboardScene(BaseModel):
    id: str = Field(description="A unique identifier for this scene")
    order: int = Field(description="The sequential order of the scene")
    title: str = Field(description="The title of the scene")
    purpose: str = Field(description="The purpose or goal of the scene")
    narration: str = Field(description="The spoken narration or dialogue")
    visualDirection: str = Field(description="The visual description or action")
    onScreenText: str = Field(description="Any text that appears on screen")
    transition: str = Field(description="How to transition to the next scene")
    estimatedDuration: str = Field(description="The estimated duration (e.g. '5 seconds')")

class StoryboardModel(BaseModel):
    id: str = Field(description="A unique identifier for this storyboard")
    projectId: str = Field(description="The project ID this belongs to")
    title: str = Field(description="The overall title of the storyboard")
    objective: str = Field(description="The overarching objective")
    status: str = Field(description="The current status (should be 'Draft')")
    scenes: List[StoryboardScene] = Field(description="The list of scenes in order")

class StoryboardOutput(BaseModel):
    storyboard: StoryboardModel = Field(description="The generated storyboard")


class ScriptSection(BaseModel):
    id: str = Field(description="A unique identifier for this section")
    order: int = Field(description="The sequential order of the section")
    title: str = Field(description="The title of the script section (maps to storyboard scene title)")
    narration: str = Field(description="The full spoken narration or written copy for this section")
    visualNotes: str = Field(description="Visual direction, B-roll notes, or production guidance")
    onScreenText: str = Field(description="Any text overlays or captions that appear on screen")
    estimatedDuration: str = Field(description="The estimated duration of this section (e.g. '8 seconds')")


class ScriptModel(BaseModel):
    id: str = Field(description="A unique identifier for this script")
    projectId: str = Field(description="The project ID this script belongs to")
    title: str = Field(description="The full title of the script")
    platform: str = Field(description="The target platform (e.g. 'LinkedIn', 'YouTube')")
    format: str = Field(description="The content format (e.g. 'Short-form video', 'Long-form post')")
    hook: str = Field(description="The opening hook — the very first words/sentences to grab attention")
    conclusion: str = Field(description="The closing statement that wraps the content")
    callToAction: str = Field(description="The final call to action (e.g. 'Follow for more', 'Comment below')")
    estimatedDuration: str = Field(description="Total estimated duration or read time (e.g. '68 seconds')")
    status: str = Field(description="The current status — always 'Draft' on generation")
    sections: List[ScriptSection] = Field(description="The ordered list of body sections, one per storyboard scene")


class ScriptOutput(BaseModel):
    script: ScriptModel = Field(description="The generated final script")

class AIState(TypedDict):
    input_text: str
    approved_content_type: Optional[str]
    selected_opportunity: Optional[dict]
    selected_platforms: Optional[List[dict]]
    selected_angle: Optional[dict]
    approved_strategy: Optional[dict]
    approved_storyboard: Optional[dict]
    grounding_context: Optional[dict]
    intent: Optional[str]
    keywords: Optional[List[str]]
    structured_output: Optional[dict]
    error: Optional[str]
    retries: int
