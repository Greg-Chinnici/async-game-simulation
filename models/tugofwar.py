from pydantic import BaseModel
from registry import register_command

@register_command("pull")
class PullParams(BaseModel):
    type: str
    count: int
