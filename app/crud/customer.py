from sqlmodel import Session, select

from app.models import Customer


# Retrieve
# - Getters
def get_customer_by_subdomain(*, session: Session, customer_subdomain: str) -> Customer:
    if customer_subdomain == "home":
        return Customer(name="Home", subdomain=customer_subdomain)
    if customer_subdomain == "admin":
        return Customer(name="Admin", subdomain=customer_subdomain)

    statement = select(Customer).where(Customer.subdomain == customer_subdomain)
    session_customer = session.exec(statement).first()
    return session_customer

