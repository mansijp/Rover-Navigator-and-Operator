from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers.Server import router as server_router
import uvicorn, os
from fastapi import Request, FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()

base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "views", "static")
templates_dir = os.path.join(base_dir, "views", "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory=templates_dir)

app.include_router(server_router, prefix="/lab4")

@app.get("/")
async def root():
    return RedirectResponse("/lab4", status_code=200)


@app.get("/lab4")
async def root(request: Request):
    return templates.TemplateResponse("operator.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.environ.get("ENVIRONMENT") == "dev" else False,
        workers=1,
    )