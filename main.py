# Orquestador - Main


import asyncio
import os
from procesador_snies import analizar_snies
from agente_analista import analizar_tendencias
from generador_reporte import crear_presentacion


async def main():
    print("--- INICIO DEL ANÁLISIS DE OPORTUNIDAD DE PROGRAMAS ---")
    
    # 1. Obtener entrada del usuario

    nombre_programa = input("Ingrese el nombre del programa a analizar: ")
    descripcion = input("Ingrese una breve descripción del programa: ")
    
    output_dir = f"Reporte_{nombre_programa.replace(' ', '_')}"

    if not os.path.exists(output_dir):

        os.makedirs(output_dir)

    try:
        # 2. Ejecutar el análisis SNIES (Módulo 1)

        datos_snies = analizar_snies(nombre_programa, output_dir)
        
        programas_snies_texto = datos_snies.get('texto_programas', 'No hay datos de SNIES.')
        
        # 3. Ejecutar el análisis de agentes (Módulo 2)

        datos_agente = await analizar_tendencias(nombre_programa, descripcion, programas_snies_texto)
        
        # 4. Generar el reporte (Módulo 3)
        
        output_file = os.path.join(output_dir, f"Reporte_{nombre_programa.replace(' ', '_')}.pptx")
        crear_presentacion(nombre_programa, datos_snies, datos_agente, output_file)

        print(f"--- ANÁLISIS COMPLETADO ---")
        print(f"El reporte se ha guardado en la carpeta: {output_dir}")

    except Exception as e:

        print(f"Ha ocurrido un error durante la ejecución: {str(e)}")

if __name__ == "__main__":

    asyncio.run(main())