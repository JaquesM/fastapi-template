from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

# Stoplight Elements Docs
@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def api_docs():
    html_content = """
	<!doctype html>
	<html lang="en">
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
		<title>Fastapi Template API Docs</title>

        <!-- Favicon -->
        <link rel="icon" type="image/png" href="https://private-user-images.githubusercontent.com/62510516/442470822-de9a89d4-f3a8-4adc-9511-890b7e96ca72.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDY5MzEwMTcsIm5iZiI6MTc0NjkzMDcxNywicGF0aCI6Ii82MjUxMDUxNi80NDI0NzA4MjItZGU5YTg5ZDQtZjNhOC00YWRjLTk1MTEtODkwYjdlOTZjYTcyLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTA1MTElMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwNTExVDAyMzE1N1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTlmZjQ2NmU4OTZmMmExM2VjZTU5MmFjNmJjOTFjNzc4NTdmYmM1ODU1NjNhNTNiMmY1NjE2NTA3YTlkZmEwZGUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.Re4tbr4Wn93_Ndi0AAVARSzlWlK9smKg9JY748fDgXM"> 

        <!-- Google Fonts: Nunito -->
        <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700&display=swap" rel="stylesheet">

        <!-- Stoplight Elements -->
		<script src="https://unpkg.com/@stoplight/elements/web-components.min.js"></script>
		<link rel="stylesheet" href="https://unpkg.com/@stoplight/elements/styles.min.css">
        
        <!-- Custom Styles -->
        <style>
            elements-api {
                --font-prose: "Nunito", sans-serif;
            }

			.svg-inline--fa {
				color: #007bff !important;
            }
        </style>
	</head>
	<body>
		<elements-api
          	apiDescriptionUrl="/openapi.json"
			router="hash"
            layout="sidebar"
            hideSchemas="true"
            hideExport="true"
		/>
	</body>
	</html>"""
    return HTMLResponse(content=html_content)

