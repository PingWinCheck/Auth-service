from fastapi import FastAPI
import uvicorn
from auth.routers import router as router_auth

app = FastAPI()
app.include_router(router_auth)


def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
