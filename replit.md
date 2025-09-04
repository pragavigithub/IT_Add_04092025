# Warehouse Management System (WMS)

## Overview
This is a comprehensive Flask-based Warehouse Management System that includes multiple modules for managing inventory transfers, GRPO (Goods Receipt PO), serial number tracking, and invoice creation. The application has been successfully adapted to run in the Replit environment with PostgreSQL database.

## Recent Changes (September 2025)
- ✅ Successfully migrated from MySQL to PostgreSQL for Replit compatibility
- ✅ Updated database configuration to prioritize PostgreSQL in Replit environment
- ✅ Fixed database constraint handling for PostgreSQL compatibility
- ✅ Configured proper Flask workflow for port 5000 with webview output
- ✅ Set up deployment configuration for production autoscaling

## Project Architecture

### Core Components
- **Flask Application**: Main web framework
- **Database**: PostgreSQL (Replit environment) with MySQL/SQLite fallback
- **Authentication**: Flask-Login with role-based permissions
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Session Management**: Secure session handling with SESSION_SECRET

### Modules
1. **Inventory Transfer**: Manage warehouse-to-warehouse transfers
2. **Serial Item Transfer**: Handle serial number tracked items
3. **GRPO (Goods Receipt PO)**: Process purchase order receipts
4. **Invoice Creation**: Generate and manage invoices
5. **QC Dashboard**: Quality control approvals
6. **User Management**: User accounts and permissions

### Database Schema
- Users with role-based permissions (admin, manager, user, qc)
- Branches for multi-location support
- Inventory transfers and items
- GRPO documents and items
- Pick lists and bin allocations
- Serial number tracking
- QR code label generation

## User Preferences
- Application supports multiple user roles with different permission levels
- Default admin credentials: username 'admin', password 'admin123'
- Multi-branch support with warehouse code management
- SAP B1 integration capabilities (configurable)

## Technical Configuration
- **Host**: 0.0.0.0 (configured for Replit proxy)
- **Port**: 5000 (frontend web interface)
- **Database**: PostgreSQL with automatic failover to MySQL/SQLite
- **Logging**: Comprehensive file-based logging system
- **Deployment**: Configured for autoscale deployment target

## Development Notes
- The application includes extensive logging for debugging
- Database migrations are handled automatically on startup
- All models are properly defined with relationships
- Blueprint-based modular architecture for maintainability
- Ready for production deployment with proper security measures

## Current Status
✅ **FULLY OPERATIONAL** - The application is running successfully on port 5000 with all modules loaded and database properly configured.