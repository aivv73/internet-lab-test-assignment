from pydantic import BaseModel, EmailStr, Field


class EmailMessageData(BaseModel):
    """Plain-text email message prepared by the email service."""

    to: EmailStr = Field(description="Recipient email address.")
    subject: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1)
