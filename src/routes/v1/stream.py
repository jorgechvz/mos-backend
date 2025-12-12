"""Stream Video related routes."""

import os
import tempfile
import time
import requests
from fastapi import APIRouter, Depends, HTTPException, status
from getstream.models import UserRequest

from src.models import StreamUserRequest, StreamTokenResponse, MosRequest
from src.dependencies.stream_dep import get_stream_client
from src.application.mos import calculate_custom_mos
from src.config import settings

REFERENCE_DIR = "../../references"

router = APIRouter(tags=["stream"])


@router.post("/token", response_model=StreamTokenResponse)
def create_stream_user_token(
    payload: StreamUserRequest,
    client=Depends(get_stream_client),
):
    """
    Generates a Stream Video user token.
    Ensures the user exists, then creates a signed JWT.
    """

    try:
        user_req = UserRequest(
            id=payload.user_id,
            name=payload.name,
            role=payload.role,
            image=str(payload.image) if payload.image else None,
            custom={},
        )
        client.upsert_users(user_req)

        ttl = settings.stream_token_seconds * 24
        token = client.create_token(payload.user_id, expiration=ttl)
        obtained_at = int(time.time())

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating Stream user token",
        ) from exc

    return StreamTokenResponse(
        user_id=payload.user_id,
        token=token,
        expires_in=ttl,
        obtained_at=obtained_at,
    )


@router.post("/evaluate-call")
async def evaluate_call(request: MosRequest):
    """
    1. Busca la referencia localmente.
    2. Descarga la grabación de Stream.
    3. Calcula MOS.
    """

    # A. Validar que tenemos el archivo de referencia en el servidor
    ref_path = os.path.join(REFERENCE_DIR, request.reference_filename)
    if not os.path.exists(ref_path):
        raise HTTPException(
            status_code=404,
            detail=f"Archivo de referencia no encontrado en el servidor",  # noqa E501
        )
    tmp_deg_path = None

    try:
        # B. Descargar la GRABACIÓN desde Stream
        print(f"Descargando grabación de: {request.recording_url}")

        response = requests.get(request.recording_url, timeout=10)
        response.raise_for_status()
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".m4a"
        ) as tmp_deg:  # noqa E501
            tmp_deg.write(response.content)
            tmp_deg_path = tmp_deg.name

        # C. Ejecutar Algoritmo MOS
        # Asegúrate de que tu función calculate_custom_mos acepte rutas (paths)
        result = calculate_custom_mos(ref_path, tmp_deg_path)

        if not result:
            raise HTTPException(
                status_code=500, detail="Error en el cálculo del MOS"
            )  # noqa E501

        return result

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e

    finally:
        if tmp_deg_path and os.path.exists(tmp_deg_path):
            os.remove(tmp_deg_path)
