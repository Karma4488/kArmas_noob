#!/usr/bin/env python3
"""
╔═════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ██╗  ██╗ █████╗ ██████╗ ███╗   ███╗ █████╗ ███████╗              ║
║   ██║ ██╔╝██╔══██╗██╔══██╗████╗ ████║██╔══██╗██╔════╝              ║
║   █████╔╝ ███████║██████╔╝██╔████╔██║███████║███████╗              ║
║   ██╔═██╗ ██╔══██║���█╔══██╗██║╚██╔╝██║██╔══██║╚════██║              ║
║   ██║  ██╗██║  ██║██║  ██║██║ ╚═╝ ██║██║  ██║███████║              ║
║   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝              ║
║                                                                      ║
║          ███╗   ██╗ ██████╗  ██████╗ ██████╗                        ║
║          ████╗  ██║██╔═══██╗██╔═══██╗██╔══██╗                       ║
║          ██╔██╗ ██║██║   ██║██║   ██║██████╔╝                       ║
║          ██║╚██╗██║██║   ██║██║   ██║██╔══██╗                       ║
║          ██║ ╚████║╚██████╔╝╚██████╔╝██████╔╝                       ║
║          ╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═════╝                        ║
║                                                                      ║
║   ░░░   kArmas_noob — Template-Based Vulnerability Scanner   ░░░    ║
║         Passive Detection │ No Exploitation │ Auth Required          ║
║                  "We Are Legion. We Do Not Forgive."                 ║
╚═════════════════════════════════════════════════════════════════════╝

  AUTHORIZED USE ONLY — Passive/Detection mode.
  No active exploitation. Requires --agree flag.

  Author  : kArma
  Version : 1.0.0
  Engine  : Python 3.8+ (stdlib only)
"""

import sys
import os
import re
import ssl
import json
import time
import random
import socket
import hashlib
import argparse
import threading
import ipaddress
import traceback
import urllib.request
import urllib.error
import urllib.parse
import subprocess
import shutil
from datetime import datetime
from collections import defaultdict
from typing import Any

# ─────────────────────────────────────────────
#  ANSI PALETTE
# ─────────��───────────────────────────────────
G  = "\033[92m"   # green
R  = "\033[91m"   # red
Y  = "\033[93m"   # yellow
C  = "\033[96m"   # cyan
W  = "\033[97m"   # white
DG = "\033[32m"   # dark green
GR = "\033[90m"   # grey
B  = "\033[94m"   # blue
M  = "\033[95m"   # magenta
RS = "\033[0m"    # reset
BOLD = "\033[1m"

# ─────────────────────────────────────────────
#  SKULL
# ─────────────────────────────────────────────
SKULL = f"""{R}
         ░░░░░░░░░░░░░░░░░░░░░░░░░
        ░░  ░░░░░░░░░░░░░░░░░░  ░░
       ░░  ░░                ░░  ░░
      ░░  ░░  ██████  ██████  ░░  ░░
      ░░ ░░  ██ ████  ████ ██  ░░ ░░
      ░░ ░░  ████████████████  ░░ ░░
      ░░ ░░  ██████████████████░░ ░░
       ░░░░░  ████████████████ ░░░░
         ░░░   ██ ████████ ██  ░░
         ░░░    ████████████   ░░
          ░░░    ██      ██   ░░
           ░░░░░░░░░░░░░░░░░░░░
{RS}"""

# ─────────────────────────────────────────────
#  MATRIX RAIN INTRO
# ─────────────────────────────────────────────
MATRIX_CHARS = "ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏ01ABCDEF<>{}[]|/\\"

def matrix_rain(duration: float = 2.2):
    cols = min(os.get_terminal_size().columns, 100) if sys.stdout.isatty() else 80
    streams: dict[int, int] = {}
    end = time.time() + duration
    try:
        while time.time() < end:
            col = random.randint(0, cols - 1)
            streams[col] = streams.get(col, 0) + random.randint(1, 4)
            line = [" "] * cols
            for c, length in streams.items():
                if c < cols:
                    ch = random.choice(MATRIX_CHARS)
                    line[c] = f"{DG}{ch}{RS}" if length % 3 != 0 else f"{G}{BOLD}{ch}{RS}"
            sys.stdout.write("\r" + "".join(line))
            sys.stdout.flush()
            time.sleep(0.04)
        streams = {}
        sys.stdout.write("\r" + " " * cols + "\r")
    except Exception:
        pass

