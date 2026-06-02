#!/bin/bash
BACKUP_FILE='./backups/backup.sql'

echo "Restaurando $BACKUP_FILE..."
docker exec -i database mysql -u root -p"$DB_PASSWORD" < "$BACKUP_FILE"

echo "Limpando cache..."
docker exec backend bench --site localhost clear-cache

echo "✅ Restauração concluída!"