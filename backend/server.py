from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form
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

class TextDelta:
    def __init__(self, content):
        self.content = content

class StreamDone:
    pass

class UserMessage:
    def __init__(self, text, file_contents=None):
        self.text = text
        self.file_contents = file_contents

class ImageContent:
    def __init__(self, image_base64):
        self.image_base64 = image_base64

class LlmChat:
    def __init__(self, api_key, session_id, system_message):
        pass
    def with_model(self, provider, model):
        return self
    async def stream_message(self, message):
        import asyncio
        yield TextDelta("This is a simulated AI response since the LLM integration is currently mocked. ")
        await asyncio.sleep(0.5)
        yield TextDelta(f"You said: {message.text}")
        yield StreamDone()

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
                    yield f"data: {ev.content}\n\n"
                elif isinstance(ev, StreamDone):
                    yield "data: [DONE]\n\n"
                    break
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

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
            "You are an expert pet breed identifier. Analyze the photo and return ONLY a short response in this format:\n"
            "Breed: <name>\nConfidence: <low/medium/high>\nTraits: <2-3 short traits>\nCare Tips: <1-2 tips>"
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
            "Format: Observation: <what you see>\nPossible Conditions: <list>\nUrgency: <low/medium/high>\n"
            "Recommended Action: <next steps>\nDisclaimer: ..."
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
