from pydantic import BaseModel
from typing import List, Optional

class URLRequest(BaseModel):
    url: Optional[str] = None
    html: Optional[str] = None
    css: Optional[str] = None
    filter: Optional[List[str]] = None