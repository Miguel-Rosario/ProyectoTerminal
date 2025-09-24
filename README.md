# Proyecto Terminal: Identificación de Documentos y Detección de Modificaciones Autorizadas mediante Criptografía
Este proyecto busca desarrollar un sistema que no solo valide la autenticidad e integridad de los documentos digitales, sino
que tambien pueda diferenciar entre modificaciones leg´ıtimas realizadas por el creador original y alteraciones no autorizadas, utilizando metodos criptograficos avanzados como funciones hash y firmas digitales.

## Sistema de Firma Digital para Documentos XML/JSON

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3%2B-green)](https://flask.palletsprojects.com)
[![Cryptography](https://img.shields.io/badge/Cryptography-RSA--2048%2FSHA--256-red)](https://cryptography.io)

Sistema integral de firma digital que garantiza autenticidad, integridad y no repudio de documentos XML y JSON mediante técnicas criptográficas avanzadas. Detecta modificaciones no autorizadas mientras permite cambios legítimos mediante re-firmado controlado.

##  Características Principales

###  **Criptografía Robusta**
- **Algoritmos**: RSA-2048 con padding PSS + SHA-256
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

## 🏗️ Arquitectura del Sistema

