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
        self.assertFalse(validate_ip("999.999.999.999"))
    
    def test_validate_domain(self):
        self.assertTrue(validate_domain("google.com"))
        self.assertTrue(validate_domain("sub.example.com"))
        self.assertFalse(validate_domain("192.168.1.1"))
    
    def test_validate_cidr(self):
        self.assertTrue(validate_cidr("192.168.1.0/24"))
        self.assertTrue(validate_cidr("10.0.0.0/8"))
        self.assertFalse(validate_cidr("192.168.1.1"))
    
    def test_sanitize_target(self):
        self.assertEqual(sanitize_target(" google.com "), "google.com")
        self.assertEqual(sanitize_target("google.com; rm -rf /"), "google.comrm -rf ")
        
        with self.assertRaises(ValueError):
            sanitize_target("")
    
    def test_validate_target(self):
        self.assertEqual(validate_target("192.168.1.1"), "ip")
        self.assertEqual(validate_target("google.com"), "domain")
        self.assertEqual(validate_target("192.168.1.0/24"), "cidr")
        
        with self.assertRaises(ValueError):
            validate_target("invalid_target")

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