# ─────────────────────────────────────────────
#  NUCLEI INTEGRATION
# ─────────────────────────────────────────────
class NucleiRunner:
    """Runs Nuclei templates and parses results."""
    
    def __init__(self, timeout: int = 30, verbose: bool = False):
        self.timeout = timeout
        self.verbose = verbose
        self.nuclei_path = shutil.which("nuclei")
    
    def is_installed(self) -> bool:
        """Check if Nuclei is installed."""
        return self.nuclei_path is not None
    
    def get_version(self) -> str:
        """Get Nuclei version."""
        try:
            result = subprocess.run(
                [self.nuclei_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"
    
    def run_scan(self, target: str, tags: list[str] = None, 
                 severity: list[str] = None, templates: list[str] = None) -> list[dict]:
        """
        Run Nuclei scan against target.
        
        Args:
            target: URL to scan
            tags: Filter templates by tags (e.g., ["cve", "rce"])
            severity: Filter by severity (e.g., ["critical", "high"])
            templates: Specific template IDs to run
        
        Returns:
            List of finding dicts
        """
        if not self.is_installed():
            return []
        
        cmd = [self.nuclei_path, "-u", target, "-json", "-silent"]
        
        if tags:
            cmd.extend(["-tags", ",".join(tags)])
        
        if severity:
            cmd.extend(["-severity", ",".join(severity)])
        
        if templates:
            for tmpl in templates:
                cmd.extend(["-t", tmpl])
        
        cmd.extend(["-timeout", str(self.timeout)])
        cmd.append("-no-color")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout * 3
            )
            
            findings = []
            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        try:
                            findings.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
            
            return findings
        
        except subprocess.TimeoutExpired:
            if self.verbose:
                print(f"  {Y}[!]{RS} Nuclei scan timeout for {target}")
            return []
        except Exception as exc:
            if self.verbose:
                print(f"  {R}[ERR]{RS} Nuclei error: {exc}")
            return []
    
    def list_templates(self) -> list[dict]:
        """List available Nuclei templates."""
        try:
            result = subprocess.run(
                [self.nuclei_path, "-list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Parse template list from output
            templates = []
            for line in result.stdout.split("\n"):
                if line.strip() and ":" in line:
                    templates.append(line.strip())
            return templates
        except Exception:
            return []

# ─────────────────────────────────────────────
#  BUILT-IN TEMPLATE LIBRARY
# ─────────────────────────────────────────────
# Each template is a dict with:
#   id, name, severity, category, tags,
#   matchers: list of matcher dicts
#   extractors: list of extractor dicts
#   description

TEMPLATES: list[dict[str, Any]] = [

    # ── HEADERS ──────────────────────────────────────────────────
    {
        "id": "missing-x-frame-options",
        "name": "Missing X-Frame-Options",
        "severity": "medium",
        "category": "headers",
        "tags": ["clickjacking", "headers"],
        "description": "X-Frame-Options header is missing, enabling clickjacking attacks.",
        "matchers": [
            {"type": "header_absent", "key": "x-frame-options"}
        ],
        "extractors": []
    },
    {
        "id": "missing-csp",
        "name": "Missing Content-Security-Policy",
        "severity": "medium",
        "category": "headers",
        "tags": ["csp", "xss", "headers"],
        "description": "No Content-Security-Policy header detected. XSS risk elevated.",
        "matchers": [
            {"type": "header_absent", "key": "content-security-policy"}
        ],
        "extractors": []
    },
    {
        "id": "missing-hsts",
        "name": "Missing Strict-Transport-Security",
        "severity": "medium",
        "category": "headers",
        "tags": ["tls", "hsts", "headers"],
        "description": "HSTS header absent — HTTPS downgrade attacks possible.",
        "matchers": [
            {"type": "header_absent", "key": "strict-transport-security"}
        ],
        "extractors": []
    },
    {
        "id": "missing-x-content-type",
        "name": "Missing X-Content-Type-Options",
        "severity": "low",
        "category": "headers",
        "tags": ["mime", "headers"],
        "description": "X-Content-Type-Options: nosniff not set — MIME sniffing risk.",
        "matchers": [
            {"type": "header_absent", "key": "x-content-type-options"}
        ],
        "extractors": []
    },
    {
        "id": "server-version-disclosure",
        "name": "Server Version Disclosure",
        "severity": "low",
        "category": "information-disclosure",
        "tags": ["disclosure", "headers"],
        "description": "Server header reveals software version string.",
        "matchers": [
            {"type": "header_regex", "key": "server",
             "pattern": r"(Apache|nginx|IIS|lighttpd|Jetty|Tomcat)/[\d.]+"}
        ],
        "extractors": [
            {"type": "header_value", "key": "server", "label": "server-banner"}
        ]
    },
    {
        "id": "x-powered-by-disclosure",
        "name": "X-Powered-By Disclosure",
        "severity": "low",
        "category": "information-disclosure",
        "tags": ["disclosure", "headers"],
        "description": "X-Powered-By header leaks backend technology.",
        "matchers": [
            {"type": "header_present", "key": "x-powered-by"}
        ],
        "extractors": [
            {"type": "header_value", "key": "x-powered-by", "label": "powered-by"}
        ]
    },
    {
        "id": "cors-wildcard",
        "name": "CORS Wildcard Origin",
        "severity": "high",
        "category": "cors",
        "tags": ["cors", "misconfiguration"],
        "description": "Access-Control-Allow-Origin: * allows any origin to read responses.",
        "matchers": [
            {"type": "header_exact", "key": "access-control-allow-origin", "value": "*"}
        ],
        "extractors": []
    },
    {
        "id": "cors-allow-credentials-wildcard",
        "name": "CORS Credentials + Wildcard",
        "severity": "critical",
        "category": "cors",
        "tags": ["cors", "misconfiguration"],
        "description": "CORS allows wildcard AND credentials — credential theft risk.",
        "matchers": [
            {"type": "header_exact", "key": "access-control-allow-credentials", "value": "true"},
            {"type": "header_exact", "key": "access-control-allow-origin", "value": "*"}
        ],
        "match_condition": "all",
        "extractors": []
    },
    {
        "id": "referrer-policy-missing",
        "name": "Missing Referrer-Policy",
        "severity": "info",
        "category": "headers",
        "tags": ["privacy", "headers"],
        "description": "No Referrer-Policy header — full referrer URL may leak to third parties.",
        "matchers": [
            {"type": "header_absent", "key": "referrer-policy"}
        ],
        "extractors": []
    },
    {
        "id": "permissions-policy-missing",
        "name": "Missing Permissions-Policy",
        "severity": "info",
        "category": "headers",
        "tags": ["privacy", "headers"],
        "description": "No Permissions-Policy header controlling browser feature access.",
        "matchers": [
            {"type": "header_absent", "key": "permissions-policy"}
        ],
        "extractors": []
    },

    # ── COOKIES ──────────────────────────────────────────────────
    {
        "id": "cookie-no-httponly",
        "name": "Cookie Missing HttpOnly Flag",
        "severity": "medium",
        "category": "cookies",
        "tags": ["cookie", "xss"],
        "description": "Session cookie lacks HttpOnly — accessible via JavaScript.",
        "matchers": [
            {"type": "cookie_flag_absent", "flag": "httponly",
             "key_pattern": r"(session|sess|auth|token|sid|jwt)"}
        ],
        "extractors": []
    },
    {
        "id": "cookie-no-secure",
        "name": "Cookie Missing Secure Flag",
        "severity": "medium",
        "category": "cookies",
        "tags": ["cookie", "tls"],
        "description": "Cookie lacks Secure flag — transmitted over HTTP.",
        "matchers": [
            {"type": "cookie_flag_absent", "flag": "secure",
             "key_pattern": r"(session|sess|auth|token|sid|jwt)"}
        ],
        "extractors": []
    },
    {
        "id": "cookie-no-samesite",
        "name": "Cookie Missing SameSite",
        "severity": "low",
        "category": "cookies",
        "tags": ["cookie", "csrf"],
        "description": "Cookie missing SameSite attribute — CSRF risk.",
        "matchers": [
            {"type": "cookie_flag_absent", "flag": "samesite",
             "key_pattern": r"(session|sess|auth|token|sid)"}
        ],
        "extractors": []
    },

    # ── TLS ──────────────────────────────────────────────────────
    {
        "id": "tls-http-available",
        "name": "HTTP (Plaintext) Available",
        "severity": "medium",
        "category": "tls",
        "tags": ["tls", "plaintext"],
        "description": "Target responds over plaintext HTTP — no forced HTTPS redirect.",
        "matchers": [
            {"type": "scheme", "scheme": "http", "no_redirect_to_https": True}
        ],
        "extractors": []
    },

    # ── BODY / CONTENT ───────────────────────────────────────────
    {
        "id": "directory-listing",
        "name": "Directory Listing Enabled",
        "severity": "medium",
        "category": "misconfiguration",
        "tags": ["exposure", "files"],
        "description": "Web server exposes directory listing — file enumeration possible.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(Index of /|Directory listing for|Parent Directory</a>|<title>Index of)"}
        ],
        "extractors": []
    },
    {
        "id": "debug-info-page",
        "name": "Debug / Error Page Exposed",
        "severity": "medium",
        "category": "information-disclosure",
        "tags": ["debug", "disclosure"],
        "description": "Detailed stack trace or debug page is publicly accessible.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(Traceback \(most recent call last\)|at [a-zA-Z.]+\(.*\.java:\d+\)|Exception in thread|PHPFatal error|<b>Fatal error</b>|Whitelabel Error Page|DebugView|django\.core\.exceptions)"}
        ],
        "extractors": [
            {"type": "body_regex_extract", "pattern": r"(Exception|Error)[:\s]+([^\n<]{5,80})", "label": "error-msg"}
        ]
    },
    {
        "id": "exposed-git-repo",
        "name": "Exposed .git Directory",
        "severity": "high",
        "category": "exposure",
        "tags": ["git", "source-code"],
        "description": ".git directory accessible — full source code and secrets may be exposed.",
        "matchers": [
            {"type": "path_probe", "path": "/.git/HEAD",
             "body_regex": r"ref: refs/heads/", "status_codes": [200]}
        ],
        "extractors": [
            {"type": "body_regex_extract", "pattern": r"ref: refs/heads/(\S+)", "label": "branch"}
        ]
    },
    {
        "id": "exposed-env-file",
        "name": "Exposed .env File",
        "severity": "critical",
        "category": "exposure",
        "tags": ["secrets", "credentials"],
        "description": ".env file publicly accessible — secrets and credentials exposed.",
        "matchers": [
            {"type": "path_probe", "path": "/.env",
             "body_regex": r"(APP_KEY|DB_PASSWORD|SECRET|API_KEY|TOKEN|DATABASE_URL)",
             "status_codes": [200]}
        ],
        "extractors": [
            {"type": "body_regex_extract",
             "pattern": r"([A-Z_]{3,30})\s*=\s*([^\n]{1,60})", "label": "env-var"}
        ]
    },
    {
        "id": "exposed-aws-credentials",
        "name": "AWS Credentials in Response",
        "severity": "critical",
        "category": "secrets",
        "tags": ["aws", "secrets"],
        "description": "AWS access key found in HTTP response body.",
        "matchers": [
            {"type": "body_regex", "pattern": r"AKIA[0-9A-Z]{16}"}
        ],
        "extractors": [
            {"type": "body_regex_extract", "pattern": r"(AKIA[0-9A-Z]{16})", "label": "aws-key"}
        ]
    },
    {
        "id": "exposed-private-key",
        "name": "Private Key in Response",
        "severity": "critical",
        "category": "secrets",
        "tags": ["pki", "secrets"],
        "description": "PEM private key detected in HTTP response — credential compromise.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"}
        ],
        "extractors": []
    },
    {
        "id": "exposed-jwt-secret",
        "name": "JWT Token in Response",
        "severity": "medium",
        "category": "secrets",
        "tags": ["jwt", "auth"],
        "description": "JWT token pattern found in HTTP response body.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}"}
        ],
        "extractors": [
            {"type": "body_regex_extract",
             "pattern": r"(eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})",
             "label": "jwt-token"}
        ]
    },
    {
        "id": "exposed-backup-file",
        "name": "Backup File Exposed",
        "severity": "high",
        "category": "exposure",
        "tags": ["backup", "source-code"],
        "description": "Common backup file extension accessible — source or data exposure.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/backup.zip", "/backup.tar.gz", "/db.sql", "/dump.sql",
                       "/site.zip", "/www.zip", "/backup.sql", "/database.sql",
                       "/app.zip", "/files.tar.gz"],
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "exposed-phpinfo",
        "name": "phpinfo() Page Exposed",
        "severity": "medium",
        "category": "information-disclosure",
        "tags": ["php", "disclosure"],
        "description": "phpinfo() output publicly accessible — PHP config, env vars exposed.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/phpinfo.php", "/info.php", "/php_info.php", "/test.php", "/i.php"],
             "body_regex": r"PHP Version",
             "status_codes": [200]}
        ],
        "extractors": [
            {"type": "body_regex_extract",
             "pattern": r"PHP Version </td><td class=\"v\">([^<]+)", "label": "php-version"}
        ]
    },
    {
        "id": "laravel-debug-mode",
        "name": "Laravel Debug Mode Active",
        "severity": "high",
        "category": "misconfiguration",
        "tags": ["laravel", "php", "debug"],
        "description": "Laravel app running in debug mode — full exception data exposed.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(laravel|Illuminate\\|APP_DEBUG|whoops\.css|Facade\\Ignition)"}
        ],
        "extractors": []
    },
    {
        "id": "wordpress-user-enum",
        "name": "WordPress User Enumeration",
        "severity": "low",
        "category": "cms",
        "tags": ["wordpress", "enumeration"],
        "description": "WordPress ?author= parameter reveals usernames.",
        "matchers": [
            {"type": "path_probe", "path": "/?author=1",
             "body_regex": r"(author\/[a-zA-Z0-9_\-]+|\"author\":\s*\"[^\"]+\")",
             "status_codes": [200, 301, 302]}
        ],
        "extractors": [
            {"type": "body_regex_extract",
             "pattern": r"author\/([a-zA-Z0-9_\-]+)", "label": "wp-user"}
        ]
    },
    {
        "id": "wp-config-backup",
        "name": "WordPress Config Backup Exposed",
        "severity": "critical",
        "category": "cms",
        "tags": ["wordpress", "secrets"],
        "description": "WordPress config backup file accessible with DB credentials.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/wp-config.php.bak", "/wp-config.php~", "/wp-config.bak",
                       "/wp-config.old", "/wp-config.txt"],
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "adminer-exposed",
        "name": "Adminer Database Tool Exposed",
        "severity": "critical",
        "category": "exposure",
        "tags": ["database", "admin"],
        "description": "Adminer database management tool publicly accessible.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/adminer.php", "/adminer", "/db.php", "/database.php"],
             "body_regex": r"(adminer|Adminer)",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "phpmyadmin-exposed",
        "name": "phpMyAdmin Exposed",
        "severity": "high",
        "category": "exposure",
        "tags": ["database", "admin", "php"],
        "description": "phpMyAdmin interface publicly accessible.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/phpmyadmin/", "/pma/", "/phpMyAdmin/", "/mysql/"],
             "body_regex": r"(phpMyAdmin|phpmyadmin)",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "swagger-ui-exposed",
        "name": "Swagger UI / OpenAPI Exposed",
        "severity": "info",
        "category": "exposure",
        "tags": ["api", "documentation"],
        "description": "Swagger/OpenAPI documentation publicly accessible — API enumeration possible.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/swagger-ui.html", "/api/swagger-ui.html", "/swagger/",
                       "/api-docs", "/openapi.json", "/swagger.json", "/v2/api-docs",
                       "/api/v1/swagger.json"],
             "body_regex": r"(swagger|Swagger|OpenAPI|openapi)",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "spring-actuator-exposed",
        "name": "Spring Boot Actuator Exposed",
        "severity": "high",
        "category": "exposure",
        "tags": ["spring", "java", "actuator"],
        "description": "Spring Boot Actuator endpoints exposed — env/heap/beans data accessible.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/actuator", "/actuator/health", "/actuator/env",
                       "/actuator/mappings", "/actuator/beans"],
             "body_regex": r"(actuator|\"status\":\"UP\"|\"components\")",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "graphql-introspection",
        "name": "GraphQL Introspection Enabled",
        "severity": "medium",
        "category": "api",
        "tags": ["graphql", "api"],
        "description": "GraphQL introspection enabled — full schema enumerable by attackers.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/graphql", "/api/graphql", "/v1/graphql"],
             "body_regex": r"\"__schema\"",
             "method": "POST",
             "body": '{"query":"{__schema{types{name}}}"}',
             "content_type": "application/json",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "robots-sensitive-paths",
        "name": "Sensitive Paths in robots.txt",
        "severity": "info",
        "category": "information-disclosure",
        "tags": ["robots", "enumeration"],
        "description": "robots.txt reveals sensitive or private URL paths.",
        "matchers": [
            {"type": "path_probe", "path": "/robots.txt",
             "body_regex": r"Disallow:\s+/[a-zA-Z]",
             "status_codes": [200]}
        ],
        "extractors": [
            {"type": "body_regex_extract",
             "pattern": r"Disallow:\s+(/[^\n\r]{1,80})", "label": "disallowed-path"}
        ]
    },
    {
        "id": "exposed-ds-store",
        "name": "Exposed .DS_Store File",
        "severity": "medium",
        "category": "exposure",
        "tags": ["macos", "enumeration"],
        "description": ".DS_Store file exposed — directory structure of Mac developer revealed.",
        "matchers": [
            {"type": "path_probe", "path": "/.DS_Store",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "security-txt-missing",
        "name": "Missing security.txt",
        "severity": "info",
        "category": "policy",
        "tags": ["security-policy"],
        "description": "No security.txt found — no responsible disclosure policy defined.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/.well-known/security.txt", "/security.txt"],
             "status_codes_absent": [200]}
        ],
        "extractors": []
    },
    {
        "id": "exposed-composer-json",
        "name": "composer.json Exposed",
        "severity": "low",
        "category": "exposure",
        "tags": ["php", "dependencies"],
        "description": "composer.json publicly accessible — dependency list disclosed.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/composer.json", "/composer.lock"],
             "body_regex": r"\"require\"",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "exposed-package-json",
        "name": "package.json Exposed",
        "severity": "low",
        "category": "exposure",
        "tags": ["nodejs", "dependencies"],
        "description": "package.json publicly accessible — Node.js dependency info disclosed.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/package.json", "/package-lock.json"],
             "body_regex": r"\"dependencies\"",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "jenkins-exposed",
        "name": "Jenkins Dashboard Exposed",
        "severity": "critical",
        "category": "exposure",
        "tags": ["ci-cd", "admin"],
        "description": "Jenkins CI/CD dashboard publicly accessible — code execution risk.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/jenkins/", "/jenkins", "/"],
             "body_regex": r"(Jenkins|<title>Dashboard \[Jenkins\])",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "exposed-ssh-key",
        "name": "SSH Private Key in Web Root",
        "severity": "critical",
        "category": "secrets",
        "tags": ["ssh", "credentials"],
        "description": "SSH private key file accessible via HTTP.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/id_rsa", "/.ssh/id_rsa", "/id_ecdsa", "/.ssh/id_ecdsa",
                       "/id_ed25519", "/.ssh/id_ed25519"],
             "body_regex": r"-----BEGIN (OPENSSH|RSA|EC) PRIVATE KEY-----",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "http-trace-method",
        "name": "HTTP TRACE Method Enabled",
        "severity": "low",
        "category": "misconfiguration",
        "tags": ["xst", "http-method"],
        "description": "HTTP TRACE method enabled — Cross-Site Tracing (XST) possible.",
        "matchers": [
            {"type": "method_probe", "method": "TRACE",
             "response_header_contains": {"allow": "TRACE"}}
        ],
        "extractors": []
    },

    # ── SQL INJECTION & DATABASE ──────────────────────────────────
    {
        "id": "sql-error-messages",
        "name": "SQL Error Messages Exposed",
        "severity": "high",
        "category": "sql-injection",
        "tags": ["sqli", "database", "disclosure"],
        "description": "SQL error messages are exposed in the response — database type and query structure may be disclosed.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(SQL syntax.*?MySQL|supplied argument is not a valid MySQL|ORA-\d{5}|Microsoft OLE DB Provider for SQL Server|Unclosed quotation mark|quoted string not properly terminated|pg_query\(\)|PostgreSQL.*ERROR|SQLite3::query\(\)|SQLSTATE\[)"}
        ],
        "extractors": [
            {"type": "body_regex_extract",
             "pattern": r"(ORA-\d{5}|SQLSTATE\[[\w]+\]|SQL syntax[^<]{5,80})", "label": "sql-error"}
        ]
    },
    {
        "id": "sqli-parameter-patterns",
        "name": "SQLi Parameter Detection Patterns",
        "severity": "high",
        "category": "sql-injection",
        "tags": ["sqli", "database"],
        "description": "Response body contains patterns indicating SQL injection vulnerability in request parameters.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(You have an error in your SQL syntax|Warning: mysql_|mysql_fetch_array\(\)|Syntax error.*unexpected|Incorrect syntax near|Division by zero in SQL|error in your SQL)"}
        ],
        "extractors": []
    },
    {
        "id": "database-backup-accessible",
        "name": "Database Backup File Accessible",
        "severity": "critical",
        "category": "sql-injection",
        "tags": ["database", "backup", "exposure"],
        "description": "Database backup file is publicly accessible — full database dump may be downloadable.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/db_backup.sql", "/database_backup.sql", "/data.sql",
                       "/mysqldump.sql", "/backup.db", "/site.db", "/app.db",
                       "/db.sqlite", "/db.sqlite3", "/database.db"],
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "jdbc-connection-string-exposed",
        "name": "JDBC Connection String Exposed",
        "severity": "critical",
        "category": "sql-injection",
        "tags": ["database", "credentials", "disclosure"],
        "description": "JDBC connection string found in response — database credentials may be exposed.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"jdbc:(mysql|postgresql|oracle|sqlserver|db2|sqlite)://[^\s\"'<]{5,120}"}
        ],
        "extractors": [
            {"type": "body_regex_extract",
             "pattern": r"jdbc:[a-z:/@\w.\-]+", "label": "jdbc-url"}
        ]
    },
    {
        "id": "mongodb-injection-indicators",
        "name": "MongoDB Injection Indicators",
        "severity": "high",
        "category": "sql-injection",
        "tags": ["nosql", "mongodb", "database"],
        "description": "MongoDB NoSQL injection indicators detected in the response body.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(MongoError|MongoServerError|BSONTypeError|CastError|mongo_connect|Mongo\\.connect|MongooseError|MongoNetworkError|failed to connect to server \[.*\] on first connect)"}
        ],
        "extractors": []
    },

    # ── AUTHENTICATION & AUTHORIZATION ────────────────────────────
    {
        "id": "default-credentials-login",
        "name": "Default Credentials Accepted",
        "severity": "critical",
        "category": "authentication",
        "tags": ["auth", "default-credentials", "login"],
        "description": "Application login page detected — default credentials (admin/admin) may be accepted.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/admin/login", "/login", "/admin", "/wp-login.php",
                       "/user/login", "/signin", "/auth/login"],
             "body_regex": r"(password|passwd|login|username|sign.?in)",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "weak-password-policy",
        "name": "Weak Password Requirements Indicated",
        "severity": "medium",
        "category": "authentication",
        "tags": ["auth", "password-policy"],
        "description": "Password policy hints indicate weak requirements (min 4–6 chars, no complexity).",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(minimum.{0,20}(4|5|6)\s*characters|password.{0,30}at least (4|5|6)|minlength=[\"']?[456][\"']?)"}
        ],
        "extractors": []
    },
    {
        "id": "session-fixation-vulnerability",
        "name": "Session Fixation Vulnerability",
        "severity": "high",
        "category": "authentication",
        "tags": ["session", "auth", "fixation"],
        "description": "Session ID does not change after authentication — session fixation attack possible.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(PHPSESSID|JSESSIONID|ASP\.NET_SessionId|session_id)[^\w]"}
        ],
        "extractors": [
            {"type": "body_regex_extract",
             "pattern": r"(PHPSESSID|JSESSIONID|ASP\.NET_SessionId)=[a-zA-Z0-9]{8,}", "label": "session-id"}
        ]
    },
    {
        "id": "auth-bypass-patterns",
        "name": "Authentication Bypass Patterns",
        "severity": "critical",
        "category": "authentication",
        "tags": ["auth", "bypass"],
        "description": "Response body contains indicators of authentication bypass vulnerabilities.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(admin panel|administrator area|management console|control panel).{0,200}(no password|unauthenticated|bypass|open access)"}
        ],
        "extractors": []
    },
    {
        "id": "api-key-in-response",
        "name": "API Key Exposed in Response",
        "severity": "high",
        "category": "authentication",
        "tags": ["api", "secrets", "disclosure"],
        "description": "API key or secret found in HTTP response body.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(api[_\-]?key|apikey|api[_\-]?secret|client[_\-]?secret)\s*[=:\"']\s*[a-zA-Z0-9_\-]{16,64}"}
        ],
        "extractors": [
            {"type": "body_regex_extract",
             "pattern": r"(api[_\-]?key|apikey|api[_\-]?secret)[\"'\s]*[=:][\"'\s]*([a-zA-Z0-9_\-]{16,64})",
             "label": "api-key"}
        ]
    },
    {
        "id": "oauth-misconfiguration",
        "name": "OAuth/OpenID Misconfiguration",
        "severity": "high",
        "category": "authentication",
        "tags": ["oauth", "openid", "auth", "misconfiguration"],
        "description": "OAuth or OpenID Connect endpoint exposed with potential misconfiguration.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/.well-known/openid-configuration", "/oauth/authorize",
                       "/oauth2/token", "/connect/token", "/.well-known/oauth-authorization-server"],
             "body_regex": r"(issuer|authorization_endpoint|token_endpoint|client_id)",
             "status_codes": [200]}
        ],
        "extractors": [
            {"type": "body_regex_extract",
             "pattern": r"\"issuer\"\s*:\s*\"([^\"]+)\"", "label": "oauth-issuer"}
        ]
    },
    {
        "id": "saml-endpoint-exposed",
        "name": "SAML Endpoint Exposed",
        "severity": "medium",
        "category": "authentication",
        "tags": ["saml", "auth", "sso"],
        "description": "SAML SSO endpoint publicly accessible — SAML misconfigurations may be testable.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/saml/metadata", "/saml2/metadata", "/auth/saml",
                       "/sso/saml", "/saml/sso", "/Shibboleth.sso/Metadata"],
             "body_regex": r"(EntityDescriptor|SAMLMetadata|urn:oasis:names:tc:SAML)",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "2fa-bypass-indicators",
        "name": "2FA Bypass Indicators",
        "severity": "high",
        "category": "authentication",
        "tags": ["2fa", "mfa", "auth", "bypass"],
        "description": "Response suggests 2FA/MFA can be bypassed or is poorly implemented.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(backup.?code|recovery.?code|skip.{0,20}2fa|bypass.{0,20}two.?factor|remember.{0,30}this.{0,10}device.{0,50}forever)"}
        ],
        "extractors": []
    },

    # ── API SECURITY ─────────────────────────────────────────────
    {
        "id": "api-versioning-issues",
        "name": "Deprecated API Version Accessible",
        "severity": "medium",
        "category": "api",
        "tags": ["api", "versioning"],
        "description": "Old/deprecated API version endpoints are still accessible.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/api/v1/", "/api/v0/", "/api/v1", "/v1/api/", "/v0/"],
             "body_regex": r"(\{|\[)",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "unversioned-api-exposed",
        "name": "Unversioned API Exposed",
        "severity": "medium",
        "category": "api",
        "tags": ["api", "versioning", "exposure"],
        "description": "Unversioned API endpoints accessible — version control and deprecation enforcement absent.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/api/users", "/api/user", "/api/accounts", "/api/admin",
                       "/api/config", "/api/settings"],
             "body_regex": r"(\{|\[)",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "api-rate-limiting-disabled",
        "name": "API Rate Limiting Disabled",
        "severity": "medium",
        "category": "api",
        "tags": ["api", "rate-limiting"],
        "description": "No rate-limiting headers detected on API endpoint — brute-force and enumeration possible.",
        "matchers": [
            {"type": "header_absent", "key": "x-ratelimit-limit"},
            {"type": "header_absent", "key": "retry-after"}
        ],
        "match_condition": "all",
        "extractors": []
    },
    {
        "id": "api-documentation-leak",
        "name": "API Documentation Publicly Accessible",
        "severity": "info",
        "category": "api",
        "tags": ["api", "documentation", "exposure"],
        "description": "API documentation endpoint accessible without authentication.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/api/docs", "/api/documentation", "/docs/api",
                       "/redoc", "/api/redoc", "/api-docs/", "/api/schema"],
             "body_regex": r"(openapi|swagger|api.?documentation|endpoint|schema)",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "soap-xml-endpoint-exposed",
        "name": "SOAP/XML Web Service Exposed",
        "severity": "medium",
        "category": "api",
        "tags": ["soap", "xml", "api", "wsdl"],
        "description": "SOAP/XML web service endpoint publicly accessible — WSDL may expose internal service details.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/ws", "/service", "/services", "/soap", "/wsdl",
                       "/api/soap", "/RPC2"],
             "body_regex": r"(wsdl|WSDL|soap:Envelope|<definitions |xmlns:soap=|<wsdl:)",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "rest-api-method-exposure",
        "name": "REST API Dangerous Methods Exposed",
        "severity": "medium",
        "category": "api",
        "tags": ["api", "rest", "http-method"],
        "description": "REST API exposes PUT/DELETE/PATCH methods that allow data modification.",
        "matchers": [
            {"type": "header_regex", "key": "allow",
             "pattern": r"(PUT|DELETE|PATCH)"}
        ],
        "extractors": [
            {"type": "header_value", "key": "allow", "label": "allowed-methods"}
        ]
    },
    {
        "id": "grpc-endpoint-accessible",
        "name": "gRPC Endpoint Accessible",
        "severity": "medium",
        "category": "api",
        "tags": ["grpc", "api", "exposure"],
        "description": "gRPC endpoint accessible — service reflection may expose internal APIs.",
        "matchers": [
            {"type": "header_regex", "key": "content-type",
             "pattern": r"application/grpc"},
            {"type": "path_probe_list",
             "paths": ["/grpc.health.v1.Health/Check", "/grpc.reflection.v1alpha.ServerReflection/ServerReflectionInfo"],
             "status_codes": [200, 415]}
        ],
        "extractors": []
    },

    # ── SERVER & FRAMEWORK ────────────────────────────────────────
    {
        "id": "apache-struts-exposed",
        "name": "Apache Struts Vulnerability Indicators",
        "severity": "critical",
        "category": "server",
        "tags": ["struts", "java", "rce"],
        "description": "Apache Struts application detected — known RCE vulnerabilities (S2-045, S2-061) may apply.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(Apache Struts|struts2|org\.apache\.struts|Struts Problem Report)"}
        ],
        "extractors": []
    },
    {
        "id": "jboss-wildfly-exposed",
        "name": "JBoss/WildFly Management Console Exposed",
        "severity": "critical",
        "category": "server",
        "tags": ["jboss", "wildfly", "java", "admin"],
        "description": "JBoss or WildFly management console publicly accessible.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/jmx-console/", "/web-console/", "/management",
                       "/console/", "/admin-console/"],
             "body_regex": r"(JBoss|WildFly|JMX Console|Management Console|jboss\.management)",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "tomcat-manager-exposed",
        "name": "Tomcat Manager Exposed",
        "severity": "critical",
        "category": "server",
        "tags": ["tomcat", "java", "admin"],
        "description": "Apache Tomcat Manager application publicly accessible — WAR deployment possible.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/manager/html", "/manager/text", "/host-manager/html",
                       "/tomcat/manager/html"],
             "body_regex": r"(Tomcat Web Application Manager|Apache Tomcat|Manager App)",
             "status_codes": [200, 401]}
        ],
        "extractors": []
    },
    {
        "id": "jetty-admin-panel",
        "name": "Jetty Admin Panel Exposed",
        "severity": "high",
        "category": "server",
        "tags": ["jetty", "java", "admin"],
        "description": "Jetty web server admin interface is publicly accessible.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(Jetty|jetty\.version|Eclipse Jetty)"}
        ],
        "extractors": [
            {"type": "body_regex_extract",
             "pattern": r"Jetty/?([\d.]+)", "label": "jetty-version"}
        ]
    },
    {
        "id": "werkzeug-debugger-active",
        "name": "Werkzeug Interactive Debugger Active",
        "severity": "critical",
        "category": "server",
        "tags": ["werkzeug", "python", "flask", "debug", "rce"],
        "description": "Werkzeug interactive debugger is active — remote code execution via console possible.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(Werkzeug Debugger|The interactive debugger|werkzeug\.debug|Traceback \(most recent call last\).{0,500}werkzeug)"}
        ],
        "extractors": []
    },
    {
        "id": "aspnet-config-exposed",
        "name": "ASP.NET Configuration Exposed",
        "severity": "critical",
        "category": "server",
        "tags": ["aspnet", "dotnet", "config", "disclosure"],
        "description": "ASP.NET configuration file accessible — connection strings and secrets may be exposed.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/web.config", "/Web.config", "/app.config",
                       "/applicationHost.config"],
             "body_regex": r"(connectionString|appSettings|system\.web|machineKey|validationKey)",
             "status_codes": [200]}
        ],
        "extractors": [
            {"type": "body_regex_extract",
             "pattern": r"connectionString\s*=\s*\"([^\"]{5,120})\"", "label": "connection-string"}
        ]
    },
    {
        "id": "iis-default-page",
        "name": "IIS Default Page Exposed",
        "severity": "info",
        "category": "server",
        "tags": ["iis", "windows", "default-page"],
        "description": "IIS default welcome page is accessible — server not fully configured.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(IIS Windows Server|Internet Information Services|iis-85|Welcome to IIS)"}
        ],
        "extractors": []
    },
    {
        "id": "axis2-admin-console",
        "name": "Apache Axis2 Admin Console Exposed",
        "severity": "critical",
        "category": "server",
        "tags": ["axis2", "java", "admin", "webservice"],
        "description": "Apache Axis2 administration console accessible — malicious service deployment possible.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/axis2/", "/axis2-admin/", "/axis2/axis2-admin/",
                       "/services/", "/axis2/services/"],
             "body_regex": r"(Axis2|Apache Axis2|axis2\.war|Available Services)",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "coldfusion-admin-exposed",
        "name": "ColdFusion Administrator Exposed",
        "severity": "critical",
        "category": "server",
        "tags": ["coldfusion", "adobe", "admin"],
        "description": "Adobe ColdFusion administrator interface publicly accessible.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/CFIDE/administrator/", "/cfide/administrator/",
                       "/CFIDE/adminapi/", "/cfide/adminapi/"],
             "body_regex": r"(ColdFusion Administrator|CFIDE|Adobe ColdFusion)",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "nexus-repository-exposed",
        "name": "Nexus Repository Manager Exposed",
        "severity": "high",
        "category": "server",
        "tags": ["nexus", "repository", "admin"],
        "description": "Sonatype Nexus Repository Manager is publicly accessible.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/nexus/", "/#browse/browse", "/service/rest/v1/status",
                       "/nexus/service/local/status"],
             "body_regex": r"(Nexus Repository|Sonatype Nexus|nexus\.version|\"edition\")",
             "status_codes": [200]}
        ],
        "extractors": []
    },

    # ── CLOUD & INFRASTRUCTURE ────────────────────────────────────
    {
        "id": "aws-s3-bucket-exposure",
        "name": "AWS S3 Bucket Exposure",
        "severity": "high",
        "category": "cloud",
        "tags": ["aws", "s3", "cloud", "exposure"],
        "description": "AWS S3 bucket reference found — bucket may be publicly accessible.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(s3\.amazonaws\.com|s3://[a-z0-9][a-z0-9\-]{1,61}[a-z0-9]|\.s3\.amazonaws\.com|\.s3-[a-z0-9\-]+\.amazonaws\.com)"}
        ],
        "extractors": [
            {"type": "body_regex_extract",
             "pattern": r"([a-z0-9][a-z0-9\-]{1,61}[a-z0-9])\.s3[^\"'\s]{0,40}", "label": "s3-bucket"}
        ]
    },
    {
        "id": "gcp-metadata-accessible",
        "name": "GCP Metadata Service Accessible",
        "severity": "critical",
        "category": "cloud",
        "tags": ["gcp", "cloud", "ssrf", "metadata"],
        "description": "GCP metadata service response patterns detected — SSRF or misconfigured service possible.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(metadata\.google\.internal|computeMetadata|instance/service-accounts|gcp-metadata)"}
        ],
        "extractors": []
    },
    {
        "id": "azure-blob-storage-exposed",
        "name": "Azure Blob Storage Exposed",
        "severity": "high",
        "category": "cloud",
        "tags": ["azure", "cloud", "storage", "exposure"],
        "description": "Azure Blob Storage URL detected — container or blob may be publicly accessible.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(blob\.core\.windows\.net|\.blob\.core\.windows\.net/[a-zA-Z0-9\-]+)"}
        ],
        "extractors": [
            {"type": "body_regex_extract",
             "pattern": r"([a-z0-9]+\.blob\.core\.windows\.net/[a-zA-Z0-9\-]+)", "label": "azure-blob-url"}
        ]
    },
    {
        "id": "docker-registry-exposed",
        "name": "Docker Registry Exposed",
        "severity": "high",
        "category": "cloud",
        "tags": ["docker", "registry", "container", "exposure"],
        "description": "Docker private registry accessible without authentication.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/v2/", "/v2/_catalog"],
             "body_regex": r"(repositories|\"name\")",
             "status_codes": [200]}
        ],
        "extractors": [
            {"type": "body_regex_extract",
             "pattern": r"\"repositories\":\[([^\]]{1,200})\]", "label": "docker-repos"}
        ]
    },
    {
        "id": "kubernetes-dashboard-exposed",
        "name": "Kubernetes Dashboard Exposed",
        "severity": "critical",
        "category": "cloud",
        "tags": ["kubernetes", "k8s", "dashboard", "admin"],
        "description": "Kubernetes dashboard is publicly accessible — cluster management without auth possible.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/",
                       "/#/overview", "/api/v1/"],
             "body_regex": r"(kubernetes-dashboard|Kubernetes Dashboard|k8s\.io|\"apiVersion\")",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "terraform-state-file-exposed",
        "name": "Terraform State File Exposed",
        "severity": "critical",
        "category": "cloud",
        "tags": ["terraform", "infrastructure", "secrets", "exposure"],
        "description": "Terraform state file accessible — full infrastructure config and secrets exposed.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/terraform.tfstate", "/.terraform/terraform.tfstate",
                       "/infra/terraform.tfstate", "/infrastructure/terraform.tfstate"],
             "body_regex": r"(\"terraform_version\"|\"resources\"|\"outputs\")",
             "status_codes": [200]}
        ],
        "extractors": [
            {"type": "body_regex_extract",
             "pattern": r"\"terraform_version\":\s*\"([^\"]+)\"", "label": "tf-version"}
        ]
    },
    {
        "id": "cloudformation-stack-exposed",
        "name": "CloudFormation Stack Info Exposed",
        "severity": "high",
        "category": "cloud",
        "tags": ["aws", "cloudformation", "infrastructure", "exposure"],
        "description": "CloudFormation template or stack information publicly accessible.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/cloudformation.json", "/cloudformation.yaml",
                       "/stack.json", "/infrastructure.json", "/cfn-template.json"],
             "body_regex": r"(AWSTemplateFormatVersion|CloudFormation|\"Resources\"|\"Parameters\")",
             "status_codes": [200]}
        ],
        "extractors": []
    },

    # ── FILE UPLOAD & PATH TRAVERSAL ──────────────────────────────
    {
        "id": "unrestricted-file-upload",
        "name": "Unrestricted File Upload Endpoint",
        "severity": "critical",
        "category": "file-upload",
        "tags": ["upload", "rce", "file-upload"],
        "description": "File upload endpoint detected that may accept unrestricted file types.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(<input[^>]+type=[\"']file[\"']|enctype=[\"']multipart/form-data[\"']|upload.{0,30}file|file.{0,30}upload)"}
        ],
        "extractors": []
    },
    {
        "id": "path-traversal-indicators",
        "name": "Path Traversal Vulnerability Indicators",
        "severity": "high",
        "category": "file-upload",
        "tags": ["path-traversal", "lfi", "rfi"],
        "description": "Response contains path traversal indicators — directory traversal attack may be possible.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(\.\./|\.\.\\|%2e%2e%2f|%252e%252e|/etc/passwd|/etc/shadow|/windows/win.ini|root:x:0:0:)"}
        ],
        "extractors": [
            {"type": "body_regex_extract",
             "pattern": r"(root:[^:]+:[^:]+:[^:]+:[^:\n]+)", "label": "passwd-entry"}
        ]
    },
    {
        "id": "arbitrary-file-download",
        "name": "Arbitrary File Download Endpoint",
        "severity": "high",
        "category": "file-upload",
        "tags": ["lfi", "download", "path-traversal"],
        "description": "File download endpoint with user-controlled filename detected — path traversal risk.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(download\.php\?file=|download\.php\?path=|file\.php\?name=|getfile\.php|filedownload\.php|download\?filename=|attachment\.php\?id=)"}
        ],
        "extractors": []
    },
    {
        "id": "upload-directory-listing",
        "name": "Upload Directory Listing Accessible",
        "severity": "high",
        "category": "file-upload",
        "tags": ["upload", "directory-listing", "exposure"],
        "description": "Upload directory has listing enabled — all uploaded files are enumerable.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/uploads/", "/upload/", "/files/", "/attachments/",
                       "/media/uploads/", "/assets/uploads/"],
             "body_regex": r"(Index of /|Directory listing|Parent Directory)",
             "status_codes": [200]}
        ],
        "extractors": []
    },
    {
        "id": "temp-file-exposure",
        "name": "Temporary File Exposed",
        "severity": "medium",
        "category": "file-upload",
        "tags": ["exposure", "temp-files"],
        "description": "Temporary or swap files accessible in web root — source code or data exposed.",
        "matchers": [
            {"type": "path_probe_list",
             "paths": ["/index.php~", "/index.php.bak", "/config.php~",
                       "/config.php.bak", "/.htaccess.bak", "/index.html.bak",
                       "/config.bak", "/settings.py.bak"],
             "status_codes": [200]}
        ],
        "extractors": []
    },

    # ── SERIALIZATION & DESERIALIZATION ───────────────────────────
    {
        "id": "java-serialization-gadgets",
        "name": "Java Serialization Gadget Indicators",
        "severity": "critical",
        "category": "deserialization",
        "tags": ["java", "deserialization", "rce"],
        "description": "Java serialized object magic bytes or deserialization error detected — RCE risk.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(java\.io\.ObjectInputStream|java\.lang\.ClassNotFoundException|org\.apache\.commons\.collections|java\.rmi\.|ysoserial|InvalidClassException|SerialVersionUID)"}
        ],
        "extractors": []
    },
    {
        "id": "python-pickle-deserialization",
        "name": "Python Pickle Deserialization Indicators",
        "severity": "critical",
        "category": "deserialization",
        "tags": ["python", "pickle", "deserialization", "rce"],
        "description": "Python pickle deserialization indicators detected — arbitrary code execution possible.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(pickle\.loads|cPickle|_pickle|Unpickler|REDUCE opcode|pickle\.UnpicklingError|__reduce__)"}
        ],
        "extractors": []
    },
    {
        "id": "ruby-yaml-deserialization",
        "name": "Ruby YAML Deserialization Indicators",
        "severity": "critical",
        "category": "deserialization",
        "tags": ["ruby", "yaml", "deserialization", "rce"],
        "description": "Ruby YAML deserialization indicators detected — code execution via YAML.load possible.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(YAML::load|Psych::SyntaxError|Psych::BadAlias|ruby/object:|ruby/sym:|Syck|ActiveSupport::HashWithIndifferentAccess)"}
        ],
        "extractors": []
    },

    # ── OTHER CRITICAL ISSUES ─────────────────────────────────────
    {
        "id": "open-redirect-patterns",
        "name": "Open Redirect Patterns",
        "severity": "medium",
        "category": "redirect",
        "tags": ["open-redirect", "phishing"],
        "description": "Unvalidated redirect URL parameter detected — open redirect to attacker-controlled URL possible.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(<a[^>]+href\s*=\s*[\"'][^\"']*\?[^\"']*(redirect|return|url|next|goto|target|redir)=[^\"']+[\"']|window\.location\s*=\s*[^;]+[\?&](redirect|url|next)=)"}
        ],
        "extractors": []
    },
    {
        "id": "xxe-vulnerability-indicators",
        "name": "XXE Vulnerability Indicators",
        "severity": "high",
        "category": "injection",
        "tags": ["xxe", "xml", "injection"],
        "description": "XML external entity processing indicators detected — XXE injection may be possible.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(<!ENTITY|SYSTEM\s+\"(file|http|ftp)://|<!DOCTYPE[^>]+SYSTEM|xml version=.{0,50}encoding|libxml2|expat|xerces|JAXP|org\.xml\.sax)"}
        ],
        "extractors": []
    },
    {
        "id": "ssrf-parameter-detection",
        "name": "SSRF Parameter Patterns Detected",
        "severity": "high",
        "category": "ssrf",
        "tags": ["ssrf", "injection"],
        "description": "Request parameters that may be vulnerable to Server-Side Request Forgery detected.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(name=[\"']?(url|uri|link|src|href|host|dest|destination|proxy|target|endpoint|redirect)[\"']?|[?&](url|uri|link|src|href|host|proxy|target|endpoint|redirect)=https?://)"}
        ],
        "extractors": [
            {"type": "body_regex_extract",
             "pattern": r"name=[\"']?(url|uri|link|src|href|proxy|target|endpoint)[\"']?", "label": "ssrf-param"}
        ]
    },
    {
        "id": "race-condition-indicators",
        "name": "Race Condition Vulnerability Indicators",
        "severity": "medium",
        "category": "logic",
        "tags": ["race-condition", "concurrency"],
        "description": "Application patterns suggest potential race condition vulnerabilities in critical operations.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(pending.{0,30}transaction|double.?spend|concurrent.{0,30}request|check.?then.?act|time.?of.?check|TOCTOU|concurrent.{0,20}user)"}
        ],
        "extractors": []
    },
    {
        "id": "insecure-randomness",
        "name": "Insecure Randomness Indicators",
        "severity": "medium",
        "category": "cryptography",
        "tags": ["crypto", "randomness", "weak-crypto"],
        "description": "Insecure or predictable random number generation patterns detected.",
        "matchers": [
            {"type": "body_regex",
             "pattern": r"(Math\.random\(\)|rand\(\)|mt_rand\(\)|srand\(time|random\.random\(\)|new Random\(\)|java\.util\.Random|System\.currentTimeMillis\(\).{0,30}token)"}
        ],
        "extractors": []
    },
]

