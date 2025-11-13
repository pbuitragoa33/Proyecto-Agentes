# Generador de reporte


from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN


def crear_presentacion(nombre_programa: str, datos_snies: dict, datos_agente: dict, output_file: str):
    """
    Crea una presentación de PowerPoint con los resultados del análisis.
    """
    print(f"Generando presentación: {output_file}...")

    prs = Presentation()


    # Diapositiva Título

    slide_layout = prs.slide_layouts[0] 
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "Análisis de Oportunidad"
    subtitle.text = nombre_programa

    # Diapositiva: Gráfica Costo vs Matriculados (SNIES) 

    slide_layout = prs.slide_layouts[5] 
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "Análisis SNIES: Costo vs. Matriculados (Colombia)"

    img_path = datos_snies['graficas'].get('costo_vs_matriculados')

    if img_path:

        slide.shapes.add_picture(img_path, Inches(1), Inches(1.5), width = Inches(8))

    # Diapositiva: Gráfica Programas por Departamento (SNIES)

    slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "Análisis SNIES: Programas por Depto. (Top 10)"

    img_path = datos_snies['graficas'].get('por_dpto')
    
    if img_path:

        slide.shapes.add_picture(img_path, Inches(1), Inches(1.5), width = Inches(8))

    # Diapositiva: Gráfica Evolución Estudiantes (SNIES) 

    slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "Análisis SNIES: Evolución de Estudiantes (Procesos)"

    img_path = datos_snies['graficas'].get('estudiantes_tiempo')

    if img_path:

        slide.shapes.add_picture(img_path, Inches(1), Inches(1.5), width = Inches(8))

    # Diapositiva: Información Internacional (Agente)

    slide_layout = prs.slide_layouts[1] 
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "Benchmark Internacional (LATAM)"

    textbox = slide.shapes.placeholders[1].text_frame
    textbox.clear() 

    items_latam = [item for item in datos_agente.get('items', []) if item.get('country') not in ['USA', 'España', 'Alemania', 'Colombia']]

    if not items_latam:

        p = textbox.paragraphs[0]
        p.text = "No se encontraron programas en LATAM."

    for item in items_latam:

        p = textbox.add_paragraph()
        p.text = f"{item.get('program_name', 'N/A')} - {item.get('university', 'N/A')} ({item.get('country', 'N/A')})"
        p.font.bold = True
        p.font.size = Pt(18)

        p_cursos = textbox.add_paragraph()
        cursos = ", ".join(item.get('courses_examples', []))
        p_cursos.text = f"  Cursos: {cursos if cursos else 'No disponibles'}"
        p_cursos.level = 1

        p_costo = textbox.add_paragraph()
        p_costo.text = f"  Costo: {item.get('tuition', 'No disponible')}"
        p_costo.level = 1


    # Diapositiva: Conclusiones y Tendencias (Agente) 
    
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "Análisis de Tendencias y Palabras Clave"

    textbox = slide.shapes.placeholders[1].text_frame
    textbox.clear()

    insights = datos_agente.get('insights', ["No se generaron insights."])
    
    for insight in insights:

        p = textbox.add_paragraph()
        p.text = f"• {insight}"
        p.font.size = Pt(16)

    # Guardar presentación

    prs.save(output_file)
    print(f"Presentación generada exitosamente en: {output_file}")