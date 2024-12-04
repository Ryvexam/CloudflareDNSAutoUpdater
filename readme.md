# 🌐 Dynamic IP DNS Updater for Cloudflare

## 🎯 Purpose

This service automatically updates your Cloudflare DNS records when your public IP address changes. Perfect for:
- 🏠 Home servers
- 🎮 Game servers
- 🖥️ Self-hosted applications
- 🌍 Personal websites running on dynamic IP connections

## 🔍 How It Works

1. 🕒 Every 5 minutes, the service:
   - Checks your current public IP using ipify.org
   - Compares it with the previous IP
   - Updates Cloudflare DNS records if a change is detected

2. 🔄 Automatic updates for:
   - Main domains
   - Subdomains
   - Multiple domain support
   - Proxied and non-proxied records

## 🚀 Quick Start

### 1️⃣ Prerequisites
- Docker and Docker Compose installed
- Cloudflare account with your domains
- Cloudflare API Token with DNS edit permissions

### 2️⃣ Setup

1. 📁 Clone or create the project structure:
```bash
mkdir ip-dns-updater
cd ip-dns-updater
mkdir config
```

2. 📝 Create configuration files:
```bash
# .env
CF_API_TOKEN=your_cloudflare_api_token_here

# config/config.json (example for ryvexam.fr and ryveweb.fr)
{
    "domains": [
        {
            "name": "ryvexam.fr",
            "records": [
                {
                    "name": "@",
                    "type": "A",
                    "proxied": true
                },
                {
                    "name": "emulator",
                    "type": "A",
                    "proxied": true
                },
                {
                    "name": "mc",
                    "type": "A",
                    "proxied": true
                }
            ]
        },
        {
            "name": "ryveweb.fr",
            "records": [
                {
                    "name": "@",
                    "type": "A",
                    "proxied": true
                }
            ]
        }
    ],
    "update_interval": 300
}
```

### 3️⃣ Launch

Start the service:
```bash
docker-compose up -d
```

## 🛠️ Management Commands

```bash
# View logs
docker-compose logs -f

# Stop the service
docker-compose down

# Restart the service
docker-compose restart

# Check container status
docker-compose ps
```

## 📋 Configuration Guide

### Cloudflare API Token 🔑
1. Go to Cloudflare Dashboard
2. Navigate to Profile > API Tokens
3. Create new token with:
   - Zone.DNS (Edit) permissions
   - Include all zones you want to manage

### Domain Configuration ⚙️
In `config.json`:
- `name`: Your domain name
- `records`: Array of DNS records to update
  - `name`: "@" for main domain, or subdomain name
  - `type`: "A" for IPv4 records
  - `proxied`: true/false for Cloudflare proxy

## 🚨 Troubleshooting

Common issues:
- 🔴 No updates happening:
  - Check API token permissions
  - Verify domain configuration
  - Check container logs

- 🔴 Container stops:
  - Check network connectivity
  - Verify API token validity
  - Review error logs

## ⚠️ Important Notes

- 🔒 Keep your API token secure
- ⏰ Default check interval is 5 minutes
- 🌐 Requires internet connectivity
- 📝 Changes to config require container restart

## 📮 Support

For issues or questions:
1. Check the container logs
2. Verify your configuration
3. Ensure Cloudflare API access

## 🔄 Updates

To update the container:
```bash
docker-compose down
docker-compose pull
docker-compose up -d
```
