from dataclasses import dataclass, field


@dataclass #python class; main job is to hold data
class Document:
    """A standardized document produced by any parser."""

    text: str
    source: str  # path relative to the documents root, e.g. "hr/policy.txt"
    metadata: dict = field(default_factory=dict) #gives each new doc its own empty metadata dictionary

    
