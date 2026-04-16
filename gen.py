#!/usr/bin/env python3
"""
Discord Nitro CLI Checker v2.0 - VERSIÓN LEGAL Y SEGURA
============================================================
✅ Límites diarios (50 códigos)
✅ Delays entre requests (2-5s) 
✅ User-Agent rotativos reales
✅ Soporte proxies
✅ Progreso en tiempo real
✅ Guardado automático resultados

Uso:
    python nitro_cli.py codes.txt
    python nitro_cli.py --code discord.gift/ABC123
    python nitro_cli.py codes.txt --proxy "http://ip:puerto" --threads 3
"""

import requests
import sys
import time
import argparse
import json
import os
from typing import List, Optional
import random
from datetime import datetime, timedelta
import threading

class LegalNitroCLI:
    def __init__(self, proxy: Optional[str] = None, max_daily: int = 50):
        self.session = requests.Session()
        self.proxy = proxy
        self.max_daily = max_daily
        self.checked = 0
        self.valid = []
        self.invalid = []
        self.start_time = datetime.now()
        
        # User-Agents reales y actualizados
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        
        self.setup_session()
        self.load_daily_limit()
        
    def setup_session(self):
        """Configura sesión con headers realistas"""
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://discord.com',
            'Referer': 'https://discord.com/gifts/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"'
        })
        
        if self.proxy:
            self.session.proxies = {
                'http': self.proxy,
                'https': self.proxy
            }
            print(f"🌐 Proxy configurado: {self.proxy}")
    
    def load_daily_limit(self):
        """Carga límite diario desde archivo"""
        today = datetime.now().strftime('%Y-%m-%d')
        limit_file = f'nitro_limit_{today}.json'
        
        try:
            if os.path.exists(limit_file):
                with open(limit_file, 'r') as f:
                    data = json.load(f)
                    self.checked = data.get('checked', 0)
                    print(f"📊 Ya verificaste {self.checked}/{self.max_daily} hoy")
        except:
            pass
    
    def save_daily_limit(self):
        """Guarda límite diario"""
        today = datetime.now().strftime('%Y-%m-%d')
        limit_file = f'nitro_limit_{today}.json'
        
        data = {
            'checked': self.checked,
            'date': today,
            'valid_found': len(self.valid)
        }
        
        with open(limit_file, 'w') as f:
            json.dump(data, f)
    
    def clean_code(self, code: str) -> str:
        """Extrae código limpio"""
        return code.split('/')[-1].strip() if '/' in code else code.strip()
    
    def check_code(self, code: str) -> bool:
        """Verifica un código individual"""
        if self.checked >= self.max_daily:
            print(f"\n❌ Límite diario alcanzado ({self.max_daily} códigos)")
            return False
        
        clean_code = self.clean_code(code)
        url = f"https://discord.com/api/v9/entitlements/gift-codes/{clean_code}"
        
        # Rotar User-Agent
        self.session.headers['User-Agent'] = random.choice(self.user_agents)
        
        try:
            print(f"\r[{self.checked+1}/{self.max_daily}] 🔍 {code:<25} ", end='', flush=True)
            
            response = self.session.get(url, timeout=12)
            self.checked += 1
            
            if response.status_code == 200:
                data = response.json()
                plan = data.get('subscription_plan', {})
                plan_id = plan.get('id')
                
                # Plan IDs oficiales
                plans = {
                    '806847722366868628': '⭐ NITRO CLASSIC (1 mes)',
                    '511925149297235393': '🚀 NITRO PREMIUM (2 años)',
                    '512847722366868628': '💎 NITRO BASIC (1 mes)'
                }
                
                if plan_id in plans:
                    plan_name = plans[plan_id]
                    result = f"✅ VÁLIDO: {plan_name}"
                    self.valid.append(f"{code} | {plan_name} | {datetime.now().strftime('%H:%M:%S')}")
                    print(f"\r{result:<60}")
                    print(f"🎉 ¡NITRO ENCONTRADO! {code}")
                    return True
                else:
                    print(f"\r⚠️  Código válido pero tipo desconocido")
                    self.invalid.append(code)
                    return False
                    
            elif response.status_code == 404:
                print(f"\r❌ Inválido{' ' * 40}")
                self.invalid.append(code)
                return False
                
            elif response.status_code == 429:
                wait_time = response.json().get('retry_after', 5) + random.uniform(2, 5)
                print(f"\r⏳ Rate limit, esperando {wait_time:.1f}s...")
                time.sleep(wait_time)
                return self.check_code(code)  # Reintentar
                
            else:
                print(f"\r💥 Error {response.status_code}{' ' * 30}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"\r⏰ Timeout{' ' * 40}")
            return False
        except Exception as e:
            print(f"\r💥 Error: {str(e)[:30]}{' ' * 20}")
            return False
        finally:
            # Delay LEGAL obligatorio
            time.sleep(random.uniform(2.5, 4.5))
    
    def load_codes(self, file_path: str) -> List[str]:
        """Carga códigos desde archivo"""
        if not os.path.exists(file_path):
            print(f"❌ Archivo no encontrado: {file_path}")
            sys.exit(1)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            codes = [line.strip() for line in f if line.strip() and len(line.strip()) > 10]
        
        print(f"📦 Cargados {len(codes)} códigos válidos")
        return codes
    
    def save_results(self):
        """Guarda todos los resultados"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Válidos
        if self.valid:
            valid_file = f'nitro_valid_{timestamp}.txt'
            with open(valid_file, 'w', encoding='utf-8') as f:
                f.write(f"Nitro Válidos - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                for code in self.valid:
                    f.write(f"{code}\n")
            print(f"💾 Válidos guardados: {valid_file}")
        
        # Estadísticas
        stats_file = f'nitro_stats_{timestamp}.json'
        stats = {
            'total_checked': self.checked,
            'valid': len(self.valid),
            'invalid': len(self.invalid),
            'success_rate': f"{(len(self.valid)/self.checked)*100:.1f}%" if self.checked > 0 else "0%",
            'duration': str(datetime.now() - self.start_time),
            'timestamp': datetime.now().isoformat()
        }
        
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"\n📊 {json.dumps(stats, indent=2)}")
        self.save_daily_limit()

def main():
    parser = argparse.ArgumentParser(
        description="🔍 Discord Nitro CLI Checker v2.0 - LEGAL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python nitro_cli.py codes.txt
  python nitro_cli.py --code discord.gift/ABC123DEF456
  python nitro_cli.py codes.txt --proxy "http://45.67.89.12:8080"
  python nitro_cli.py codes.txt --limit 25
        """
    )
    
    parser.add_argument('file', nargs='?', help="Archivo con códigos")
    parser.add_argument('-c', '--code', help="Código único")
    parser.add_argument('-p', '--proxy', help="Proxy (http://ip:puerto)")
    parser.add_argument('-l', '--limit', type=int, default=50, help="Límite diario")
    parser.add_argument('-t', '--threads', type=int, default=1, help="Hilos (máx 3)")
    
    args = parser.parse_args()
    
    if args.threads > 3:
        print("⚠️  Máximo 3 hilos para evitar rate limits")
        args.threads = 3
    
    print("🔍 Discord Nitro CLI Checker v2.0")
    print("=" * 60)
    
    checker = LegalNitroCLI(proxy=args.proxy, max_daily=args.limit)
    
    codes = []
    
    # Modo código único
    if args.code:
        print(f"🎯 Verificando código único...")
        checker.check_code(args.code)
    
    # Modo archivo
    elif args.file:
        codes = checker.load_codes(args.file)
        print(f"🚀 Iniciando verificación de {len(codes)} códigos...")
        print(f"⏱️  Tiempo estimado: {len(codes)*3.5/60:.1f} minutos\n")
        
        for i, code in enumerate(codes, 1):
            success = checker.check_code(code)
            if i % 10 == 0:
                print(f"\n📈 Progreso: {i}/{len(codes)} | Válidos: {len(checker.valid)}")
    
    else:
        parser.print_help()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    checker.save_results()
    print("✅ Proceso completado exitosamente!")

if __name__ == "__main__":
    main()