# ─────────────────────────────────────────────
#  SEVERITY CONFIG
# ─────────────────────────────────────────────
SEV_COLOR = {
    "critical": R + BOLD,
    "high":     R,
    "medium":   Y,
    "low":      C,
    "info":     GR,
}
SEV_ICON = {
    "critical": "💀",
    "high":     "🔴",
    "medium":   "🟡",
    "low":      "🔵",
    "info":     "⚪",
}
SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


# ─────────────────────────────────────────────
#  HTTP HELPER
# ─────────────────────────────────────────────
class HTTPResult:
    def __init__(self):
        self.url = ""
        self.status = 0
        self.headers: dict[str, str] = {}
        self.body = ""
        self.raw_cookies: list[str] = []
        self.error: str | None = None
        self.final_url = ""
        self.scheme = "https"
        self.redirect_chain: list[str] = []

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
}
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

def http_get(url: str, method: str = "GET", body: bytes | None = None,
             extra_headers: dict | None = None, timeout: int = 10,
             follow_redirects: bool = True) -> HTTPResult:
    res = HTTPResult()
    res.url = url
    res.scheme = url.split("://")[0] if "://" in url else "https"
    headers = {**DEFAULT_HEADERS, **(extra_headers or {})}
    try:
        req = urllib.request.Request(url, data=body, method=method, headers=headers)
        opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=SSL_CTX),
            urllib.request.HTTPCookieProcessor()
        )
        if not follow_redirects:
            class NoRedirect(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, *a, **kw): return None
            opener.add_handler(NoRedirect())
        with opener.open(req, timeout=timeout) as resp:
            res.status = resp.status
            res.final_url = resp.url
            raw_headers = dict(resp.headers)
            res.headers = {k.lower(): v for k, v in raw_headers.items()}
            raw_set = resp.headers.get_all("set-cookie") or []
            res.raw_cookies = raw_set
            raw_body = resp.read(1024 * 512)  # cap at 512 KB
            try:
                res.body = raw_body.decode("utf-8", errors="replace")
            except Exception:
                res.body = ""
    except urllib.error.HTTPError as e:
        res.status = e.code
        try:
            raw_body = e.read(1024 * 64)
            res.body = raw_body.decode("utf-8", errors="replace")
        except Exception:
            res.body = ""
        res.headers = {k.lower(): v for k, v in dict(e.headers).items()}
    except Exception as exc:
        res.error = str(exc)
    return res


