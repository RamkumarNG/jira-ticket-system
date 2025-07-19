from pydantic import BaseModel
from enum import Enum
from typing import Optional, List, Dict, Union

class RequestStatus(str, Enum):
    success = 'SUCCESS'
    failure = 'FAILURE'
    accepted = 'ACCEPTED'
    inprogress = 'INPROGRESS'

class ResponseStructure(BaseModel):
    request_id: Optional[str]
    status: Optional[RequestStatus]
    message: str

class FailureResponseStructure(ResponseStructure):
    """
    Failure Response Model
    """
    data: Optional[Union[str, Dict, List]]

class SuccessResponseStructure(ResponseStructure):
    """
    Success Response Model
    """
    data: Optional[Union[str, Dict, List]]  