from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from mcp.server import MCPServer, Tool, Arg, String, Integer
from tools.sql import run_sql
from tools.scraper import launch_scraper
from tools.kpi import get_indicator, forecast_kpi
from datetime import timedelta
from auth import User, authenticate_user, create_access_token, get_current_user, check_permission
from pydantic import BaseModel
from typing import Dict

# Modèle pour la réponse de token
class Token(BaseModel):
    access_token: str
    token_type: str

app = FastAPI(title="MG Data MCP")

# Configuration OAuth2 pour l'authentification par token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

server = MCPServer(
    name="mg-data-mcp",
    description="Outils pour le pipeline Marne & Gondoire",
    version="0.1.0"
)

server.add_tool(
    Tool(
        name="run_sql",
        description="Exécute une requête SQL en lecture seule sur la base de données analytique",
        args=[Arg("query", String())],
        func=run_sql,
        permissions=["viewer", "editor"]
    )
)

server.add_tool(
    Tool(
        name="launch_scraper",
        description="Lance un spider Scrapy ou Playwright par nom",
        args=[Arg("spider", String()), Arg("url", String())],
        func=launch_scraper,
        permissions=["editor"]
    )
)

server.add_tool(
    Tool(
        name="get_indicator",
        description="Retourne la valeur d'un KPI pour une date donnée",
        args=[Arg("name", String()), Arg("date", String())],
        func=get_indicator,
        permissions=["viewer"]
    )
)

server.add_tool(
    Tool(
        name="forecast_kpi",
        description="Retourne une prévision pour un KPI donné",
        args=[Arg("name", String()), Arg("horizon", Integer())],
        func=forecast_kpi,
        permissions=["viewer"]
    )
)

app.mount("/mcp", server.as_fastapi())

# Endpoint pour l'authentification et la génération de tokens
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint pour s'authentifier et obtenir un token JWT
    """
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(
        data={"sub": user.username}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint pour vérifier le token et obtenir les informations de l'utilisateur
@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Endpoint pour obtenir les informations de l'utilisateur courant
    """
    return current_user

# Endpoint pour la documentation du serveur MCP
@app.get("/")
async def root():
    """
    Page d'accueil du serveur MCP
    """
    return {
        "name": "Marne & Gondoire MCP Server",
        "version": "0.1.0",
        "docs_url": "/docs",
        "mcp_endpoint": "/mcp"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