# ─────────────────────────────────────────────
#  MATCHER ENGINE
# ─────────────────────────────────────────────
class Finding:
    def __init__(self, template_id: str, name: str, severity: str,
                 category: str, description: str, url: str,
                 matched_on: str, extractions: dict, source: str = "internal"):
        self.template_id = template_id
        self.name = name
        self.severity = severity
        self.category = category
        self.description = description
        self.url = url
        self.matched_on = matched_on
        self.extractions = extractions
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.source = source  # "internal" or "nuclei"

    def to_dict(self) -> dict:
        return {
            "id": self.template_id,
            "name": self.name,
            "severity": self.severity,
            "category": self.category,
            "description": self.description,
            "url": self.url,
            "matched_on": self.matched_on,
            "extractions": self.extractions,
            "timestamp": self.timestamp,
            "source": self.source,
        }


def run_extractor(ext: dict, res: HTTPResult) -> list[str]:
    etype = ext.get("type", "")
    label = ext.get("label", "value")
    results = []
    if etype == "header_value":
        val = res.headers.get(ext["key"].lower())
        if val:
            results.append(f"{label}={val.strip()}")
    elif etype == "body_regex_extract":
        pattern = ext.get("pattern", "")
        for m in re.finditer(pattern, res.body, re.IGNORECASE | re.MULTILINE):
            snippet = m.group(0)[:100]
            results.append(f"{label}={snippet.strip()}")
            if len(results) >= 3:
                break
    return results


