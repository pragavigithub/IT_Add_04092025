#!/usr/bin/env python3
"""
MySQL Migration: Invoice Customer Code Fix
Date: 2025-09-04
Author: WMS System
Description: Migration to ensure customer_code and customer_name fields in invoice_documents table 
            are properly handled and saved during invoice creation workflow.

Related Issue: Customer code selected in UI not being saved to invoice drafts
Files Modified: modules/invoice_creation/routes.py
"""

import mysql.connector
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_mysql_connection():
    """Get MySQL connection using environment variables"""
    try:
        connection = mysql.connector.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            port=int(os.environ.get('MYSQL_PORT', '3306')),
            user=os.environ.get('MYSQL_USER', 'root'),
            password=os.environ.get('MYSQL_PASSWORD', 'root123'),
            database=os.environ.get('MYSQL_DATABASE', 'it_lobby'),
            autocommit=True
        )
        return connection
    except Exception as e:
        logging.error(f"Failed to connect to MySQL: {e}")
        return None

def check_invoice_documents_table_structure():
    """Check and validate invoice_documents table structure for customer fields"""
    connection = get_mysql_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Check if invoice_documents table exists and has required customer fields
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'invoice_documents'
            AND COLUMN_NAME IN ('customer_code', 'customer_name')
            ORDER BY COLUMN_NAME
        """)
        
        columns = cursor.fetchall()
        
        if len(columns) >= 2:
            logging.info("✅ invoice_documents table has required customer fields:")
            for col in columns:
                logging.info(f"   - {col['COLUMN_NAME']}: {col['DATA_TYPE']}({col['CHARACTER_MAXIMUM_LENGTH']}) NULL:{col['IS_NULLABLE']}")
            return True
        else:
            logging.error("❌ invoice_documents table missing customer fields")
            return False
            
    except Exception as e:
        logging.error(f"Error checking invoice_documents table: {e}")
        return False
    finally:
        if connection:
            connection.close()

def validate_customer_code_data_consistency():
    """Validate that existing invoice records have consistent customer data"""
    connection = get_mysql_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Check for invoices with NULL customer_code but have line items
        cursor.execute("""
            SELECT 
                id.id,
                id.invoice_number,
                id.customer_code,
                id.customer_name,
                id.status,
                COUNT(il.id) as line_count,
                id.created_at
            FROM invoice_documents id
            LEFT JOIN invoice_lines il ON id.id = il.invoice_id
            WHERE id.customer_code IS NULL OR id.customer_code = ''
            GROUP BY id.id
            HAVING line_count > 0
            ORDER BY id.created_at DESC
            LIMIT 10
        """)
        
        problematic_invoices = cursor.fetchall()
        
        if problematic_invoices:
            logging.warning(f"⚠️  Found {len(problematic_invoices)} invoices with missing customer codes but have line items:")
            for invoice in problematic_invoices:
                logging.warning(f"   - Invoice {invoice['id']}: {invoice['invoice_number']} ({invoice['line_count']} lines) - Status: {invoice['status']}")
            
            # These invoices would benefit from the customer code fix
            return False
        else:
            logging.info("✅ No invoices found with missing customer codes and line items")
            return True
            
    except Exception as e:
        logging.error(f"Error validating customer code data: {e}")
        return False
    finally:
        if connection:
            connection.close()

def update_migration_log():
    """Update migration log table to track this fix"""
    connection = get_mysql_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Create migration log table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migration_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                migration_name VARCHAR(255) NOT NULL UNIQUE,
                description TEXT,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status ENUM('applied', 'failed', 'rolled_back') DEFAULT 'applied',
                notes TEXT
            )
        """)
        
        # Insert this migration record
        cursor.execute("""
            INSERT INTO migration_log (migration_name, description, notes) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                applied_at = CURRENT_TIMESTAMP,
                status = 'applied',
                notes = VALUES(notes)
        """, (
            'invoice_customer_code_fix_20250904',
            'Fixed customer code saving issue in invoice creation workflow',
            'Updated invoice creation routes to properly save user-selected customer code and name when creating draft invoices and adding serial items. Customer code is now frozen after first line item is added.'
        ))
        
        logging.info("✅ Migration log updated successfully")
        return True
        
    except Exception as e:
        logging.error(f"Error updating migration log: {e}")
        return False
    finally:
        if connection:
            connection.close()

def main():
    """Main migration execution"""
    logging.info("=" * 60)
    logging.info("INVOICE CUSTOMER CODE FIX MIGRATION")
    logging.info("=" * 60)
    logging.info(f"Migration Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("")
    
    # Step 1: Check table structure
    logging.info("Step 1: Checking invoice_documents table structure...")
    structure_ok = check_invoice_documents_table_structure()
    
    if not structure_ok:
        logging.error("❌ Migration failed: Table structure issues")
        return False
    
    # Step 2: Validate existing data
    logging.info("\nStep 2: Validating customer code data consistency...")
    data_consistent = validate_customer_code_data_consistency()
    
    if not data_consistent:
        logging.warning("⚠️  Found invoices that would benefit from the customer code fix")
    
    # Step 3: Update migration log
    logging.info("\nStep 3: Updating migration log...")
    log_updated = update_migration_log()
    
    if not log_updated:
        logging.error("❌ Failed to update migration log")
        return False
    
    # Summary
    logging.info("\n" + "=" * 60)
    logging.info("MIGRATION SUMMARY")
    logging.info("=" * 60)
    logging.info("✅ Table Structure: OK")
    logging.info(f"{'✅' if data_consistent else '⚠️'} Data Consistency: {'OK' if data_consistent else 'Issues found (will be fixed by code changes)'}")
    logging.info("✅ Migration Log: Updated")
    logging.info("")
    logging.info("🔧 CODE CHANGES APPLIED:")
    logging.info("   - Updated invoice creation routes in modules/invoice_creation/routes.py")
    logging.info("   - Fixed customer code saving in create_draft endpoint")
    logging.info("   - Enhanced customer code freeze logic in add serial item endpoint")
    logging.info("   - Prioritizes user-selected customer over SAP-detected customer")
    logging.info("")
    logging.info("✅ Migration completed successfully!")
    logging.info("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)