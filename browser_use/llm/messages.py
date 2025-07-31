from abc import ABCMeta
from typing import List, Literal, Optional, Union

from pydantic import BaseModel


# Type alias for supported image media types
SupportedImageMediaType = Literal["image/jpeg", "image/png", "image/gif", "image/webp"]


class ContentPartTextParam(BaseModel):
    type: Literal["text"] = "text"
    text: str


class ImageURL(BaseModel):
    url: str
    detail: Optional[Literal["auto", "low", "high"]] = "auto"


class ContentPartImageParam(BaseModel):
    type: Literal["image_url"] = "image_url"
    image_url: ImageURL


class ContentPartRefusalParam(BaseModel):
    type: Literal["refusal"] = "refusal"
    refusal: str


class Function(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    id: str
    type: Literal["function"] = "function"
    function: Function


ContentPart = Union[ContentPartTextParam, ContentPartImageParam, ContentPartRefusalParam]


class BaseMessage(BaseModel, metaclass=ABCMeta):
    role: str
    content: Union[str, List[ContentPart]]
    name: Optional[str] = None
    cache: bool = False  # For caching support (e.g., Anthropic)


class SystemMessage(BaseMessage):
    role: Literal["system"] = "system"
    content: Union[str, List[ContentPartTextParam]]  # System messages only support text


class UserMessage(BaseMessage):
    role: Literal["user"] = "user"
    content: Union[str, List[Union[ContentPartTextParam, ContentPartImageParam]]]  # User messages support text and images


class AssistantMessage(BaseMessage):
    role: Literal["assistant"] = "assistant"
    content: Optional[Union[str, List[Union[ContentPartTextParam, ContentPartRefusalParam]]]] = None  # Assistant content can be None
    tool_calls: Optional[List[ToolCall]] = None
    refusal: Optional[str] = None  # For OpenAI refusal support