def probe_path(base_url: str, path: str, tmpl: dict,
               timeout: int = 10) -> tuple[bool, HTTPResult, str]:
    """Fetch a probed path and return (matched, result, matched_on_url)."""
    target = base_url.rstrip("/") + path
    method = tmpl.get("method", "GET").upper()
    body_str = tmpl.get("body")
    body_bytes = body_str.encode() if body_str else None
    ct = tmpl.get("content_type")
    extra_h = {"Content-Type": ct} if ct else {}
    r = http_get(target, method=method, body=body_bytes,
                 extra_headers=extra_h, timeout=timeout)
    if r.error:
        return False, r, target

    status_codes = tmpl.get("status_codes", [200])
    status_codes_absent = tmpl.get("status_codes_absent", [])

    if status_codes_absent:
        if r.status not in status_codes_absent:
            return True, r, target
        return False, r, target

    if r.status not in status_codes:
        return False, r, target

    body_pat = tmpl.get("body_regex")
    if body_pat:
        if not re.search(body_pat, r.body, re.IGNORECASE):
            return False, r, target

    return True, r, target


def evaluate_template(tmpl: dict, base_res: HTTPResult,
                      base_url: str, timeout: int = 10) -> Finding | None:
    matchers = tmpl.get("matchers", [])
    condition = tmpl.get("match_condition", "any")  # "any" | "all"
    hits = []

    for m in matchers:
        mtype = m.get("type", "")
        matched = False
        matched_on = base_url

        if mtype == "header_absent":
            key = m["key"].lower()
            matched = key not in base_res.headers
        elif mtype == "header_present":
            key = m["key"].lower()
            matched = key in base_res.headers
        elif mtype == "header_exact":
            key = m["key"].lower()
            val = base_res.headers.get(key, "")
            matched = val.strip().lower() == m["value"].strip().lower()
        elif mtype == "header_regex":
            key = m["key"].lower()
            val = base_res.headers.get(key, "")
            matched = bool(re.search(m["pattern"], val, re.IGNORECASE))
        elif mtype == "body_regex":
            matched = bool(re.search(m["pattern"], base_res.body, re.IGNORECASE))
        elif mtype == "cookie_flag_absent":
            flag = m["flag"].lower()
            kpat = m.get("key_pattern", "")
            for raw_cookie in base_res.raw_cookies:
                parts = [p.strip().lower() for p in raw_cookie.split(";")]
                cookie_name = parts[0].split("=")[0] if parts else ""
                if kpat and not re.search(kpat, cookie_name, re.IGNORECASE):
                    continue
                if flag not in " ".join(parts[1:]):
                    matched = True
                    break
        elif mtype == "scheme":
            if m.get("no_redirect_to_https"):
                if base_res.scheme == "http":
                    # check there is no redirect to https
                    redir_url = base_res.final_url or ""
                    matched = not redir_url.startswith("https://")
                else:
                    matched = False
            else:
                matched = base_res.scheme == m.get("scheme", "https")
        elif mtype == "path_probe":
            ok, _, mu = probe_path(base_url, m["path"], m, timeout)
            matched = ok
            matched_on = mu
        elif mtype == "path_probe_list":
            for path in m.get("paths", []):
                ok, _, mu = probe_path(base_url, path, m, timeout)
                if ok:
                    matched = True
                    matched_on = mu
                    break
        elif mtype == "method_probe":
            target = base_url.rstrip("/") + "/"
            r = http_get(target, method=m["method"], timeout=timeout)
            if not r.error:
                rhc = m.get("response_header_contains", {})
                all_ok = all(
                    v.lower() in r.headers.get(k.lower(), "").lower()
                    for k, v in rhc.items()
                )
                matched = all_ok or r.status in [200, 405]

        hits.append((matched, matched_on))

    if condition == "all":
        overall = all(h for h, _ in hits)
    else:
        overall = any(h for h, _ in hits)

    if not overall:
        return None

    # Gather matched_on from first hit
    matched_on_url = next((u for m, u in hits if m), base_url)

    # Run extractors on base response
    extractions: dict[str, list] = {}
    for ext in tmpl.get("extractors", []):
        vals = run_extractor(ext, base_res)
        if vals:
            label = ext.get("label", "value")
            extractions[label] = vals

    return Finding(
        template_id=tmpl["id"],
        name=tmpl["name"],
        severity=tmpl["severity"],
        category=tmpl["category"],
        description=tmpl["description"],
        url=matched_on_url,
        matched_on=matched_on_url,
        extractions=extractions,
        source="internal"
    )


