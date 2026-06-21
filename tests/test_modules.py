"""Testes automatizados para os módulos do BeaverSec."""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from beaversec.utils.security import (
    validate_ip, validate_domain, validate_cidr, 
    sanitize_target, validate_target
)

class TestSecurity(unittest.TestCase):
    def test_validate_ip(self):
        self.assertTrue(validate_ip("192.168.1.1"))
        self.assertTrue(validate_ip("8.8.8.8"))
        self.assertTrue(validate_ip("2001:db8::1"))
        self.assertFalse(validate_ip("999.999.999.999"))
        self.assertFalse(validate_ip("google.com"))
    
    def test_validate_domain(self):
        self.assertTrue(validate_domain("google.com"))
        self.assertTrue(validate_domain("sub.example.com"))
        self.assertTrue(validate_domain("www.google.com.br"))
        self.assertFalse(validate_domain("192.168.1.1"))
        self.assertFalse(validate_domain("google"))
    
    def test_validate_cidr(self):
        self.assertTrue(validate_cidr("192.168.1.0/24"))
        self.assertTrue(validate_cidr("10.0.0.0/8"))
        self.assertTrue(validate_cidr("192.168.1.1/32"))
        # 192.168.1.1 sem barra NÃO é CIDR
        self.assertFalse(validate_cidr("192.168.1.1"))
        self.assertFalse(validate_cidr("google.com"))
    
    def test_sanitize_target(self):
        # Testa remoção de espaços
        self.assertEqual(sanitize_target(" google.com "), "google.com")
        
        # Testa remoção de caracteres maliciosos
        result = sanitize_target("google.com; rm -rf /")
        self.assertEqual(result, "google.comrm-rf/")
        self.assertNotIn(";", result)
        self.assertNotIn("$", result)
        self.assertNotIn("(", result)
        
        # Testa remoção de caracteres de controle
        result = sanitize_target("google.com\x00test")
        self.assertEqual(result, "google.comtest")
        
        # Testa alvo vazio
        with self.assertRaises(ValueError):
            sanitize_target("")
        with self.assertRaises(ValueError):
            sanitize_target("   ")
    
    def test_validate_target(self):
        # Testa IP
        self.assertEqual(validate_target("192.168.1.1"), "ip")
        self.assertEqual(validate_target("8.8.8.8"), "ip")
        self.assertEqual(validate_target("2001:db8::1"), "ip")
        
        # Testa domínio
        self.assertEqual(validate_target("google.com"), "domain")
        self.assertEqual(validate_target("www.google.com.br"), "domain")
        
        # Testa CIDR
        self.assertEqual(validate_target("192.168.1.0/24"), "cidr")
        self.assertEqual(validate_target("10.0.0.0/8"), "cidr")
        
        # Testa alvo inválido
        with self.assertRaises(ValueError):
            validate_target("invalid_target")
        with self.assertRaises(ValueError):
            validate_target("")

class TestModules(unittest.TestCase):
    def test_import_modules(self):
        modules = ["ping_sweep", "port_scanner", "dns_enum", "ssl_scan", 
                   "http_headers", "subdomain_brute", "traceroute"]
        
        for module_name in modules:
            try:
                module = __import__(f"beaversec.modules.{module_name}", fromlist=["run"])
                self.assertTrue(hasattr(module, "run"))
                print(f"✅ Módulo {module_name} importado com sucesso")
            except ImportError as e:
                self.fail(f"Erro ao importar {module_name}: {e}")

if __name__ == "__main__":
    unittest.main()
