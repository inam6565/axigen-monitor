from pydantic import BaseModel, Field

class ServerCreate(BaseModel):
    name: str = Field(..., example="Podbeez-Inam")
    hostname: str = Field(..., example="203.175.66.162")
    cli_port: int = Field(default=7000)
    webadmin_port: int = Field(default=9000)
    username: str
    password: str

class ResponseMessage(BaseModel):
    success: bool
    message: str
