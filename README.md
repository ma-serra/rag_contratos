# 📄 RAG - Sistema de Análisis de Documentos Jurídicos

Sistema inteligente de análisis de documentos jurídicos utilizando **Claude AI** y **ChromaDB**. Implementa técnicas de RAG (Retrieval Augmented Generation) para extracción estructurada de información.

## 🎯 Dos Sistemas Disponibles:

### 1. **Extracción de Contratos de Alquiler** (Original)
Extracción simple de datos de contratos de arrendamiento.
> 🚀 **¿Primera vez aquí?** Lee la [Guía Rápida de 3 Minutos](QUICKSTART.md)

### 2. **Diagnóstico Jurídico Condominial** (Nuevo) 🆕
Sistema RAG completo para análisis jurídico de condomínios.
> 🏢 **Sistema avanzado:** [Documentación Completa del Sistema de Diagnóstico](DIAGNOSTICO_README.md)

**Características del Sistema de Diagnóstico:**
- ✅ Análisis de múltiples tipos de documentos (convenções, normas, atas, contratos)
- ✅ Chunking inteligente con ChromaDB
- ✅ Diagnóstico jurídico en 5 fases
- ✅ Búsqueda semántica (RAG)
- ✅ Identificación automática de no conformidades
- ✅ Relatórios estructurados en JSON

## 🎯 ¿Qué hace este proyecto?

Extrae automáticamente información clave de contratos de alquiler como:
- Datos del arrendador y arrendatarios (nombres, DNI/CIF)
- Información del inmueble (dirección, superficie, referencia catastral)
- Condiciones económicas (renta mensual, gastos comunes, IBI)
- Duración del contrato y fianza

**Salidas generadas:**
- `datos_contrato.json` - Datos en formato JSON estructurado
- `datos_contrato.csv` - Tabla CSV para análisis en Excel/Google Sheets

---

## 🚀 Inicio Rápido

### Opción 1: Usando Docker (Recomendado)

**1. Configura tu API Key de Claude:**
```bash
# Crea el archivo .env en la raíz del proyecto
echo "ANTHROPIC_API_KEY=tu_api_key_de_claude_aqui" > .env
echo "CHROMADB_URI=chromadb" >> .env
```

**2. Inicia el contenedor:**
```bash
docker-compose up -d
```

**3. Ejecuta el programa:**
```bash
docker exec -it rag_contratos python main.py
```

**4. Selecciona un modelo de contrato:**
```
Seleccione el ejemplo que desea ejecutar:
1. Modelo de contrato 1
2. Modelo de contrato 2
0. Salir
Ingrese su opción: 1
```

### Opción 2: Ejecución Local

**1. Requisitos:**
- Python 3.11 o superior
- pip (gestor de paquetes de Python)

**2. Instalación:**
```bash
# Clona el repositorio
git clone <url-del-repo>
cd rag_contratos

# Crea y activa entorno virtual
python -m venv venv

# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate

# Instala dependencias
pip install -r requirements.txt
```

**3. Configuración:**
```bash
# Crea archivo .env con tu API key
echo "ANTHROPIC_API_KEY=tu_api_key_aqui" > .env
```

**4. Ejecuta:**
```bash
python main.py
```

---

## 📋 Cómo Obtener tu API Key de Claude

1. Ve a [console.anthropic.com](https://console.anthropic.com)
2. Crea una cuenta o inicia sesión
3. Navega a **API Keys** en el menú
4. Crea una nueva clave y cópiala
5. Pégala en tu archivo `.env`

---

## 💡 Ejemplos de Uso

### Ejecutar extracción de Modelo 1:
```bash
$ python main.py
Seleccione el ejemplo que desea ejecutar:
1. Modelo de contrato 1  ← Selecciona esta opción
2. Modelo de contrato 2
0. Salir
Ingrese su opción: 1
¿Desea continuar? (s/n): s

# Resultado: Se generan datos_contrato.json y datos_contrato.csv
```

### Ver los datos extraídos:
```bash
# Ver JSON
cat datos_contrato.json

# Ver CSV en formato tabla
column -s, -t < datos_contrato.csv
```

### Procesar tu propio contrato:
Edita los archivos en `test/contrato_test2.py` o `test/contrato_test3.py` y modifica la variable `fragmentos_contrato` con los datos de tu contrato.

---

## 📁 Estructura del Proyecto

```
rag_contratos/
├── main.py                    # Programa principal - menú interactivo
├── test/
│   ├── contrato_test2.py     # Modelo 1: Extracción con Claude API
│   ├── contrato_test3.py     # Modelo 2: Extracción alternativa
│   ├── inserta_contrato.py   # Inserción en ChromaDB
│   └── pruebas.py            # Tests adicionales
├── chromadb/                  # Base de datos vectorial
├── requirements.txt           # Dependencias Python
├── Dockerfile                 # Imagen Docker
├── docker-compose.yml         # Orquestación Docker
├── .env                       # Variables de entorno (CREAR ESTE!)
└── README.md                  # Este archivo
```

---

## 🔧 Configuración Avanzada

### Variables de Entorno (.env)

```bash
# Obligatoria - Tu API key de Claude
ANTHROPIC_API_KEY=sk-ant-api03-...

# Opcional - URI de ChromaDB (si usas BD externa)
CHROMADB_URI=http://localhost:8000
```

### Modelos Disponibles

El proyecto usa `claude-3-sonnet-20240229` por defecto. Puedes cambiarlo en los archivos de test editando:

```python
model="claude-3-sonnet-20240229"  # Cambiar a claude-3-opus, etc.
```

---

## 🛠️ Solución de Problemas

### Error: "ANTHROPIC_API_KEY not found"
**Solución:** Verifica que el archivo `.env` existe y contiene tu API key:
```bash
cat .env
# Debe mostrar: ANTHROPIC_API_KEY=sk-ant-api03-...
```

### Error: "ModuleNotFoundError: No module named 'anthropic'"
**Solución:** Instala las dependencias:
```bash
pip install -r requirements.txt
```

### Error: "Connection refused" (ChromaDB)
**Solución:** ChromaDB se usa localmente, no necesitas configurar URI. Elimina o comenta la variable `CHROMADB_URI` en tu `.env`.

---

## 📊 Ejemplo de Salida

**datos_contrato.json:**
```json
{
  "arrendador": {
    "nombre": "PROMONTORIA MACC XXX XXX, S.A",
    "cif": "A12345678"
  },
  "arrendatarios": [
    {
      "nombre": "Glenda Isabel Sumalave Zambrano",
      "dni": "Y1234567F"
    }
  ],
  "inmueble": {
    "direccion": "CL DE BADAJOZ, número 7, planta 1 y letra 1",
    "superficie": "66,00 m2",
    "ref_catastral": "9567001VK2696N0004DR"
  },
  "condiciones_economicas": {
    "renta_mensual": "990,00 €"
  }
}
```

---

## 🤝 Contribuciones

Este es un proyecto de prueba de concepto. Si deseas mejorarlo:
1. Fork el repositorio
2. Crea una rama con tu feature (`git checkout -b feature/mejora`)
3. Haz commit de tus cambios (`git commit -m 'Añadir mejora'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

---

## 📞 Soporte

¿Problemas o preguntas? Abre un **Issue** en GitHub con:
- Descripción del problema
- Pasos para reproducirlo
- Logs de error (si aplica)
- Tu sistema operativo y versión de Python

