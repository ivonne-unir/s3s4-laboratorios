# Proyecto reproducible: Dengue Perú (2000–2024)

Taller para el curso **Ciencia de Datos e IA Aplicada**. Datos originales: 1 029 421 registros, 14 columnas. Se distingue el caso docente (cáncer de mama) de los registros de dengue del grupo.

## Contenido
- `index.qmd`: informe y cuatro actividades, con R ejecutable.
- `scripts/limpiar_dengue.py`: lectura, auditoría y preparación de agregados.
- `data/`: tablas agregadas para publicar; **no** microdatos individuales.
- `.github/workflows/publicar.yml`: render automático con GitHub Actions y Pages.
- `documentos/`: taller y auditoría en Word.

## Reproducir el procesamiento local
1. Instalar Python 3 y `pip install pandas numpy`.
2. Poner `dengue_original.csv` en la raíz del proyecto **sin subirlo a GitHub**.
3. Ejecutar:
   ```bash
   python scripts/limpiar_dengue.py --entrada dengue_original.csv --salida data --guardar-individual
   ```
   Para regenerar solo agregados, omitir `--guardar-individual`.
4. Instalar R, Quarto y los paquetes `knitr`, `rmarkdown`.
5. Ejecutar `quarto render index.qmd --to html`.

## Publicar en GitHub Pages
1. Crear repositorio `taller-dengue-quarto` (inicialmente privado) y subir el **contenido** de este proyecto; respetar `.gitignore`.
2. En GitHub: **Settings > Pages > Build and deployment > Source: GitHub Actions**.
3. En **Actions**, ejecutar «Generar y publicar informe de dengue»; también se ejecuta al subir cambios a `main`.
4. El informe se publicará en `https://USUARIO.github.io/taller-dengue-quarto/`, si tu plan y la visibilidad del repositorio lo permiten.

## Consideraciones científicas
- Los números son conteos de registros notificados, no incidencia poblacional.
- Los 152 737 duplicados exactos se conservan porque no hay ID individual.
- Se marcaron 28 edades inválidas sin modificar `edad` original.
- La clasificación `diagnostic` coincide totalmente con `enfermedad`; **prohibido usarla como predictor**.
- Los agregados de modelado solo contienen celdas con n>=30 y mínimo 5 por cada clase; se excluyen 59 338 registros del resumen analítico publicado. Por tanto, la inferencia sobre todos los casos queda limitada.
- No subir `dengue_original.csv` ni archivos por localidad/persona al repositorio público.

## Referencia del caso docente
El CSV `data/comparacion_caso_clase.csv` contiene métricas provistas por el taller anterior, sin reentrenamiento de modelos de cáncer.
