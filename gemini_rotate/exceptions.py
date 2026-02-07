class GeminiRotationError(Exception):
    """Base exception for Gemini Rotation Library"""
    pass

class AllClientsFailed(GeminiRotationError):
    """Raised when all available agents fail to generate content."""
    pass
