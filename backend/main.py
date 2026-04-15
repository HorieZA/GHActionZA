from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from settings import settings
# ai-agent.py에서 router 객체를 가져옵니다.
from src.ai_agent import router as board_router


origins = [ settings.react_url ]

app = FastAPI()

app.add_middleware(
 CORSMiddleware,
 allow_origins=origins,
 allow_credentials=True,
 allow_methods=["*"],
 allow_headers=["*"],
)

# 요청하신 통합 방식 적용
apis = [board_router] # 향후 home.router, user.router 등 추가 가능

for router in apis:
    app.include_router(router)