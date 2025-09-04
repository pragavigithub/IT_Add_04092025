# WMS (Warehouse Management System) Application

## Overview
This is a Flask-based Warehouse Management System with SAP B1 integration. The application provides inventory management, transfer operations, barcode generation, and invoice creation functionality.

## Project Architecture
- **Framework**: Flask (Python web framework)
- **Database**: PostgreSQL (Replit managed database)
- **Frontend**: HTML templates with Bootstrap styling
- **Integration**: SAP Business One API integration
- **Authentication**: Flask-Login for user management

## Current Configuration
- **Port**: 5000 (configured for Replit webview)
- **Database**: PostgreSQL with automatic table creation
- **Environment**: Production-ready with gunicorn server
- **Logging**: File-based logging system enabled

## Key Features
- User authentication and role management
- Inventory transfer operations
- Barcode and QR code generation
- SAP B1 integration for warehouse operations
- Serial number tracking
- Invoice creation module
- Pick list management
- GRPO (Goods Receipt PO) functionality

## Setup Status
✅ PostgreSQL database configured and connected
✅ Default admin user created (username: admin, password: admin123)
✅ Environment variables configured (DATABASE_URL, SESSION_SECRET)
✅ Gunicorn server running on port 5000
✅ Deployment configuration set for autoscale
✅ All database tables created with default data

## Default Credentials
- **Username**: admin
- **Password**: admin123
- **Role**: System Administrator

## Modules
- Main application routes
- Inventory transfer module
- Serial item transfer module
- Invoice creation module
- SAP B1 integration utilities
- Barcode generation utilities

## Recent Changes
- Configured for Replit environment (September 3, 2025)
- PostgreSQL database setup completed
- Default branch and admin user initialized
- Logging system configured for development