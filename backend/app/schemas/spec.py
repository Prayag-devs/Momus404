"""
momus404 — app.schemas.spec
Test case and test specification models.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import Priority


class TestCase(BaseModel):
    id: str
    title: str
    preconditions: str = ""
    steps: str = ""
    expected_result: str = ""
    priority: str = Priority.MEDIUM.value
    tags: List[str] = Field(default_factory=list)


class SpecUploadResponse(BaseModel):
    filename: str
    test_case_count: int
    test_cases: List[TestCase]
    spec_path: str


class GenerateTestRequest(BaseModel):
    id: Optional[str] = "TC-CUSTOM"
    title: Optional[str] = "Custom Test"
    preconditions: Optional[str] = ""
    steps: Optional[str] = ""
    expected_result: Optional[str] = ""
