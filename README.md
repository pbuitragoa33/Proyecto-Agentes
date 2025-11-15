# Proyecto Orquestación de Agentes

## Integrantes:
- **Mariana Agudelo Areiza**
- **Pablo Buitrago Álvarez**



# **Resumen del Proyecto: Análisis de Oportunidad de Programas Académicos**

Este proyecto es un sistema automatizado para generar un Análisis de Oportunidad para un programa académico. Combina datos locales del sistema SNIES de Colombia con un análisis de benchmarking internacional realizado por agentes de IA.

El resultado final es un reporte consolidado y una presentación de PowerPoint (.pptx) con gráficas, tablas y análisis comparativos de programas similares a nivel nacional e internacional.


# **Arquitectura del Agente**

El núcleo del análisis se basa en una arquitectura de agentes Planner-Executor:

- **Planner (Planificador):** Es el "cerebro" de la operación. Recibe una solicitud principal como por ejemoplo analizar una carrera y la descompone en un plan de varias subtareas ("Buscar algunos programas en LATAM", "Buscar costos de esos programas", "Analizar tendencias del programa a buscar).

- **Executor (Ejecutor):** Es un agente más simple que recibe una a una esas subtareas concretas. Utiliza sus herramientas (WebSearchTool, fetch_url) para encontrar la información en la web, verificarla y devolver un resumen al Planner.

- **Integración:** El Planner recoge todas las respuestas del Executor y las consolida en el informe JSON final 


# **Flujo de Ejecución**

Este proyecto está compuesto por 4 módulos principales, donde `main.py` es el punto de entrada:

`main.py`: Es el punto de orquestador

* Pide al usuario el nombre del programa y una descripción de este.

* Llama a `procesador_snies.py` para el análisis local y es el encargado de reportar lo que hay en Colombia.

* Llama a `agente_analista.py` para el análisis internacional.

* Llama a `generador_reporte.py` para crear el PowerPoint con los resultados de los análisis encntrados


`procesador_snies.py`: Módulo de análisis de datos locales (Colombia).

* Descarga las tablas de SNIES (Maestro, Oferta, Programas, IES).

* Filtra programas similares al ingresado por el usuario usando un índice Jaccard.

* Genera y guarda algunas gráficas .png sobre la competencia local

`agente_analista.py`: El núcleo de IA (Planner-Executor).

* Define la configuración para conectarse a Azure OpenAI.

* Define las herramientas (fetch_url, WebSearchTool) que usará el Executor.

* Contiene los prompts detallads para el Planner y el Executor.

* Define los modelos de datos (ProgramItem, FinalReport) para estructurar la salida del LLM.

`generador_reporte.py`: Creador de la presentación.

* Usa la librería `python-pptx`.

* Toma los datos de los diccionarios `datos_snies` y `datos_agente`.

* Crea las diapositivas.

* Inserta las imágenes .png generadas por `procesador_snies.py`.

* Redacta un breve informe de lo encontradop.


# **Cómo Correr el Proyecto**

1. Crear un entorno virtual con venv (env)

2. Configurar las variables del entorno (Azure OpenAI Key, Azure Endpoint y Azure API Version) - Obviamente se debe de contar con un API Key valido.

3. Instalar los requerimientos (`pip install -r requirements.txt`)

4. Correr el orquestador (`python main.py`)

5. El `main.py` pide 2 cosas: 
* El nombre del programa que se quiere buscar.
* Una descripción breve de ese progrma a buscar.

6. A continuación,  se generará una carpeta con los resultados, incluyendo las imagenes del `procesador_snies.py` y la presentación como resultado final.


**Entrega #4: Técnicas Avanzadas en Inteligencia Artificial**
**2025**