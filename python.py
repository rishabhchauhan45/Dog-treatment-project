#!/usr/bin/env python3
"""
PetVerse AI - Project Structure Generator
This script creates the complete file structure and all code files for the PetVerse AI application.
"""

import os
import json
from pathlib import Path

# Base directories
BASE_DIR = Path(".")
FRONTEND_DIR = BASE_DIR / "frontend"
BACKEND_DIR = BASE_DIR / "backend"
SRC_DIR = FRONTEND_DIR / "src"
COMPONENTS_DIR = SRC_DIR / "components"
UI_DIR = COMPONENTS_DIR / "ui"
PAGES_DIR = SRC_DIR / "pages"
CONTEXT_DIR = SRC_DIR / "context"
LIB_DIR = SRC_DIR / "lib"
HOOKS_DIR = SRC_DIR / "hooks"
UTILS_DIR = SRC_DIR / "utils"

# Ensure all directories exist
directories = [
    FRONTEND_DIR,
    BACKEND_DIR,
    SRC_DIR,
    COMPONENTS_DIR,
    UI_DIR,
    PAGES_DIR,
    CONTEXT_DIR,
    LIB_DIR,
    HOOKS_DIR,
    UTILS_DIR,
]

for d in directories:
    d.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created directory: {d}")

# ============================================================================
# BACKEND FILES
# ============================================================================

