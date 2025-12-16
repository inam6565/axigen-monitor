from pydantic import BaseModel, Field

class DeleteServerRequest(BaseModel):
    hostname: str = Field(..., example="203.175.66.162")

class ResponseMessage(BaseModel):
    success: bool
    message: str
