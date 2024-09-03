from fastapi import FastAPI
from routs.user import user

app = FastAPI()
app.include_router(user)
