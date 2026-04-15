from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from src.db import save, findAll, findOne, saveParams
from settings import settings
import requests
import json

router = APIRouter(prefix="/api")

# =========================
# Request
# =========================
class ChatRequest(BaseModel):
  message: str

# ==========================
# AI Agent 응답 스키마 (작업 의도 파악 추가)
# ==========================
class AgentResponse(BaseModel):
  action: str = Field(description="요청된 작업. 'CREATE', 'UPDATE', 'DELETE' 중 하나를 반환하세요.")
  name: str = Field(description="작성자 이름 (작업 대상)") 
  title: str = Field(description="제목 (등록 및 수정 시)")
  content: str = Field(description="내용 (등록 및 수정 시)")


# =========================
# 1. 데이터 분석가
# =========================
class DataAnalyst:

  def __init__(self):
    self.model = settings.ollama_model_name
    self.url = f"{settings.ollama_base_url}/api/generate"

  def analyze(self, user_input: str):
    schema_str = json.dumps(AgentResponse.model_json_schema(), ensure_ascii=False)
    """
      데이터 분석 및 수집 전문가 노드: 자연어에서 의도(Action)와 데이터 추출
      자연어 → 구조화 데이터 (name, title, content 추출)
    """
    prompt = f"""
      [지시사항]
      당신은 데이터 분석 전문가입니다. 사용자의 입력을 분석하여 JSON 스키마에 맞게 데이터를 추출하세요.

      [추출 로직 및 규칙]
      name (이름): "XX의", "XX가", "XX님" 등 작업의 주체나 대상을 나타내는 고유 명사를 반드시 추출하세요. (예: "강남의 제목을" -> name: "강남")
      title (제목): 새로 설정하거나 변경하려는 핵심 제목 문구를 반드시 추출하세요. 제목이 없는 경우 빈 문자열("")로 설정하세요.
      content (내용): 상세 설명이나 변경 내용을 반드시 추출하세요. 내용이 없는 경우 빈 문자열("")로 설정하세요.

      [데이터 스키마]
      {schema_str}

      [출력 형식]
      JSON 형식으로만 답변하세요.
      
      [사용자 입력]
      {user_input}
    """

    response = requests.post(self.url, json={
      "model": self.model,
      "prompt": prompt,
      "stream": False,
      "format": "json"
    })

    return json.loads(response.json()['response'])


# =========================
# 2. DB 전문가(의도 파악 및 DB 처리)
# =========================
class ActionDBExpert:

  def __init__(self):
    self.model = settings.ollama_model_name
    self.url = f"{settings.ollama_base_url}/api/generate"

  def process(self, user_input: str, analyzed_data: dict):

    schema = {
      "action": "CREATE | UPDATE | DELETE",
      "name": "string",
      "title": "string",
      "content": "string"
    }

    prompt = f"""
      [지시사항]
      당신은 데이터 처리 전문가입니다.
      사용자의 의도를 파악하고 DB에 저장할 최종 데이터를 생성하세요.

      [목표]
      1. 반드시 action 결정 (CREATE / UPDATE / DELETE)
      2. content에서 반드시 "수정해줘", "지워줘" 같은 명령어 제거
      3. 반드시 최종 DB 저장 형태 생성

      [현재 분석 데이터]
      {json.dumps(analyzed_data, ensure_ascii=False)}

      [사용자 입력]
      {user_input}

      [출력 형식]
      반드시 아래 JSON으로만 응답:
      {json.dumps(schema, ensure_ascii=False)}
    """

    response = requests.post(self.url, json={
      "model": self.model,
      "prompt": prompt,
      "stream": False,
      "format": "json"
    })

    result = json.loads(response.json()['response'])

    # -------------------------
    # DB 처리
    # -------------------------
    create_sql = """
    CREATE TABLE IF NOT EXISTS boards (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(50),
      title VARCHAR(200),
      content TEXT,
      reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      mod_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      is_deleted TINYINT(1) DEFAULT 0
    )
    """
    save(create_sql)

    action = result.get("action", "CREATE")
    name = result.get("name", "")
    title = result.get("title", "")
    content = result.get("content", "")

    if action == "CREATE":
      sql = f"INSERT INTO boards (name, title, content) VALUES ('{name}', '{title}', '{content}')"
      db_result = save(sql)

    elif action == "UPDATE":
      sql = f"UPDATE boards SET title=IFNULL(%s, title), content=IFNULL(%s, content) WHERE name=%s AND is_deleted=0"
      params = (title if title else None, content if content else None, name)
      db_result = saveParams(sql, params)

    elif action == "DELETE":
      sql = f"UPDATE boards SET is_deleted=1 WHERE name='{name}' AND is_deleted=0"
      db_result = save(sql)

    else:
      db_result = False

    return {
      "action": action,
      "data": result,
      "db_result": db_result
    }


# =========================
# 3. Orchestrator (핵심 흐름)
# =========================
class AIAgent:

  def __init__(self):
    self.analyst = DataAnalyst()
    self.action_db = ActionDBExpert()

  def run(self, user_input: str):

    # 1. 데이터 분석
    analyzed_data = self.analyst.analyze(user_input)

    # 2. 의도 + DB 처리 (통합)
    result = self.action_db.process(user_input, analyzed_data)

    return result

agent = AIAgent()

# =========================
# API
# =========================
@router.post("/chat")
async def chat(req: ChatRequest):
  try:
    result = agent.run(req.message)
    return {"status": "success", "result": result}

  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.get("/boards")
async def get_boards():
  sql = "SELECT id, name, title, content, reg_date FROM boards WHERE is_deleted=0 ORDER BY reg_date DESC"
  return findAll(sql)


@router.get("/boards/{id}")
async def get_board(id: int):
  sql = f"SELECT * FROM boards WHERE id={id} AND is_deleted=0"
  return findOne(sql)