"""Pydantic models defining the shape of every file in conf/.

Each model maps to one YAML file, named after it. Validating them at
startup catches a wrong type or missing field in the config immediately,
instead of a bad value silently reaching business logic later.
"""

from pydantic import BaseModel


class ClaudeConfig(BaseModel):
    """Model and call defaults for every Claude API call."""

    tag_model: str
    chat_model: str
    prose_temperature: float
    max_tokens: int


class EscalationConfig(BaseModel):
    """Thresholds for backend.escalation's rules."""

    missed_medication_pattern_threshold: int
    repeated_question_weekly_threshold: int
    low_mood_streak_days: int


class MedicationConfig(BaseModel):
    """Dose-status timing for backend.medications."""

    grace_minutes: int


class ChatConfig(BaseModel):
    """Chat history and bounded Check-In limits for backend.chat."""

    recent_messages_limit: int
    bounded_checkin_max_replies: int


class PointAndAskConfig(BaseModel):
    """Image handling and risk-scoring for backend.point_and_ask."""

    max_image_dimension: int
    core_signal_weight: int
    high_risk_cutoff: int
    medium_risk_cutoff: int


class MemoryConfig(BaseModel):
    """Memory bank context limits for backend.memory_bank."""

    context_facts_limit: int
    reminiscence_nudge_probability: float


class CompanionLineConfig(BaseModel):
    """Daily-opener timing for backend.companion_line."""

    family_nudge_silence_days: int
    family_nudge_cooldown_days: int
    reminiscence_cooldown_days: int


class ApiConfig(BaseModel):
    """FastAPI layer settings."""

    cors_origin: str


class LoggingConfig(BaseModel):
    """Logging destination and verbosity."""

    level: str
    log_file: str


class PromptsConfig(BaseModel):
    """AI system prompts, static text or templates with {placeholder} clauses
    filled in by the assembling function."""

    tag_system: str
    classify_system: str
    companion_persona: str
    explain_image_base: str
    reminiscence_base: str
    weekly_summary_base: str


class Settings(BaseModel):
    """Top-level config, aggregating one section per conf/*.yaml file."""

    claude: ClaudeConfig
    escalation: EscalationConfig
    medications: MedicationConfig
    chat: ChatConfig
    point_and_ask: PointAndAskConfig
    memory: MemoryConfig
    companion_line: CompanionLineConfig
    api: ApiConfig
    logging: LoggingConfig
    prompts: PromptsConfig
