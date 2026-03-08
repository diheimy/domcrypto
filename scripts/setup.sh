#!/bin/bash
# Setup script for dom-crypto project

echo "Setting up dom-crypto project..."

# Install Node.js dependencies
npm install

# Create .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please fill in your environment variables."
fi

echo "Setup complete!"
