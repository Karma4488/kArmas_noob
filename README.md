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


# Scan with both internal templates and Nuclei
python3 kArmas_noob.py --agree -u https://example.com

# Skip Nuclei scans
python3 kArmas_noob.py --agree -u https://example.com --no-nuclei

# Filter Nuclei by tags/severity
python3 kArmas_noob.py --agree -u https://example.com --tags cve,rce --severity critical