# server.py
with open(BACKEND_DIR / "server.py", "w") as f:
    f.write('''from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import base64
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta

from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent, TextDelta, StreamDone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ.get('JWT_SECRET', 'change-me')
JWT_ALGO = 'HS256'
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

app = FastAPI(title="PetVerse AI API")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# ---------- Models ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "pet_parent"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: str

class TokenResponse(BaseModel):
    access_token: str
    user: UserOut

class PetCreate(BaseModel):
    name: str
    species: str
    breed: Optional[str] = ""
    age: Optional[float] = 0
    weight: Optional[float] = 0
    color: Optional[str] = ""
    gender: Optional[str] = ""
    photo: Optional[str] = ""

class Pet(PetCreate):
    id: str
    owner_id: str
    created_at: str

class VaccinationCreate(BaseModel):
    pet_id: str
    name: str
    date: str
    next_due: Optional[str] = ""
    notes: Optional[str] = ""

class Vaccination(VaccinationCreate):
    id: str
    owner_id: str

class AppointmentCreate(BaseModel):
    pet_id: str
    vet_name: str
    date: str
    reason: str
    status: str = "scheduled"

class Appointment(AppointmentCreate):
    id: str
    owner_id: str

class ChatMessage(BaseModel):
    session_id: str
    message: str

class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = ""
    message: str

# ---------- Helpers ----------
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def verify_password(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    except Exception:
        return False

def create_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=30),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGO])
        user_id = payload.get("sub")
        user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
        if not user:
            raise HTTPException(401, "Invalid auth")
        return user
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid token")

def now_iso():
    return datetime.now(timezone.utc).isoformat()

# ---------- Auth ----------
@api_router.post("/auth/signup", response_model=TokenResponse)
async def signup(body: UserCreate):
    existing = await db.users.find_one({"email": body.email.lower()})
    if existing:
        raise HTTPException(400, "Email already registered")
    user_id = str(uuid.uuid4())
    doc = {
        "id": user_id,
        "name": body.name,
        "email": body.email.lower(),
        "password": hash_password(body.password),
        "role": body.role,
        "created_at": now_iso(),
    }
    await db.users.insert_one(doc)
    token = create_token(user_id)
    return TokenResponse(
        access_token=token,
        user=UserOut(id=user_id, name=body.name, email=body.email.lower(), role=body.role),
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(body: UserLogin):
    user = await db.users.find_one({"email": body.email.lower()})
    if not user or not verify_password(body.password, user["password"]):
        raise HTTPException(401, "Invalid credentials")
    token = create_token(user["id"])
    return TokenResponse(
        access_token=token,
        user=UserOut(id=user["id"], name=user["name"], email=user["email"], role=user["role"]),
    )

@api_router.get("/auth/me", response_model=UserOut)
async def me(user=Depends(get_current_user)):
    return UserOut(id=user["id"], name=user["name"], email=user["email"], role=user["role"])

# ---------- Pets ----------
@api_router.post("/pets", response_model=Pet)
async def create_pet(body: PetCreate, user=Depends(get_current_user)):
    pid = str(uuid.uuid4())
    doc = {**body.model_dump(), "id": pid, "owner_id": user["id"], "created_at": now_iso()}
    await db.pets.insert_one(doc)
    doc.pop("_id", None)
    return doc

@api_router.get("/pets", response_model=List[Pet])
async def list_pets(user=Depends(get_current_user)):
    pets = await db.pets.find({"owner_id": user["id"]}, {"_id": 0}).to_list(200)
    return pets

@api_router.delete("/pets/{pet_id}")
async def delete_pet(pet_id: str, user=Depends(get_current_user)):
    await db.pets.delete_one({"id": pet_id, "owner_id": user["id"]})
    return {"ok": True}

# ---------- Vaccinations ----------
@api_router.post("/vaccinations", response_model=Vaccination)
async def add_vacc(body: VaccinationCreate, user=Depends(get_current_user)):
    vid = str(uuid.uuid4())
    doc = {**body.model_dump(), "id": vid, "owner_id": user["id"]}
    await db.vaccinations.insert_one(doc)
    doc.pop("_id", None)
    return doc

@api_router.get("/vaccinations", response_model=List[Vaccination])
async def list_vacc(user=Depends(get_current_user)):
    items = await db.vaccinations.find({"owner_id": user["id"]}, {"_id": 0}).to_list(500)
    return items

# ---------- Appointments ----------
@api_router.post("/appointments", response_model=Appointment)
async def add_appt(body: AppointmentCreate, user=Depends(get_current_user)):
    aid = str(uuid.uuid4())
    doc = {**body.model_dump(), "id": aid, "owner_id": user["id"]}
    await db.appointments.insert_one(doc)
    doc.pop("_id", None)
    return doc

@api_router.get("/appointments", response_model=List[Appointment])
async def list_appt(user=Depends(get_current_user)):
    items = await db.appointments.find({"owner_id": user["id"]}, {"_id": 0}).to_list(200)
    return items

# ---------- AI: Pet Assistant (Streaming) ----------
@api_router.post("/ai/chat")
async def ai_chat(body: ChatMessage, user=Depends(get_current_user)):
    sys_msg = (
        "You are Dr. Whiskers, an AI Pet Care Assistant for PetVerse AI. "
        "You provide helpful, accurate, friendly advice on pet health, nutrition, behavior, "
        "training, and general wellness. Always recommend consulting a licensed veterinarian "
        "for medical concerns. Be warm, concise, and professional."
    )
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=body.session_id,
        system_message=sys_msg,
    ).with_model("anthropic", "claude-sonnet-4-5-20250929")

    async def event_gen():
        try:
            async for ev in chat.stream_message(UserMessage(text=body.message)):
                if isinstance(ev, TextDelta):
                    yield f"data: {ev.content}\\n\\n"
                elif isinstance(ev, StreamDone):
                    yield "data: [DONE]\\n\\n"
                    break
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\\n\\n"

    await db.chat_messages.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "session_id": body.session_id,
        "role": "user",
        "content": body.message,
        "created_at": now_iso(),
    })

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

# ---------- AI: Breed Detection ----------
@api_router.post("/ai/breed-detect")
async def breed_detect(file: UploadFile = File(...), user=Depends(get_current_user)):
    contents = await file.read()
    b64 = base64.b64encode(contents).decode()
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"breed-{uuid.uuid4()}",
        system_message=(
            "You are an expert pet breed identifier. Analyze the photo and return ONLY a short response in this format:\\n"
            "Breed: <name>\\nConfidence: <low/medium/high>\\nTraits: <2-3 short traits>\\nCare Tips: <1-2 tips>"
        ),
    ).with_model("anthropic", "claude-sonnet-4-5-20250929")

    result = ""
    try:
        async for ev in chat.stream_message(UserMessage(
            text="Identify the breed in this image.",
            file_contents=[ImageContent(image_base64=b64)],
        )):
            if isinstance(ev, TextDelta):
                result += ev.content
            elif isinstance(ev, StreamDone):
                break
    except Exception as e:
        raise HTTPException(500, f"AI error: {e}")
    return {"result": result}

# ---------- AI: Disease Detection ----------
@api_router.post("/ai/disease-detect")
async def disease_detect(file: UploadFile = File(...), symptoms: str = Form(""), user=Depends(get_current_user)):
    contents = await file.read()
    b64 = base64.b64encode(contents).decode()
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"disease-{uuid.uuid4()}",
        system_message=(
            "You are a veterinary AI triage assistant. Given a photo and symptoms, suggest possible conditions. "
            "Always include a clear disclaimer that this is not a diagnosis and to consult a vet. "
            "Format: Observation: <what you see>\\nPossible Conditions: <list>\\nUrgency: <low/medium/high>\\n"
            "Recommended Action: <next steps>\\nDisclaimer: ..."
        ),
    ).with_model("anthropic", "claude-sonnet-4-5-20250929")

    result = ""
    try:
        async for ev in chat.stream_message(UserMessage(
            text=f"Symptoms reported: {symptoms or 'None provided'}. Please assess.",
            file_contents=[ImageContent(image_base64=b64)],
        )):
            if isinstance(ev, TextDelta):
                result += ev.content
            elif isinstance(ev, StreamDone):
                break
    except Exception as e:
        raise HTTPException(500, f"AI error: {e}")
    return {"result": result}

# ---------- Marketplace & Adoption (public seed data) ----------
@api_router.get("/marketplace")
async def marketplace():
    return [
        {"id": "m1", "name": "Premium Grain-Free Dog Food", "price": 49.99, "category": "Food", "image": "https://images.unsplash.com/photo-1589924691995-400dc9ecc119?w=600&q=80", "rating": 4.8},
        {"id": "m2", "name": "Orthopedic Memory Foam Bed", "price": 89.00, "category": "Comfort", "image": "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=600&q=80", "rating": 4.9},
        {"id": "m3", "name": "Smart GPS Pet Tracker", "price": 129.00, "category": "Tech", "image": "https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=600&q=80", "rating": 4.7},
        {"id": "m4", "name": "Interactive Puzzle Toy", "price": 24.50, "category": "Toys", "image": "https://images.unsplash.com/photo-1535930891776-0c2dfb7fda1a?w=600&q=80", "rating": 4.6},
        {"id": "m5", "name": "Organic Cat Treats", "price": 14.99, "category": "Treats", "image": "https://images.unsplash.com/photo-1574144611937-0df059b5ef3e?w=600&q=80", "rating": 4.5},
        {"id": "m6", "name": "Self-Cleaning Litter Box", "price": 199.00, "category": "Hygiene", "image": "https://images.unsplash.com/photo-1545249390-6bdfa286032f?w=600&q=80", "rating": 4.7},
    ]

@api_router.get("/adoption")
async def adoption():
    return [
        {"id": "a1", "name": "Luna", "species": "Dog", "breed": "Golden Retriever", "age": 2, "location": "Brooklyn, NY", "image": "https://images.unsplash.com/photo-1552053831-71594a27632d?w=600&q=80", "story": "Sweet, gentle, loves swimming."},
        {"id": "a2", "name": "Milo", "species": "Cat", "breed": "Tabby", "age": 1, "location": "Austin, TX", "image": "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=600&q=80", "story": "Playful kitten looking for a calm home."},
        {"id": "a3", "name": "Cooper", "species": "Dog", "breed": "Beagle Mix", "age": 4, "location": "Seattle, WA", "image": "https://images.unsplash.com/photo-1505628346881-b72b27e84530?w=600&q=80", "story": "Loyal and energetic, great with kids."},
        {"id": "a4", "name": "Bella", "species": "Cat", "breed": "Siamese", "age": 3, "location": "Miami, FL", "image": "https://images.unsplash.com/photo-1573865526739-10659fec78a5?w=600&q=80", "story": "Affectionate lap-cat, loves naps."},
    ]

@api_router.post("/contact")
async def contact(msg: ContactMessage):
    doc = {**msg.model_dump(), "id": str(uuid.uuid4()), "created_at": now_iso()}
    await db.contact_messages.insert_one(doc)
    return {"ok": True}

@api_router.get("/")
async def root():
    return {"name": "PetVerse AI", "version": "1.0.0"}

# ---------- Wire-up ----------
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
''')
print("✅ Created: backend/server.py")

