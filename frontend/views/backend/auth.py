from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import create_client, Client
from sqlalchemy.orm import Session
import os
import models, database

# Configurações do Supabase extraídas do .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(database.get_db)
):
    token = credentials.credentials
    try:
        # Busca o usuário no Supabase
        user_res = supabase.auth.get_user(token)
        supabase_user = user_res.user
        
        # VALIDAÇÃO EXTRA: O e-mail foi confirmado?
        if not supabase_user.email_confirmed_at:
            raise HTTPException(
                status_code=403, 
                detail="E-mail ainda não confirmado. Verifique sua caixa de entrada (Etapa 1)."
            )
        
        # VALIDAÇÃO ETAPA 2: Aprovação manual na base local
        perfil = db.query(models.UsuarioPerfil).filter(
            models.UsuarioPerfil.supabase_uid == supabase_user.id
        ).first()

        if not perfil or not perfil.is_aprovado:
            raise HTTPException(
                status_code=403, 
                detail="Aguardando aprovação manual do administrador (Etapa 2)."
            )

        return perfil 
    except Exception as e:
        # Se o erro já for uma HTTPException (como as de cima), repassa ela
        if isinstance(e, HTTPException): raise e
        # Se for erro de token expirado ou inválido
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada.")