# Proyecto Terminal: Identificación de Documentos y Detección de Modificaciones Autorizadas mediante Criptografía

Este proyecto busca desarrollar un sistema que no solo valide la autenticidad e integridad de los documentos digitales, sino que también pueda diferenciar entre modificaciones legítimas realizadas por el creador original y alteraciones no autorizadas, utilizando métodos criptográficos avanzados como funciones hash y firmas digitales.

## Evolución del Proyecto

El sistema experimentó una evolución significativa desde su concepción inicial hasta la solución final, documentada en los siguientes programas:

### **Fase 1: Prototipo Básico (Consola)**
- **`importar_haslib.py`** - Fundamentos de cálculo de hashes SHA-256
- **`leer_xml.py`** - Procesamiento básico y análisis de archivos XML
- **`editar_xml.py`** - Manipulación genérica de documentos XML
- **`xml_hash.py`** - Sistema completo de hashes múltiples y verificación de integridad

### **Fase 2: Sistema de Firma Digital**
- **`prototipoIntegridad.py`** - Primera integración de criptografía asimétrica
- **`Edita_firma.py`** - Mecanismo de firma y re-firmado automático
- **`PT_SistemaFirmas.py`** - Sistema consolidado de firma digital para XML/JSON

### **Fase 3: Sistema Web Completo**
- **`PT_web/backend.py`** - API RESTful con Flask para operaciones criptográficas
- **`PT_web/client/`** - Interfaz web multi-usuario con gestión documental

##  Sistema de Firma Digital para Documentos XML/JSON

Sistema integral que garantiza autenticidad, integridad y no repudio de documentos XML y JSON mediante técnicas criptográficas avanzadas. Detecta modificaciones no autorizadas mientras permite cambios legítimos mediante re-firmado controlado.

### **Hitos de Validación**
- **280 Pruebas Exitosas**: 100% de efectividad en detección de alteraciones
- **Rendimiento Optimizado**: Tiempos de procesamiento inferiores a 2 segundos
- **Escalabilidad Comprobada**: Soporte para documentos hasta 10MB
- **Seguridad Robusta**: Cero falsos positivos/negativos en verificación

## Características Principales

### **Criptografía Robusta**
- **Algoritmos**: RSA-2048 con padding PSS + SHA-256
- **Firmas Digitales**: Verificación de autenticidad e integridad
- **Funciones Hash**: Cálculo de hashes múltiples (MD5, SHA-1, SHA-256, etc.)
- **Gestión de Claves**: Generación automática de pares de claves RSA

### **Gestión Documental Avanzada**
- **Formatos Soportados**: XML y JSON (implementado en `xml_hash.py` y `PT_SistemaFirmas.py`)
- **Control de Versiones**: Historial completo de modificaciones
- **Verificación en Tiempo Real**: Validación inmediata de integridad
- **Re-firmado Automático**: Para modificaciones autorizadas del propietario

### **Interfaz Web Multi-Usuario**
- **Autenticación Segura**: Registro y login con hash de contraseñas
- **API RESTful**: Endpoints para integración con otros sistemas
- **Interfaz Intuitiva**: Gestión documental mediante navegador web
- **Base de Datos**: Almacenamiento persistente en MySQL