# .env
with open(BACKEND_DIR / ".env", "w") as f:
    f.write('''MONGO_URL="mongodb://localhost:27017"
DB_NAME="petverse_db"
CORS_ORIGINS="*"
EMERGENT_LLM_KEY=sk-emergent-8C9BeA503Cb1dF7505
JWT_SECRET=petverse-prod-secret-key-2026-change-this
''')
print("✅ Created: backend/.env")

# requirements.txt
with open(BACKEND_DIR / "requirements.txt", "w") as f:
    f.write('''fastapi==0.110.1
uvicorn==0.25.0
boto3>=1.34.129
requests-oauthlib>=2.0.0
cryptography>=42.0.8
python-dotenv>=1.0.1
pymongo==4.5.0
pydantic>=2.6.4
email-validator>=2.2.0
pyjwt>=2.10.1
bcrypt==4.1.3
passlib>=1.7.4
tzdata>=2024.2
motor==3.3.1
pytest>=8.0.0
black>=24.1.1
isort>=5.13.2
flake8>=7.0.0
mypy>=1.8.0
python-jose>=3.3.0
requests>=2.31.0
pandas>=2.2.0
numpy>=1.26.0
python-multipart>=0.0.9
jq>=1.6.0
typer>=0.9.0
emergentintegrations==0.2.0
''')
print("✅ Created: backend/requirements.txt")

