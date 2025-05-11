from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.core.config import settings
from app.services.monitoring import logger
from app.api.v1.main import api_router
from app.api.v1.docs import router as api_docs

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


# Main app
app = FastAPI(
    title="FastAPI Template",
    version="1.0.0",
    description=
        """<div style="display: flex; flex-direction: row; align-items: center; gap: 10px;">
            <img src='https://private-user-images.githubusercontent.com/62510516/442470820-5b2c3076-5d52-4d2b-9313-9a1eddca3e76.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDY5MzEwMTcsIm5iZiI6MTc0NjkzMDcxNywicGF0aCI6Ii82MjUxMDUxNi80NDI0NzA4MjAtNWIyYzMwNzYtNWQ1Mi00ZDJiLTkzMTMtOWExZWRkY2EzZTc2LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTA1MTElMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwNTExVDAyMzE1N1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTcwZWMyMzhkMzhmZmY5NTVkNzcxNWEyODUyNzY2ODI0ZDE2NjBkZTlhYjg2ZDVkZmE4YjNhZTg3ZGM1NzcwM2UmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.VhNV-w7fjo4PRWvojDe-ulliL0iD6tSNv3s--xf9WOc' width='45'/>
            <h1>FastAPI Complete Starter Kit</h1>
        </div>
        <p style="font-size: 1.1em;">
            A powerful, production-ready FastAPI starter packed with batteries included:
        </p>
        <ul style="font-size: 1.05em;">
            <li><strong>Passwordless authentication</strong> with multi-tenant & multi-role support (users, superusers, etc.)</li>
            <li><strong>Alembic</strong> for migrations, Pydantic models & schemas preconfigured</li>
            <li>Sample endpoints with <strong>extensive test coverage</strong></li>
            <li>Integrated CI/CD using <strong>GitHub Actions</strong></li>
            <li><strong>AWS-ready</strong> deployment: Lambda, API Gateway, ECR, RDS via CloudFormation</li>
        </ul>
        <h2 style="margin-top: 25px; font-size: 1.3em;">🚀 Getting Started</h2>
        <p style="font-size: 1.05em;">
            Visit the <a href="https://github.com/JaquesM/fastapi-template/wiki" target="_blank"><strong>Project Wiki</strong></a> for setup instructions, deployment guide, and architecture details.
        </p>
        <p style="font-size: 1.05em;">
            👉 A few good starting points:
        </p>
        <ul style="font-size: 1.05em;">
            <li>Understand the <strong>folder structure</strong> and core components</li>
            <li>Try out the <strong>auth flow</strong> using the sample frontend or test endpoints</li>
            <li>Customize user roles, permissions, or models to fit your needs</li>
            <li>Deploy your own version using the <strong>CloudFormation templates</strong></li>
        </ul>
        <hr style="margin-top: 40px; border: none; border-top: 1px solid #ccc;" />
        <footer style="font-size: 0.95em; text-align: center; color: #666; margin-top: 20px;">
            Built and maintained by 
            <a href="https://github.com/JaquesM" target="_blank">
                <strong>Jaques Missrie</strong>
            </a> — part of a series of <strong>ready-to-use templates</strong> for the open-source community.
        </footer>
    """,
    openapi_url="/openapi.json",
    docs_url="/swagger",
    generate_unique_id_function=custom_generate_unique_id,
    redirect_slashes=True,
    contact={
        "name": settings.EMAILS_FROM_NAME,
        "url": f"https://{settings.BASE_HOST}/contato",
        "email": settings.EMAILS_FROM_EMAIL,
    },
)

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # [settings.FRONTEND_HOST],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routes
app.include_router(api_router, prefix="/v1")

# Mount API Docs
app.include_router(api_docs, prefix="/docs", tags=["docs"])


handler = Mangum(app)
handler = logger.inject_lambda_context(handler, clear_state=True)

def lambda_handler(event, context):
    logger.info(f"Lambda event: {event}")
    response = handler(event, context)
    logger.info(f"Lambda response: {response}")
    return response
