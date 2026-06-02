#!/bin/bash

SECRET_VALUE=$(aws secretsmanager get-secret-value \
    --secret-id "" \
    --region "sa-east-1" \
    --query SecretString \
    --output text)

if [ $? -ne 0 ]; then
    echo "Failed to retrieve secret"
    exit 1
fi

# Transform to KEY="VALUE" format
echo "$SECRET_VALUE" | jq -r 'to_entries | .[] | "\(.key)=\"\(.value)\""' >> "code/.env"

if [ $? -eq 0 ]; then
    echo ".env file created successfully: .env"
else
    echo "Failed to create .env file"
    exit 1
fi
