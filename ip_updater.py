# config/ip_updater.py
import os
import json
import time
import schedule
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Cloudflare API configuration
CF_API_TOKEN = os.getenv('CF_API_TOKEN')
CF_API_URL = 'https://api.cloudflare.com/client/v4'
HEADERS = {
    'Authorization': f'Bearer {CF_API_TOKEN}',
    'Content-Type': 'application/json'
}

previous_ip = None


def log_message(message):
    """Log message with timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")


def get_current_ip():
    """Get current public IP address."""
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except Exception as e:
        log_message(f"Error getting current IP: {e}")
        return None


def get_zone_id(domain):
    """Get Cloudflare zone ID for a domain."""
    try:
        response = requests.get(
            f'{CF_API_URL}/zones',
            headers=HEADERS,
            params={'name': domain}
        )
        zones = response.json()['result']
        return zones[0]['id'] if zones else None
    except Exception as e:
        log_message(f"Error getting zone ID for {domain}: {e}")
        return None


def get_dns_records(zone_id):
    """Get all DNS records for a zone."""
    try:
        response = requests.get(
            f'{CF_API_URL}/zones/{zone_id}/dns_records',
            headers=HEADERS
        )
        return response.json()['result']
    except Exception as e:
        log_message(f"Error getting DNS records: {e}")
        return []


def update_dns_record(zone_id, record_id, record_config, new_ip):
    """Update DNS record with new IP."""
    data = {
        'type': record_config['type'],
        'name': record_config['name'],
        'content': new_ip,
        'proxied': record_config.get('proxied', True)
    }

    try:
        response = requests.put(
            f'{CF_API_URL}/zones/{zone_id}/dns_records/{record_id}',
            headers=HEADERS,
            json=data
        )
        return response.json()['success']
    except Exception as e:
        log_message(f"Error updating DNS record {record_config['name']}: {e}")
        return False


def should_update_record(record, record_config):
    """Check if record matches configuration and should be updated."""
    record_name = record_config['name']
    if record_name.startswith('*.'):
        wildcard_prefix = record_name[2:]
        return (record['type'] == record_config['type'] and
                record['name'].endswith(wildcard_prefix))
    else:
        return (record['type'] == record_config['type'] and
                record['name'] == record_config['name'])


def check_and_update():
    """Main function to check IP and update DNS records."""
    global previous_ip

    log_message("Starting IP check...")
    current_ip = get_current_ip()

    if not current_ip:
        log_message("Could not get current IP. Will retry in next schedule.")
        return

    if current_ip != previous_ip:
        log_message(f"IP change detected: {previous_ip} -> {current_ip}")

        # Load configuration
        try:
            with open('config/config.json', 'r') as f:
                config = json.load(f)
        except Exception as e:
            log_message(f"Error loading config: {e}")
            return

        for domain_config in config['domains']:
            domain = domain_config['name']
            zone_id = get_zone_id(domain)

            if not zone_id:
                log_message(f"Could not find zone ID for {domain}")
                continue

            dns_records = get_dns_records(zone_id)

            for record_config in domain_config['records']:
                # Convert relative names to FQDN
                if record_config['name'] == '@':
                    record_config['name'] = domain
                elif not record_config['name'].endswith(domain):
                    if record_config['name'].startswith('*.'):
                        record_config['name'] = f"*.{record_config['name'][2:]}.{domain}"
                    else:
                        record_config['name'] = f"{record_config['name']}.{domain}"

                matching_records = [r for r in dns_records if should_update_record(r, record_config)]

                for record in matching_records:
                    if record['content'] != current_ip:
                        success = update_dns_record(zone_id, record['id'], record_config, current_ip)
                        if success:
                            log_message(f"Updated {record_config['name']} to {current_ip}")
                        else:
                            log_message(f"Failed to update {record_config['name']}")

        previous_ip = current_ip
    else:
        log_message("No IP change detected.")


def main():
    log_message("IP Updater Service Started")

    # Run immediately on startup
    check_and_update()

    # Schedule to run every 5 minutes
    schedule.every(5).minutes.do(check_and_update)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()