# ============================================================================
# FRONTEND FILES
# ============================================================================

# package.json
with open(FRONTEND_DIR / "package.json", "w") as f:
    f.write('''{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@hookform/resolvers": "5.0.1",
    "@radix-ui/react-accordion": "1.2.8",
    "@radix-ui/react-alert-dialog": "1.1.11",
    "@radix-ui/react-aspect-ratio": "1.1.4",
    "@radix-ui/react-avatar": "1.1.7",
    "@radix-ui/react-checkbox": "1.2.3",
    "@radix-ui/react-collapsible": "1.1.8",
    "@radix-ui/react-context-menu": "2.2.12",
    "@radix-ui/react-dialog": "1.1.11",
    "@radix-ui/react-dropdown-menu": "2.1.12",
    "@radix-ui/react-hover-card": "1.1.11",
    "@radix-ui/react-label": "2.1.4",
    "@radix-ui/react-menubar": "1.1.12",
    "@radix-ui/react-navigation-menu": "1.2.10",
    "@radix-ui/react-popover": "1.1.11",
    "@radix-ui/react-progress": "1.1.4",
    "@radix-ui/react-radio-group": "1.3.4",
    "@radix-ui/react-scroll-area": "1.2.6",
    "@radix-ui/react-select": "2.2.2",
    "@radix-ui/react-separator": "1.1.4",
    "@radix-ui/react-slider": "1.3.2",
    "@radix-ui/react-slot": "1.2.0",
    "@radix-ui/react-switch": "1.2.2",
    "@radix-ui/react-tabs": "1.1.9",
    "@radix-ui/react-toast": "1.2.11",
    "@radix-ui/react-toggle": "1.1.6",
    "@radix-ui/react-toggle-group": "1.1.7",
    "@radix-ui/react-tooltip": "1.2.4",
    "@tanstack/react-query": "5.56.2",
    "axios": "1.8.4",
    "class-variance-authority": "0.7.1",
    "clsx": "2.1.1",
    "cmdk": "1.1.1",
    "cra-template": "1.2.0",
    "date-fns": "4.1.0",
    "dayjs": "1.11.13",
    "embla-carousel-react": "8.6.0",
    "framer-motion": "11.18.0",
    "input-otp": "1.4.2",
    "lodash": "4.18.1",
    "lucide-react": "0.516.0",
    "next-themes": "0.4.6",
    "react": "19.0.0",
    "react-day-picker": "8.10.1",
    "react-dom": "19.0.0",
    "react-hook-form": "7.56.2",
    "react-resizable-panels": "3.0.1",
    "react-router-dom": "7.5.1",
    "react-scripts": "5.0.1",
    "recharts": "3.6.0",
    "sonner": "2.0.3",
    "swr": "2.3.8",
    "tailwind-merge": "3.2.0",
    "tailwindcss-animate": "1.0.7",
    "vaul": "1.1.2",
    "zod": "3.24.4"
  },
  "scripts": {
    "start": "craco start",
    "build": "craco build",
    "test": "craco test"
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "devDependencies": {
    "@babel/plugin-proposal-private-property-in-object": "7.21.11",
    "@craco/craco": "7.1.0",
    "@emergentbase/visual-edits": "https://assets.emergent.sh/npm/emergentbase-visual-edits-1.0.8.tgz",
    "@eslint/js": "9.23.0",
    "@types/lodash": "4.17.24",
    "autoprefixer": "10.4.20",
    "dotenv": "16.4.5",
    "eslint": "9.23.0",
    "eslint-plugin-import": "2.31.0",
    "eslint-plugin-jsx-a11y": "6.10.2",
    "eslint-plugin-react": "7.37.4",
    "eslint-plugin-react-hooks": "5.2.0",
    "globals": "15.15.0",
    "postcss": "8.4.49",
    "tailwindcss": "3.4.17"
  },
  "packageManager": "yarn@1.22.22+sha512.a6b2f7906b721bba3d67d4aff083df04dad64c399707841b7acf00f6b133b7ac24255f2652fa22ae3534329dc6180534e98d17432037ff6fd140556e2bb3137e"
}
''')
print("✅ Created: frontend/package.json")

