# ⚡ Guía Rápida de 3 Minutos

## Para Usuarios Sin Experiencia

### 🐳 Método Docker (Más Fácil)

**Paso 1:** Instala Docker Desktop
- Windows/Mac: [Descarga Docker Desktop](https://www.docker.com/products/docker-desktop)
- Instala y abre Docker Desktop

**Paso 2:** Obtén tu API Key de Claude
1. Ve a https://console.anthropic.com
2. Regístrate o inicia sesión
3. Ve a "API Keys" → "Create Key"
4. Copia la clave (empieza con `sk-ant-api03-`)

**Paso 3:** Configura el proyecto
```bash
# Abre la terminal en la carpeta del proyecto
# Windows: Shift + Click derecho → "Abrir PowerShell aquí"
# Mac: Botón derecho → "Nuevo terminal en la carpeta"

# Crea el archivo de configuración
echo ANTHROPIC_API_KEY=pega_tu_clave_aqui > .env
```

**Paso 4:** Ejecuta el programa
```bash
# Inicia Docker
docker-compose up -d

# Ejecuta el extractor
docker exec -it rag_contratos python main.py
```

**Paso 5:** Selecciona una opción
```
Ingrese su opción: 1  ← Escribe 1 y presiona Enter
¿Desea continuar? (s/n): s  ← Escribe s y presiona Enter
```

✅ **¡Listo!** Los archivos `datos_contrato.json` y `datos_contrato.csv` se crean en la carpeta del proyecto.

---

## Para Usuarios con Python Instalado

### 🐍 Método Python Directo

```bash
# 1. Instala dependencias
pip install -r requirements.txt

# 2. Configura API Key
echo "ANTHROPIC_API_KEY=tu_clave_aqui" > .env

# 3. Ejecuta
python main.py
```

---

## 📝 Procesar Tu Propio Contrato

**Opción A - Editar Directamente:**
1. Abre `test/contrato_test2.py` en un editor de texto
2. Modifica la variable `fragmentos_contrato` con tu contrato:
```python
fragmentos_contrato = {
    "partes": """
    Copia aquí la sección de las partes de tu contrato
    """,
    "inmueble": """
    Copia aquí los datos del inmueble
    """,
    # ... etc
}
```
3. Guarda y ejecuta `python test/contrato_test2.py`

**Opción B - Crear Nuevo Script:**
```python
# mi_contrato.py
from test.contrato_test2 import extract_contract_data

# Copia el código de contrato_test2.py y modifica fragmentos_contrato
```

---

## 🆘 Problemas Comunes

### "No se encuentra Docker"
- Instala Docker Desktop y asegúrate de que esté corriendo

### "API Key inválida"
- Verifica que copiaste toda la clave (empieza con `sk-ant-api03-`)
- Revisa que el archivo `.env` existe: `cat .env` (Linux/Mac) o `type .env` (Windows)

### "No module named anthropic"
- Instala dependencias: `pip install -r requirements.txt`

---

## 📤 Exportar Resultados

Los archivos se crean automáticamente en la raíz del proyecto:

**Ver resultados:**
```bash
# Ver JSON formateado
cat datos_contrato.json

# Abrir CSV en Excel
start datos_contrato.csv  # Windows
open datos_contrato.csv   # Mac
xdg-open datos_contrato.csv  # Linux
```

---

## 🎯 Próximos Pasos

1. **Procesa contratos reales:** Edita `test/contrato_test2.py` con tus contratos
2. **Personaliza la extracción:** Modifica el prompt en línea 62-104 para extraer otros datos
3. **Usa ChromaDB:** Explora `chromadb/inserta_contrato.py` para almacenar múltiples contratos
4. **Automatiza:** Crea scripts para procesar múltiples archivos PDF/DOCX

---

## 💬 ¿Necesitas Ayuda?

- Lee el [README completo](README.md)
- Abre un Issue en GitHub
- Revisa los logs de error para diagnóstico
