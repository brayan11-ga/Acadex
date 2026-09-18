# backend/app/services/ia_service.py
import os
import json
import pdfplumber
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.tarea import TareaPropuestaIA

load_dotenv()

# Asumiendo que tienes un modelo Categoria. Ajusta el import según tu estructura.
# from app.models.categoria import Categoria 

# Configuración inicial de Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extraer_texto_pdf(archivo: UploadFile) -> str:
    texto_extraido = ""
    try:
        # Abre el archivo directamente desde el buffer en memoria de FastAPI
        with pdfplumber.open(archivo.file) as pdf:
            for pagina in pdf.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_extraido += texto_pagina + "\n"
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo PDF está dañado o no se puede leer."
        )
    
    if not texto_extraido.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El PDF está vacío o es una imagen escaneada sin texto seleccionable."
        )
    return texto_extraido

def analizar_documento_con_ia(db: Session, archivo: UploadFile) -> TareaPropuestaIA:
    texto = extraer_texto_pdf(archivo)

    # Limitar el tamaño del texto para no exceder los tokens de Gemini (aprox 15,000 caracteres)
    texto = texto[:15000] 

    # Aquí deberías consultar las categorías de tu base de datos para enviarlas al prompt.
    # Ejemplo comentado si usas el modelo Categoria:
    # categorias = db.query(Categoria).all()
    # categorias_info = ", ".join([f"ID: {c.id_categoria} ({c.nombre_categoria})" for c in categorias])
    
    # Para este código base, dejaremos la instrucción genérica:
    categorias_info = "Selecciona un ID de categoría apropiado si conoces el contexto, de lo contrario devuelve null."

    prompt = f"""
    Eres un asistente para Acadex, un software de gestión académica. 
    Tu objetivo es analizar el siguiente documento académico y extraer la información necesaria para crear una tarea.
    
    Reglas estrictas:
    1. Debes responder ÚNICAMENTE con un objeto JSON válido.
    2. No incluyas markdown (como ```json). Solo las llaves y el contenido.
    3. 'titulo': Un título corto y claro (máximo 100 caracteres).
    4. 'descripcion': Un resumen detallado de lo que hay que hacer.
    5. 'dificultad_estimada': Un número entero del 1 al 5.
    6. 'tiempo_estimado': Un número entero en minutos mayor a 0.
    7. 'id_categoria': {categorias_info}
    
    Documento:
    {texto}
    """

    try:
        # Usamos gemini-1.5-flash por ser rápido y económico para procesamiento de texto
        modelo = genai.GenerativeModel("gemini-3.6-flash")
        respuesta = modelo.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json" # Fuerza a Gemini a devolver JSON puro
            )
        )
        
        datos_json = json.loads(respuesta.text)
        return TareaPropuestaIA(**datos_json)
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="La IA no devolvió un formato válido. Intenta nuevamente."
        )
    except Exception as e:
        print(f"❌ ERROR REAL DE GEMINI: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de IA no está disponible en este momento."
        )