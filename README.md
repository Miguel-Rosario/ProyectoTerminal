# Proyecto Terminal: Identificación de Documentos y Detección de Modificaciones Autorizadas mediante Criptografía
Este proyecto busca desarrollar un sistema que no solo valide la autenticidad e integridad de los documentos digitales, sino
que tambien pueda diferenciar entre modificaciones leg´ıtimas realizadas por el creador original y alteraciones no autorizadas, utilizando metodos criptograficos avanzados como funciones hash y firmas digitales.

## Sistema de Firma Digital para Documentos XML/JSON

Sistema de firma digital que garantiza autenticidad, integridad y no repudio de documentos XML y JSON mediante técnicas criptográficas avanzadas. Detecta modificaciones no autorizadas mientras permite cambios legítimos mediante re-firmado controlado.

El sistema experimentó una evolución significativa desde su concepción inicial hasta la solución final:

### **Fase 1: Prototipo Básico (Consola)**
- **Cálculo de Hashes**: Implementación inicial con `hashlib` para verificación de integridad

- 
- **Múltiples Algoritmos**: Soporte para MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512
- **Análisis de Documentos**: Lectura y procesamiento de archivos XML y JSON
- **Verificación de Checksum**: Comparación de hashes para detección de alteraciones

### **Fase 2: Sistema de Firma Digital**
- **Criptografía Asimétrica**: Integración de RSA-2048 con la biblioteca `cryptography`
- **Firmas Digitales**: Implementación de esquema PSS con SHA-256
- **Verificación de Autenticidad**: Mecanismo robusto para validación de firmas
- **Re-firmado Automático**: Capacidad para modificaciones legítimas del propietario

### **Fase 3: Sistema Web Completo**
- **Arquitectura Cliente-Servidor**: Migración a Flask con API RESTful
- **Base de Datos MySQL**: Almacenamiento persistente y gestión de usuarios
- **Control de Versiones**: Historial completo de modificaciones documentales
- **Interfaz Web Multi-Usuario**: Autenticación y gestión documental intuitiva
- **Verificación en Tiempo Real**: Validación inmediata mediante endpoints API

### **Hitos de Validación**
- **280 Pruebas Exitosas**: 100% de efectividad en detección de alteraciones
- **Rendimiento Optimizado**: Tiempos de procesamiento inferiores a 2 segundos
- **Escalabilidad Comprobada**: Soporte para documentos hasta 10MB
- **Seguridad Robusta**: Cero falsos positivos/negativos en verificación


##  Características Principales

###  **Criptografía Robusta**
- **Algoritmos**: RSA-2048 + SHA-256
- **Firmas Digitales**: Verificación de autenticidad e integridad
- **Funciones Hash**: Cálculo de hashes múltiples (MD5, SHA-1, SHA-256, etc.)
- **Gestión de Claves**: Generación automática de pares de claves RSA

###  **Gestión Documental Avanzada**
- **Formatos Soportados**: XML y JSON
- **Control de Versiones**: Historial completo de modificaciones
- **Verificación en Tiempo Real**: Validación inmediata de integridad
- **Re-firmado Automático**: Para modificaciones autorizadas del propietario

###  **Interfaz Web Multi-Usuario**
- **Autenticación Segura**: Registro y login con hash de contraseñas
- **API RESTful**: Endpoints para integración con otros sistemas
- **Interfaz Intuitiva**: Gestión documental mediante navegador web
- **Base de Datos**: Almacenamiento persistente en MySQL

##  Arquitectura del Sistema

