from sqlmodel import SQLModel


# Input Schemas
class NewContact(SQLModel):
    name: str
    email: str
    phone: str
    company: str