# .env
with open(FRONTEND_DIR / ".env", "w") as f:
    f.write('''REACT_APP_BACKEND_URL=https://ai-petcare-1.preview.emergentagent.com
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false
''')
print("✅ Created: frontend/.env")

# craco.config.js
with open(FRONTEND_DIR / "craco.config.js", "w") as f:
    f.write('''module.exports = {
  style: {
    postcss: {
      plugins: [
        require('tailwindcss'),
        require('autoprefixer'),
      ],
    },
  },
};
''')
print("✅ Created: frontend/craco.config.js")

# tailwind.config.js
with open(FRONTEND_DIR / "tailwind.config.js", "w") as f:
    f.write('''/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
''')
print("✅ Created: frontend/tailwind.config.js")

# ============================================================================
# FRONTEND SRC FILES
# ============================================================================

# index.css
with open(SRC_DIR / "index.css", "w") as f:
    f.write('''@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
    margin: 0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background: #000;
    color: #fff;
}

.font-display { font-family: 'Outfit', sans-serif; }
.font-mono { font-family: 'JetBrains Mono', monospace; }

@layer base {
    :root {
        --background: 0 0% 0%;
        --foreground: 0 0% 98%;
        --card: 0 0% 4%;
        --card-foreground: 0 0% 98%;
        --popover: 0 0% 4%;
        --popover-foreground: 0 0% 98%;
        --primary: 0 0% 98%;
        --primary-foreground: 0 0% 9%;
        --secondary: 0 0% 9%;
        --secondary-foreground: 0 0% 98%;
        --muted: 0 0% 9%;
        --muted-foreground: 0 0% 64%;
        --accent: 73 90% 62%;
        --accent-foreground: 0 0% 0%;
        --destructive: 0 62% 50%;
        --destructive-foreground: 0 0% 98%;
        --border: 0 0% 14%;
        --input: 0 0% 14%;
        --ring: 73 90% 62%;
        --radius: 1rem;
    }
}

@layer base {
    * { @apply border-border; }
    body { @apply bg-background text-foreground; }
    html { scroll-behavior: smooth; }
    ::selection { background: #D9F845; color: #000; }
}

.bg-grid {
    background-image:
        linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px);
    background-size: 60px 60px;
}

.bg-grid-fade {
    mask-image: radial-gradient(ellipse at center, black 30%, transparent 75%);
    -webkit-mask-image: radial-gradient(ellipse at center, black 30%, transparent 75%);
}

.glow-accent {
    box-shadow: 0 0 80px rgba(217, 248, 69, 0.25), 0 0 30px rgba(217, 248, 69, 0.15);
}

.text-balance { text-wrap: balance; }

.glass {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.marquee {
    display: flex;
    width: max-content;
    animation: marquee 40s linear infinite;
}
@keyframes marquee {
    from { transform: translateX(0); }
    to { transform: translateX(-50%); }
}

.dot-pattern {
    background-image: radial-gradient(rgba(255,255,255,0.08) 1px, transparent 1px);
    background-size: 24px 24px;
}

::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: #0a0a0a; }
::-webkit-scrollbar-thumb { background: #1f1f1f; border-radius: 6px; }
::-webkit-scrollbar-thumb:hover { background: #2f2f2f; }
''')
print("✅ Created: src/index.css")

