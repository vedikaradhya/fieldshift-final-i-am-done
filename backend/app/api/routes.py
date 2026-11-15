from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.geospatial.area import geojson_area_hectares
from app.integrations.nasa.power import daily_weather
from app.services.farm_context import farm_context
from app.models import AuditEvent, Farm, Field, SessionToken, User
from app.rotation.engine import RotationRequest, recommend
from app.schemas.contracts import DeleteAccountRequest, FarmInput, FarmOut, FieldInput, FieldOut, LoginRequest, RegisterRequest, TokenOut, UserOut, UserUpdate
from app.security.auth import create_access_token, create_refresh_token, current_user, decode_token, hash_password, revoke_token_id, token_id_hash, verify_password
from app.core.config import get_settings

router = APIRouter(prefix="/api/v1")

def audit(db: Session, actor_id: int | None, event_type: str, resource_type: str, resource_id: str | None = None, metadata: dict | None = None) -> None:
    db.add(AuditEvent(actor_id=actor_id, event_type=event_type, resource_type=resource_type, resource_id=resource_id, metadata_json=metadata))

def token_response(user: User, db: Session, response: Response) -> TokenOut:
    refresh_token = create_refresh_token(user, db)
    settings = get_settings()
    response.set_cookie("refresh_token", refresh_token, max_age=settings.refresh_token_expire_days * 86400, httponly=True, secure=settings.secure_cookies, samesite="strict", domain=settings.cookie_domain, path="/api/v1/auth")
    return TokenOut(access_token=create_access_token(user), user=user)

