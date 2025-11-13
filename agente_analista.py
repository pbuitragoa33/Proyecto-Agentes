# Agente Analista - Patrón de diseño Planeador-Ejecutor


# - El Planner descompone una solicitud compleja en subtareas y las delega.
# - El Executor ejecuta cada subtarea, busca información en la web (usando WebSearchTool y 
# fetch_url) y devuelve resúmenes verificados con fuentes.
# - El Planner integra los resultados en un informe JSON con datos sobre programas,
#  universidades, costos y tendencias.


import asyncio
from agents import Agent, Runner, WebSearchTool, function_tool, AgentOutputSchema
from pydantic import BaseModel, Field
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json
import os # Asegúrate de que 'os' esté importado si no lo estaba

# Cargar variables de entorno (API Keys)

load_dotenv()

# Tools

@function_tool
def fetch_url(url: str, max_chars: int = 4000) -> str:
    """
    Descarga una página y retorna texto visible (recortado).
    """
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return text[:max_chars]
    except Exception as e:
        return f"Error al acceder a la URL: {str(e)}"

EXECUTOR_INSTRUCTIONS = """
Eres un EXECUTOR. Tu trabajo es resolver subtareas CONCRETAS que te delega un Planner.
Sigue este patrón simple de verificación:
- Si necesitas fuentes, usa primero la herramienta de búsqueda web para localizar URLs confiables.
- Luego, usa fetch_url para extraer el contenido clave y verificar.
- Devuelve SIEMPRE una respuesta breve, precisa y con 1–3 URLs como evidencia.
No inventes datos. Si hay incertidumbre, dilo explícitamente.
Formato de salida recomendado (texto):
- Hallazgos clave en 3–6 viñetas.
- Fuentes: lista de URLs.
"""

executor = Agent(
    name="Executor",
    instructions=EXECUTOR_INSTRUCTIONS,
    tools=[WebSearchTool(), fetch_url],
)

@function_tool
async def delegate_to_executor(subtask: str) -> str:
    """
    Ejecuta la subtarea con el EXECUTOR y devuelve su salida final.
    """
    print(f"--- EXECUTOR Inicia Tarea: {subtask} ---")
    res = await Runner.run(starting_agent=executor, input=subtask)
    print(f"--- EXECUTOR Finaliza Tarea ---")
    return res.final_output


class ProgramItem(BaseModel):
    program_name: Optional[str] = Field(None, description="Nombre del programa")
    university: Optional[str] = Field(None, description="Universidad")
    country: Optional[str] = Field(None, description="País")
    url: Optional[str] = Field(None, description="URL oficial o principal")
    courses_examples: List[str] = Field(default_factory=list, description="Curso(s) representativos si están disponibles")
    tuition: Optional[str] = Field(None, description="Costo (monto+moneda+periodicidad) si está disponible")
    intake_per_year: Optional[str] = Field(None, description="Ingreso/aforo anual si está disponible")
    sources: List[str] = Field(default_factory=list)

class FinalReport(BaseModel):
    input_program: str
    input_description: str
    coverage: dict
    items: List[ProgramItem]
    insights: List[str]

# --- PLANNER AGENT ---

PLANNER_INSTRUCTIONS = """
Eres un PLANNER. Tu objetivo es:
1) Descomponer la solicitud del usuario en subtareas claras para analizar un programa académico.
2) Delegar cada subtarea al EXECUTOR.
3) Integrar la información en un informe final JSON estructurado.

Reglas:
- Define subtareas para cubrir:
    1. Búsqueda de 2-3 programas similares en LATAM (fuera de Colombia).
    2. Búsqueda de 2-3 programas similares en EE.UU. o Europa.
    3. Para CADA programa encontrado (LATAM y USA/Europa), encontrar: URL, 2-3 cursos clave del plan de estudios, y costo de matrícula (si está disponible públicamente).
    4. Análisis de tendencias generales del nombre del programa (keywords, popularidad).
- Delega cada subtarea con 'delegate_to_executor'.
- Sintetiza TODOS los hallazgos en el JSON final.

Salida final:
Devuelve un JSON que cumpla EXACTAMENTE este esquema (usa FinalReport):
{
  "input_program": "...",
  "input_description": "...",
  "coverage": {"local": int, "national": int, "international": int}, 
  "items": [ ... (lista de ProgramItem) ... ],
  "insights": ["...", "..."]
}

Notas:
- 'coverage' se refiere a cuántos programas encontraste en cada región.
- 'insights' debe resumir las tendencias de palabras clave.
"""

planner = Agent(
    name="Planner",
    instructions=PLANNER_INSTRUCTIONS,
    tools=[delegate_to_executor],
    output_type=AgentOutputSchema(FinalReport, strict_json_schema=False)
)

async def analizar_tendencias(nombre_programa: str, descripcion: str, programas_snies: str) -> dict:
    """
    Ejecuta el agente Planner-Executor para buscar tendencias internacionales.
    """
    print(f"Iniciando análisis de agentes para: {nombre_programa}...")
    
    prompt = f"""
    Quiero mapear programas similares a: "{nombre_programa}".
    Descripción corta: "{descripcion}".
    
    Ya tengo una lista de programas locales (Colombia) gracias a SNIES, así que NO BUSQUES EN COLOMBIA.
    La lista local es: "{programas_snies}" (úsala solo como contexto).

    Tareas:
    - Encontrar 2-3 programas similares en LATAM (ej. México, Chile, Argentina, Brasil).
    - Encontrar 2-3 programas similares en EE.UU. y/o Europa (ej. España, Alemania).
    - Para cada programa internacional encontrado: nombre, universidad, país, sitio web, y 2-3 cursos representativos del plan de estudios.
    - Buscar el costo (tuition) de esos programas.
    - Analizar tendencias generales del nombre del programa (ej. "Data Science PhD trends", "Doctorado Ciencias Sociales demanda").

    Devuélveme el JSON final con el esquema 'FinalReport'.
    """

    result = await Runner.run(starting_agent=planner, input=prompt)

    print("Análisis de agentes completado.")
    
    if isinstance(result.final_output, FinalReport):
        
        return result.final_output.model_dump() 
    else:
        
        try:
            return json.loads(result.final_output)
        except json.JSONDecodeError:
            print("Error: La salida del agente no fue un JSON válido.")
            return {"error": "La salida del agente no fue un JSON válido", "raw_output": str(result.final_output)}