# App.css
with open(SRC_DIR / "App.css", "w") as f:
    f.write('''.App { min-height: 100vh; background: #000; }
''')
print("✅ Created: src/App.css")

# App.js
with open(SRC_DIR / "App.js", "w") as f:
    f.write('''import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { Toaster } from "./components/ui/sonner";
import MarketingLayout from "./components/MarketingLayout";
import Home from "./pages/Home";
import About from "./pages/About";
import Products from "./pages/Products";
import Technology from "./pages/Technology";
import Solutions from "./pages/Solutions";
import Pricing from "./pages/Pricing";
import Contact from "./pages/Contact";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import "./App.css";

const Protected = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen bg-black flex items-center justify-center text-white">Loading…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
};

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<MarketingLayout><Outlet /></MarketingLayout>}>
              <Route path="/" element={<Home />} />
              <Route path="/about" element={<About />} />
              <Route path="/products" element={<Products />} />
              <Route path="/technology" element={<Technology />} />
              <Route path="/solutions" element={<Solutions />} />
              <Route path="/pricing" element={<Pricing />} />
              <Route path="/contact" element={<Contact />} />
            </Route>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/dashboard/*" element={<Protected><Dashboard /></Protected>} />
          </Routes>
          <Toaster theme="dark" position="top-right" />
        </BrowserRouter>
      </AuthProvider>
    </div>
  );
}

export default App;
''')
print("✅ Created: src/App.js")

# index.js
with open(SRC_DIR / "index.js", "w") as f:
    f.write('''import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
''')
print("✅ Created: src/index.js")
print("🎉 All files generated successfully!")