# ─────────────────────────────────────────────
#  SCANNER
# ─────────────────────────────────────────────
class Scanner:
    def __init__(self, args):
        self.args = args
        self.targets: list[str] = []
        self.templates = TEMPLATES
        self.findings: list[Finding] = []
        self.lock = threading.Lock()
        self.scanned = 0
        self.total_checks = 0
        self._stop = False
        self.nuclei_runner = NucleiRunner(timeout=args.timeout, verbose=args.verbose)

    def load_targets(self) -> list[str]:
        urls = []
        if self.args.url:
            for u in self.args.url:
                urls.append(self._normalise(u))
        if self.args.list:
            try:
                with open(self.args.list) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            urls.append(self._normalise(line))
            except FileNotFoundError:
                self._die(f"Target list not found: {self.args.list}")
        return list(dict.fromkeys(urls))  # dedup preserving order

    @staticmethod
    def _normalise(url: str) -> str:
        url = url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        return url.rstrip("/")

    def _die(self, msg: str):
        print(f"{R}[FATAL]{RS} {msg}")
        sys.exit(1)

    def filter_templates(self) -> list[dict]:
        tmpl = self.templates
        if self.args.severity:
            allowed = {s.lower() for s in self.args.severity.split(",")}
            tmpl = [t for t in tmpl if t["severity"] in allowed]
        if self.args.tags:
            wanted = {t.lower() for t in self.args.tags.split(",")}
            tmpl = [t for t in tmpl
                    if wanted.intersection({x.lower() for x in t.get("tags", [])})]
        if self.args.category:
            allowed = {c.lower() for c in self.args.category.split(",")}
            tmpl = [t for t in tmpl if t["category"].lower() in allowed]
        if self.args.exclude_tags:
            excluded = {t.lower() for t in self.args.exclude_tags.split(",")}
            tmpl = [t for t in tmpl
                    if not excluded.intersection({x.lower() for x in t.get("tags", [])})]
        return tmpl

    def print_finding(self, f: Finding):
        sc = SEV_COLOR.get(f.severity, W)
        icon = SEV_ICON.get(f.severity, "?")
        src_label = f" {GR}[{f.source}]{RS}" if f.source == "nuclei" else ""
        with self.lock:
            sev_label = f"{sc}[{f.severity.upper()}]{RS}"
            print(f"\n  {icon}  {sev_label} {BOLD}{f.name}{RS}{src_label}")
            print(f"     {GR}├─ URL     :{RS} {f.url}")
            print(f"     {GR}├─ ID      :{RS} {f.template_id}")
            print(f"     {GR}├─ Cat     :{RS} {f.category}")
            print(f"     {GR}└─ Detail  :{RS} {f.description}")
            for label, vals in f.extractions.items():
                for v in vals:
                    print(f"       {Y}  ★ {label}: {v}{RS}")

    def scan_target_with_nuclei(self, url: str):
        """Run Nuclei scan on target."""
        if not self.nuclei_runner.is_installed():
            return
        
        if self.args.verbose:
            with self.lock:
                print(f"\n  {B}[nuclei]{RS} Scanning {url}")
        
        # Parse severity filter
        severity_filter = None
        if self.args.severity:
            severity_filter = [s.lower() for s in self.args.severity.split(",")]
        
        # Parse tags filter
        tags_filter = None
        if self.args.tags:
            tags_filter = [t.lower() for t in self.args.tags.split(",")]
        
        # Run scan
        nuclei_findings = self.nuclei_runner.run_scan(
            target=url,
            tags=tags_filter,
            severity=severity_filter
        )
        
        # Convert Nuclei results to Finding objects
        for nf in nuclei_findings:
            try:
                finding = Finding(
                    template_id=nf.get("template-id", nf.get("id", "unknown")),
                    name=nf.get("info", {}).get("name", nf.get("name", "Nuclei Finding")),
                    severity=nf.get("info", {}).get("severity", nf.get("severity", "info")).lower(),
                    category=nf.get("type", "nuclei"),
                    description=nf.get("info", {}).get("description", ""),
                    url=nf.get("matched-at", nf.get("url", url)),
                    matched_on=nf.get("matched-at", nf.get("url", url)),
                    extractions={"nuclei-data": [json.dumps(nf.get("extracted", {}))]} if nf.get("extracted") else {},
                    source="nuclei"
                )
                with self.lock:
                    self.findings.append(finding)
                self.print_finding(finding)
            except Exception as exc:
                if self.args.verbose:
                    with self.lock:
                        print(f"  {GR}[nuclei-err]{RS} {exc}")

    def scan_target(self, url: str, templates: list[dict]):
        if self.args.verbose:
            with self.lock:
                print(f"\n  {C}[~]{RS} Scanning {url}")
        # Fetch base response
        res = http_get(url, timeout=self.args.timeout)
        if res.error:
            with self.lock:
                print(f"  {R}[ERR]{RS} {url} → {res.error}")
            return

        if self.args.verbose:
            with self.lock:
                print(f"  {GR}[base]{RS} HTTP {res.status} | "
                      f"{len(res.body)} bytes | "
                      f"{len(res.headers)} headers")

        for tmpl in templates:
            if self._stop:
                break
            try:
                finding = evaluate_template(tmpl, res, url, self.args.timeout)
                if finding:
                    with self.lock:
                        self.findings.append(finding)
                    self.print_finding(finding)
            except Exception as exc:
                if self.args.verbose:
                    with self.lock:
                        print(f"  {GR}[tmpl-err]{RS} {tmpl['id']}: {exc}")

        with self.lock:
            self.scanned += 1

    def run(self):
        self.targets = self.load_targets()
        templates = self.filter_templates()
        self.total_checks = len(self.targets) * len(templates)

        print(f"\n  {G}[*]{RS} Targets     : {W}{len(self.targets)}{RS}")
        print(f"  {G}[*]{RS} Templates   : {W}{len(templates)}{RS}")
        print(f"  {G}[*]{RS} Threads     : {W}{self.args.threads}{RS}")
        print(f"  {G}[*]{RS} Total checks: {W}{self.total_checks}{RS}")
        
        # Nuclei info
        if self.nuclei_runner.is_installed():
            print(f"  {G}[*]{RS} Nuclei      : {W}✓ Installed ({self.nuclei_runner.get_version()}){RS}")
        else:
            if not self.args.no_nuclei:
                print(f"  {Y}[!]{RS} Nuclei      : {W}Not found (install with: go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest){RS}")
        
        print(f"\n  {DG}{'─'*60}{RS}")

        threads = []
        sem = threading.Semaphore(self.args.threads)

        def worker(url):
            with sem:
                self.scan_target(url, templates)
                if not self.args.no_nuclei and self.nuclei_runner.is_installed():
                    self.scan_target_with_nuclei(url)

        for url in self.targets:
            t = threading.Thread(target=worker, args=(url,), daemon=True)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.print_summary()
        self.export_results()

    def print_summary(self):
        counts = defaultdict(int)
        source_counts = defaultdict(int)
        for f in self.findings:
            counts[f.severity] += 1
            source_counts[f.source] += 1

        print(f"\n  {DG}{'═'*60}{RS}")
        print(f"  {G}{BOLD}  SCAN COMPLETE{RS}")
        print(f"  {DG}{'─'*60}{RS}")
        print(f"  {W}  Targets scanned : {self.scanned}{RS}")
        print(f"  {W}  Total findings  : {len(self.findings)}{RS}")
        for src, cnt in source_counts.items():
            print(f"  {W}  {src.capitalize()} findings : {cnt}{RS}")
        print()
        for sev in ["critical", "high", "medium", "low", "info"]:
            c = counts.get(sev, 0)
            if c:
                sc = SEV_COLOR.get(sev, W)
                icon = SEV_ICON.get(sev, "?")
                bar = "█" * min(c * 2, 30)
                print(f"  {icon} {sc}{sev.upper():10}{RS}  {W}{c:3}{RS}  {DG}{bar}{RS}")
        print(f"  {DG}{'═'*60}{RS}\n")

    def export_results(self):
        if not self.args.output:
            return
        out = self.args.output
        ext = out.rsplit(".", 1)[-1].lower()
        data = [f.to_dict() for f in
                sorted(self.findings, key=lambda x: SEV_ORDER.get(x.severity, 9))]
        if ext == "json":
            with open(out, "w") as fh:
                json.dump({"meta": {
                    "tool": "kArmas_noob",
                    "targets": self.targets,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "total_findings": len(self.findings),
                }, "findings": data}, fh, indent=2)
            print(f"  {G}[+]{RS} JSON report saved → {W}{out}{RS}")
        elif ext == "html":
            self._export_html(data, out)
        else:
            # plain text
            with open(out, "w") as fh:
                for d in data:
                    fh.write(f"[{d['severity'].upper()}] {d['name']}\n")
                    fh.write(f"  URL: {d['url']}\n")
                    fh.write(f"  Source: {d.get('source', 'internal')}\n")
                    fh.write(f"  {d['description']}\n\n")
            print(f"  {G}[+]{RS} Text report saved → {W}{out}{RS}")

    def _export_html(self, data: list[dict], path: str):
        sev_colors = {
            "critical": "#ff2d55",
            "high": "#ff6b35",
            "medium": "#ffd166",
            "low": "#06d6a0",
            "info": "#8d99ae",
        }
        rows = ""
        for d in data:
            sc = sev_colors.get(d["severity"], "#8d99ae")
            src = d.get("source", "internal")
            ext_html = ""
            for k, vals in d.get("extractions", {}).items():
                for v in vals:
                    ext_html += f'<div class="extract">★ {k}: {v}</div>'
            rows += f"""
<tr class="sev-{d['severity']}">
  <td><span class="badge" style="background:{sc}">{d['severity'].upper()}</span></td>
  <td>{d['name']}<br/><small style="color:#888">[{src}]</small></td>
  <td class="url">{d['url']}</td>
  <td>{d['category']}</td>
  <td>{d['description']}{ext_html}</td>
</tr>"""

        # build summary cards outside f-string to avoid backslash restriction
        cards_html = ""
        for s in ["critical", "high", "medium", "low", "info"]:
            col = sev_colors.get(s, "#888")
            cnt = sum(1 for d in data if d["severity"] == s)
            cards_html += (
                f'<div class="card" style="border-color:{col}">'
                f'<div style="color:{col};font-size:1.2em;font-weight:bold">{cnt}</div>'
                f'<div style="color:#888;font-size:.8em">{s.upper()}</div></div>'
            )
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>kArmas_noob Report</title>
<style>
  * {{box-sizing:border-box;margin:0;padding:0}}
  body {{background:#0d0d0d;color:#c9d1d9;font-family:'Courier New',monospace;padding:20px}}
  h1 {{color:#00ff41;font-size:2em;margin-bottom:4px}}
  .sub {{color:#555;margin-bottom:20px;font-size:.9em}}
  table {{width:100%;border-collapse:collapse;font-size:.85em}}
  th {{background:#161b22;color:#00ff41;padding:10px;text-align:left;border-bottom:2px solid #00ff41}}
  td {{padding:8px 10px;border-bottom:1px solid #1f2937;vertical-align:top}}
  tr:hover {{background:#161b22}}
  .badge {{display:inline-block;padding:2px 8px;border-radius:3px;font-weight:bold;color:#000;font-size:.8em}}
  .url {{color:#58a6ff;word-break:break-all;max-width:250px}}
  .extract {{margin-top:4px;color:#f0c27f;font-size:.8em}}
  .summary {{display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap}}
  .card {{background:#161b22;border-left:4px solid;padding:10px 16px;border-radius:4px}}
</style>
</head>
<body>
<h1>&#9760; kArmas_noob</h1>
<div class="sub">Template-Based Vulnerability Scanner Report &bull; {ts} UTC</div>
<div class="summary">
  {cards_html}
</div>
<table>
<thead><tr><th>Severity</th><th>Finding</th><th>URL</th><th>Category</th><th>Details</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</body></html>"""
        with open(path, "w") as fh:
            fh.write(html)
        print(f"  {G}[+]{RS} HTML report saved → {W}{path}{RS}")


# ─────────────────────────────────────────────
#  BANNER + LIST
# ─────────────────────────────────────────────
def print_banner():
    print(SKULL)
    print(f"{G}{BOLD}  ██╗  ██╗ █████╗ ██████╗ ███╗   ███╗ █████╗ ███████╗{RS}")
    print(f"{G}  ██║ ██╔╝██╔══██╗██╔══██╗████╗ ████║██╔══██╗██╔════╝{RS}")
    print(f"{DG}  █████╔╝ ███████║██████╔╝██╔████╔██║███████║███████╗{RS}")
    print(f"{DG}  ██╔═██╗ ██╔══██║██╔══██╗██║╚██╔╝██║██╔══██║╚════██║{RS}")
    print(f"{G}  ██║  ██╗██║  ██║██║  ██║██║ ╚═╝ ██║██║  ██║███████║{RS}")
    print(f"{G}  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝{RS}")
    print(f"\n  {DG}         kArmas_noob  v1.0.0  │  Template Scanner{RS}")
    print(f"  {GR}         We Are Legion. We Do Not Forgive.{RS}")
    print(f"  {GR}         AUTHORIZED USE ONLY — Passive Detection{RS}")
    print(f"\n  {DG}{'─'*60}{RS}\n")


def list_templates():
    print(f"\n  {G}{BOLD}BUILT-IN TEMPLATES ({len(TEMPLATES)} total){RS}\n")
    cats: dict[str, list] = defaultdict(list)
    for t in TEMPLATES:
        cats[t["category"]].append(t)
    for cat, tmpls in sorted(cats.items()):
        print(f"  {C}{BOLD}{cat.upper()}{RS}")
        for t in sorted(tmpls, key=lambda x: SEV_ORDER.get(x["severity"], 9)):
            sc = SEV_COLOR.get(t["severity"], W)
            icon = SEV_ICON.get(t["severity"], "?")
            print(f"    {icon} {sc}{t['severity']:8}{RS}  {t['id']:35}  {GR}{t['name']}{RS}")
        print()


# ─────────────────────────────────────────────
#  ARGUMENT PARSER
# ─────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(
        prog="kArmas_noob",
        description="kArmas_noob — Template-Based Vulnerability Scanner (passive, detection only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python3 kArmas_noob.py --agree -u https://example.com
  python3 kArmas_noob.py --agree -u https://example.com -o report.html
  python3 kArmas_noob.py --agree -l targets.txt -t 20 --severity critical,high
  python3 kArmas_noob.py --agree -u https://example.com --tags cors,headers -v
  python3 kArmas_noob.py --list-templates
  python3 kArmas_noob.py --agree -u https://example.com --no-nuclei
"""
    )
    p.add_argument("--agree", action="store_true",
                   help="Confirm authorized use (REQUIRED)")
    p.add_argument("-u", "--url", nargs="+", metavar="URL",
                   help="Target URL(s)")
    p.add_argument("-l", "--list", metavar="FILE",
                   help="File with one target URL per line")
    p.add_argument("-o", "--output", metavar="FILE",
                   help="Output file (.json / .html / .txt)")
    p.add_argument("-t", "--threads", type=int, default=10,
                   help="Concurrent threads (default: 10)")
    p.add_argument("--timeout", type=int, default=10,
                   help="HTTP timeout in seconds (default: 10)")
    p.add_argument("--severity", metavar="LEVELS",
                   help="Filter by severity: critical,high,medium,low,info")
    p.add_argument("--tags", metavar="TAGS",
                   help="Filter by tags (comma-separated): cors,xss,headers…")
    p.add_argument("--exclude-tags", metavar="TAGS",
                   help="Exclude templates with these tags")
    p.add_argument("--category", metavar="CATS",
                   help="Filter by category: headers,exposure,secrets…")
    p.add_argument("--list-templates", action="store_true",
                   help="List all built-in templates and exit")
    p.add_argument("--no-nuclei", action="store_true",
                   help="Disable Nuclei integration (even if installed)")
    p.add_argument("-v", "--verbose", action="store_true",
                   help="Verbose output")
    return p.parse_args()


# ─────────────────────────────────────────────
#  AUTHORIZATION GATE
# ─────────────────────────────────────────────
def auth_gate():
    print(f"\n  {Y}╔══════════════════════════════════════════════════╗{RS}")
    print(f"  {Y}║   ⚠  AUTHORIZATION REQUIRED                     ║{RS}")
    print(f"  {Y}║                                                  ║{RS}")
    print(f"  {Y}║  kArmas_noob is a passive security scanner.      ║{RS}")
    print(f"  {Y}║  You MUST have explicit authorization to scan    ║{RS}")
    print(f"  {Y}║  any target. Unauthorized scanning is illegal.   ║{RS}")
    print(f"  {Y}║                                                  ║{RS}")
    print(f"  {Y}║  Re-run with --agree to confirm authorized use.  ║{RS}")
    print(f"  {Y}╚══════════════════════════════════════════════════╝{RS}\n")
    sys.exit(1)


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    matrix_rain(2.0)
    print_banner()

    args = parse_args()

    if args.list_templates:
        list_templates()
        sys.exit(0)

    if not args.agree:
        auth_gate()

    if not args.url and not args.list:
        print(f"  {R}[!]{RS} Provide at least one target with -u or -l\n")
        sys.exit(1)

    scanner = Scanner(args)
    try:
        scanner.run()
    except KeyboardInterrupt:
        print(f"\n\n  {Y}[!]{RS} Interrupted — partial results shown above.\n")
        scanner._stop = True
        scanner.print_summary()
        scanner.export_results()
        sys.exit(0)


if __name__ == "__main__":
    main()