@router.post("/auth/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == body.email.lower())): raise HTTPException(409, "Email already registered")
    user = User(name=body.name, email=body.email.lower(), phone=body.phone, password_hash=hash_password(body.password))
    db.add(user); db.commit(); db.refresh(user)
    audit(db, user.id, "user.registered", "user", str(user.id)); payload = token_response(user, db, response); db.commit()
    return payload

@router.post("/auth/login", response_model=TokenOut)
def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if not user or not verify_password(body.password, user.password_hash) or not user.is_active: raise HTTPException(401, "Invalid email or password")
    audit(db, user.id, "user.logged_in", "user", str(user.id)); payload = token_response(user, db, response); db.commit()
    return payload

@router.post("/auth/refresh", response_model=TokenOut)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    raw_token = request.cookies.get("refresh_token")
    if not raw_token: raise HTTPException(401, "Refresh token not found")
    origin = request.headers.get("origin")
    if origin and origin not in get_settings().cors_origin_list: raise HTTPException(403, "Untrusted request origin")
    payload = decode_token(raw_token, "refresh")
    session = db.scalar(select(SessionToken).where(SessionToken.token_id_hash == token_id_hash(payload["jti"])))
    now = datetime.now(timezone.utc)
    expiry = session.expires_at.replace(tzinfo=timezone.utc) if session and session.expires_at.tzinfo is None else (session.expires_at if session else now)
    if not session or session.revoked_at or expiry <= now: raise HTTPException(401, "Refresh session is invalid")
    user = db.get(User, int(payload["sub"]))
    if not user or not user.is_active: raise HTTPException(401, "Refresh session is invalid")
    session.revoked_at = now; audit(db, user.id, "user.session_rotated", "session", str(session.id)); result = token_response(user, db, response); db.commit()
    return result

@router.post("/auth/logout", status_code=204)
def logout(request: Request, response: Response, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    raw_access = request.headers.get("authorization", "").removeprefix("Bearer ")
    payload = decode_token(raw_access, "access")
    revoke_token_id(db, payload["jti"], datetime.fromtimestamp(payload["exp"], tz=timezone.utc))
    refresh = request.cookies.get("refresh_token")
    if refresh:
        try:
            refresh_payload = decode_token(refresh, "refresh")
            session = db.scalar(select(SessionToken).where(SessionToken.token_id_hash == token_id_hash(refresh_payload["jti"])))
            if session: session.revoked_at = datetime.now(timezone.utc)
        except HTTPException: pass
    audit(db, user.id, "user.logged_out", "user", str(user.id)); db.commit()
    response.delete_cookie("refresh_token", domain=get_settings().cookie_domain, path="/api/v1/auth")
    response.status_code = 204
    return response

@router.get("/users/me", response_model=UserOut)
def me(user: User = Depends(current_user)): return user

@router.patch("/users/me", response_model=UserOut)
def update_me(body: UserUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    for key, value in body.model_dump(exclude_unset=True).items(): setattr(user, key, value)
    audit(db, user.id, "user.profile_updated", "user", str(user.id)); db.commit(); db.refresh(user); return user

@router.get("/users/me/export")
def export_me(db: Session = Depends(get_db), user: User = Depends(current_user)):
    farms = db.scalars(select(Farm).where(Farm.owner_id == user.id)).all()
    export = {"generated_at": datetime.now(timezone.utc).isoformat(), "user": UserOut.model_validate(user).model_dump(mode="json"), "farms": [{"id": farm.id, "name": farm.name, "boundary": farm.boundary, "area_hectares": farm.area_hectares, "fields": [{"id": field.id, "name": field.name, "boundary": field.boundary, "area_hectares": field.area_hectares} for field in farm.fields]} for farm in farms]}
    audit(db, user.id, "user.data_exported", "user", str(user.id)); db.commit()
    return JSONResponse(export, headers={"Content-Disposition": "attachment; filename=agrispace-data-export.json", "Cache-Control": "no-store"})

@router.delete("/users/me", status_code=204)
def delete_me(body: DeleteAccountRequest, response: Response, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Response:
    if not verify_password(body.password, user.password_hash): raise HTTPException(401, "Invalid password")
    audit(db, user.id, "user.account_deleted", "user", str(user.id)); db.delete(user); db.commit()
    response.delete_cookie("refresh_token", domain=get_settings().cookie_domain, path="/api/v1/auth"); response.status_code = 204; return response

def owned_farm(farm_id: int, db: Session, user: User) -> Farm:
    farm = db.get(Farm, farm_id)
    if not farm: raise HTTPException(404, "Farm not found")
    if farm.owner_id != user.id and user.role.value != "administrator": raise HTTPException(403, "You do not have access to this farm")
    return farm

@router.get("/farms", response_model=list[FarmOut])
def list_farms(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return db.scalars(select(Farm).where(Farm.owner_id == user.id).order_by(Farm.created_at.desc())).all()

@router.post("/farms", response_model=FarmOut, status_code=201)
def create_farm(body: FarmInput, db: Session = Depends(get_db), user: User = Depends(current_user)):
    farm = Farm(owner_id=user.id, **body.model_dump(), area_hectares=geojson_area_hectares(body.boundary))
    db.add(farm); db.commit(); db.refresh(farm); audit(db, user.id, "farm.created", "farm", str(farm.id)); db.commit(); return farm

@router.get("/farms/{farm_id}", response_model=FarmOut)
def get_farm(farm_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)): return owned_farm(farm_id, db, user)

@router.patch("/farms/{farm_id}", response_model=FarmOut)
def update_farm(farm_id: int, body: FarmInput, db: Session = Depends(get_db), user: User = Depends(current_user)):
    farm = owned_farm(farm_id, db, user)
    for key, value in body.model_dump().items(): setattr(farm, key, value)
    farm.area_hectares = geojson_area_hectares(body.boundary); db.commit(); db.refresh(farm); return farm

@router.delete("/farms/{farm_id}", status_code=204)
def delete_farm(farm_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    farm = owned_farm(farm_id, db, user); audit(db, user.id, "farm.deleted", "farm", str(farm.id)); db.delete(farm); db.commit(); return Response(status_code=204)

@router.get("/farms/{farm_id}/fields", response_model=list[FieldOut])
def list_fields(farm_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owned_farm(farm_id, db, user)
    return db.scalars(select(Field).where(Field.farm_id == farm_id)).all()

@router.post("/farms/{farm_id}/fields", response_model=FieldOut, status_code=201)
def create_field(farm_id: int, body: FieldInput, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owned_farm(farm_id, db, user)
    field = Field(farm_id=farm_id, **body.model_dump(), area_hectares=geojson_area_hectares(body.boundary))
    db.add(field); db.commit(); db.refresh(field); audit(db, user.id, "field.created", "field", str(field.id), {"farm_id": farm_id}); db.commit(); return field

def owned_field(field_id: int, db: Session, user: User) -> Field:
    field = db.get(Field, field_id)
    if not field: raise HTTPException(404, "Field not found")
    owned_farm(field.farm_id, db, user)
    return field

@router.get("/fields/{field_id}", response_model=FieldOut)
def get_field(field_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    return owned_field(field_id, db, user)

@router.patch("/fields/{field_id}", response_model=FieldOut)
def update_field(field_id: int, body: FieldInput, db: Session = Depends(get_db), user: User = Depends(current_user)):
    field = owned_field(field_id, db, user)
    for key, value in body.model_dump().items(): setattr(field, key, value)
    field.area_hectares = geojson_area_hectares(body.boundary); db.commit(); db.refresh(field); return field

@router.delete("/fields/{field_id}", status_code=204)
def delete_field(field_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    db.delete(owned_field(field_id, db, user)); db.commit(); return Response(status_code=204)

@router.get("/farms/{farm_id}/climate")
async def climate(farm_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    farm = owned_farm(farm_id, db, user); return await daily_weather(farm.latitude, farm.longitude)

@router.get("/farms/{farm_id}/observations")
async def observations(farm_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    farm = owned_farm(farm_id, db, user); return await daily_weather(farm.latitude, farm.longitude)

@router.get("/farms/{farm_id}/llm-context")
async def llm_context(farm_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Return source-labelled facts for an external LLM integration; does not invoke an LLM."""
    farm = owned_farm(farm_id, db, user)
    context = await farm_context(farm)
    audit(db, user.id, "farm.llm_context_exported", "farm", str(farm_id)); db.commit()
    return context

@router.post("/farms/{farm_id}/rotation-scenarios")
def rotation(farm_id: int, body: RotationRequest, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owned_farm(farm_id, db, user)
    try: return recommend(body)
    except ValueError as error: raise HTTPException(422, str(error))
