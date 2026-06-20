"""Módulo de brute force de subdomínios."""

import dns.resolver
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any
from beaversec.utils.security import validate_target

DEFAULT_WORDLIST = [
    'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
    'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'm', 'imap', 'test',
    'ns', 'blog', 'pop3', 'dev', 'www2', 'admin', 'forum', 'news', 'vpn', 'ns3',
    'mail2', 'new', 'mysql', 'old', 'lists', 'support', 'mobile', 'mx', 'static',
    'docs', 'beta', 'shop', 'sql', 'secure', 'demo', 'cp', 'calendar', 'wiki',
    'web', 'media', 'email', 'images', 'img', 'www1', 'intranet', 'portal', 'video',
    'sip', 'dns2', 'api', 'cdn', 'stats', 'dns1', 'ns4', 'www3', 'dns', 'apps',
    'internal', 'fs', 'download', 'ftp2', 'vps', 'crm', 'admin2', 'proxy', 'test2',
    'info', 'host', 'sip2', 'panel', 'ftp1', 'reseller', 'video2', 'm2', 'bugs',
]

def run(target: str, **kwargs) -> Dict[str, Any]:
    """Descobre subdomínios por brute force."""
    target_type = validate_target(target)
    if target_type != 'domain':
        raise ValueError(f"Subdomain brute requer um domínio, não {target_type}")
    
    wordlist = kwargs.get('wordlist', DEFAULT_WORDLIST)
    if isinstance(wordlist, str):
        try:
            with open(wordlist, 'r') as f:
                wordlist = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            wordlist = DEFAULT_WORDLIST
    
    max_threads = kwargs.get('max_threads', 20)
    timeout = kwargs.get('timeout', 3)
    
    found = []
    
    def check_subdomain(sub):
        full_domain = f"{sub}.{target}"
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = timeout
            answers = resolver.resolve(full_domain, 'A')
            if answers:
                ips = [str(r) for r in answers]
                return {"subdomain": full_domain, "ips": ips, "found": True}
        except:
            pass
        return {"subdomain": full_domain, "found": False}
    
    print(f"🔍 Brute force em {target} com {len(wordlist)} subdomínios...")
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(check_subdomain, sub): sub for sub in wordlist}
        count = 0
        for future in as_completed(futures):
            count += 1
            if count % 50 == 0:
                print(f"   ⏳ Progresso: {count}/{len(wordlist)}")
            
            result = future.result()
            if result['found']:
                found.append(result)
                print(f"   ✅ Encontrado: {result['subdomain']} -> {', '.join(result['ips'])}")
    
    return {
        "target": target,
        "subdomains": found,
        "total_found": len(found),
        "total_tested": len(wordlist)
    }