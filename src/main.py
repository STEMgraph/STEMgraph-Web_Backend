from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import exercises, authors, keywords, graph, admin

# setup the api object
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["https://stemgraph.boekelmann.net"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Router registrieren
app.include_router(exercises.router)
app.include_router(authors.router)
app.include_router(keywords.router)
app.include_router(graph.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    """Returns a greeting."""
    return {"message": "Welcome to STEMgraph API"}
