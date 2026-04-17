from fastapi import FastAPI
from api import exercises, authors, keywords, graph, admin

app = FastAPI()

# Router registrieren
app.include_router(exercises.router)
app.include_router(authors.router)
app.include_router(keywords.router)
app.include_router(graph.router)
app.include_router(admin.router)
