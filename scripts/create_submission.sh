#!/bin/bash

# Create submission files

echo "========================================="
echo "Creating Submission Files"
echo "========================================="
echo ""

cd "$(dirname "$0")/.."

# Export database
echo "1. Exporting database..."
bash scripts/export_database.sh
echo ""

# Create ZIP file
echo "2. Creating ZIP file..."
cd ..
zip -r securechat-assignment.zip securechat-skeleton/ \
  -x "*.git*" \
  -x "*.venv*" \
  -x "*.pyc" \
  -x "__pycache__/*" \
  -x "certs/*" \
  -x "transcripts/*" \
  -x "*.pem" \
  -x "*.key" \
  -x ".env" \
  -x "*.pcap" \
  -x "*.pcapng" \
  -x ".DS_Store" \
  -x "Thumbs.db" \
  -x "*.log" \
  > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "   ✓ ZIP file created: securechat-assignment.zip"
else
    echo "   ❌ Failed to create ZIP file"
    exit 1
fi

# Check file size
if [ -f securechat-assignment.zip ]; then
    SIZE=$(du -h securechat-assignment.zip | cut -f1)
    echo "   ✓ File size: $SIZE"
fi

echo ""
echo "========================================="
echo "Submission Files Created"
echo "========================================="
echo ""
echo "Files created:"
echo "  1. schema.sql - Database schema"
echo "  2. sample_records.sql - Sample user records"
echo "  3. securechat-assignment.zip - Repository ZIP"
echo ""
echo "Next steps:"
echo "  1. Fork GitHub repository"
echo "  2. Push code with 10+ commits"
echo "  3. Create reports (Report and Test Report)"
echo "  4. Submit on GCR"
echo ""

