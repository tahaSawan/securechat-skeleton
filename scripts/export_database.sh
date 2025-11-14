#!/bin/bash

# Export database schema and sample records

echo "Exporting database files..."

# Export schema (no data)
echo "1. Exporting schema..."
docker exec securechat-db mysqldump -u scuser -pscpass securechat --no-data --skip-triggers 2>/dev/null > schema.sql
if [ $? -eq 0 ]; then
    echo "   ✓ Schema exported to schema.sql"
else
    echo "   ❌ Failed to export schema"
    exit 1
fi

# Export sample records
echo "2. Exporting sample records..."
docker exec securechat-db mysqldump -u scuser -pscpass securechat users --skip-triggers 2>/dev/null > sample_records.sql
if [ $? -eq 0 ]; then
    echo "   ✓ Sample records exported to sample_records.sql"
else
    echo "   ❌ Failed to export sample records"
    exit 1
fi

# View users
echo "3. Viewing users..."
docker exec securechat-db mysql -u scuser -pscpass securechat -e "SELECT email, username, LENGTH(salt) as salt_length, LENGTH(pwd_hash) as hash_length FROM users;" 2>/dev/null

echo ""
echo "✅ Database export completed!"
echo "   - schema.sql: Database schema"
echo "   - sample_records.sql: Sample user records"

