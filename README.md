# kArmas_noob 👽 

# Scan a single target
python3 kArmas_noob.py --agree -u https://target.com

# Multiple targets with HTML report
python3 kArmas_noob.py --agree -l targets.txt -o report.html

# Filter by severity + threads
python3 kArmas_noob.py --agree -u https://target.com --severity critical,high -t 20

# Filter by tags
python3 kArmas_noob.py --agree -u https://target.com --tags cors,secrets -v

# List all templates
python3 kArmas_noob.py --list-templates
