#!/usr/bin/env python3
"""
BRVM RESUME SCRAPER
Récupère Top 5 gagnants, Flop 5 perdants et indices depuis /fr/resume
"""

import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup

class BRVMResumeScraper:
    def __init__(self):
        self.output_file = 'brvm_resume.json'
        self.log_file = f'scraper_resume_{datetime.now().strftime("%Y-%m-%d")}.log'
        self.resume_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'heure': datetime.now().strftime('%H:%M:%S'),
            'source': 'https://www.brvm.org/fr/resume',
            'top_5_gagnants': [],
            'flop_5_perdants': [],
            'indices': {},
            'indices_sectoriels': {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def log(self, msg):
        """Logger"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def scrape_resume(self):
        """Scraper la page resume"""
        self.log("\n📍 Scraping BRVM.org /fr/resume...")
        
        url = 'https://www.brvm.org/fr/resume'
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                self.log(f"✅ BRVM.org/resume accessible (status 200)")
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Chercher les tables TOP 5 et FLOP 5
                tables = soup.find_all('table')
                self.log(f"📊 Tables trouvées: {len(tables)}")
                
                # Parser les tables
                for table in tables:
                    # Chercher le header pour identifier TOP 5 ou FLOP 5
                    header_text = table.get_text()
                    
                    rows = table.find_all('tr')
                    
                    for row in rows[1:]:  # Skip header
                        try:
                            cols = row.find_all('td')
                            if len(cols) >= 3:
                                code = cols[0].get_text().strip()
                                cours_text = cols[1].get_text().strip()
                                variation_text = cols[2].get_text().strip()
                                
                                if code and cours_text:
                                    try:
                                        cours_val = float(cours_text.replace(',', '.').replace(' ', ''))
                                        variation_val = float(variation_text.replace(',', '.').replace('%', '').replace(' ', ''))
                                        
                                        action_data = {
                                            'code': code,
                                            'cours': cours_val,
                                            'variation': variation_val
                                        }
                                        
                                        # Ajouter au top 5 ou flop 5 selon le signe
                                        if 'TOP' in header_text.upper():
                                            if len(self.resume_data['top_5_gagnants']) < 5:
                                                self.resume_data['top_5_gagnants'].append(action_data)
                                                self.log(f"  ✅ TOP 5: {code} - {cours_val} FCFA ({variation_val:+.2f}%)")
                                        elif 'FLOP' in header_text.upper():
                                            if len(self.resume_data['flop_5_perdants']) < 5:
                                                self.resume_data['flop_5_perdants'].append(action_data)
                                                self.log(f"  ✅ FLOP 5: {code} - {cours_val} FCFA ({variation_val:+.2f}%)")
                                    except:
                                        pass
                        except:
                            pass
                
                self.log(f"\n✅ Scraping terminé!")
                self.log(f"   Top 5 gagnants: {len(self.resume_data['top_5_gagnants'])}")
                self.log(f"   Flop 5 perdants: {len(self.resume_data['flop_5_perdants'])}")
                
                return True
            else:
                self.log(f"⚠️ BRVM.org/resume inaccessible (status {response.status_code})")
                return False
                
        except Exception as e:
            self.log(f"❌ Erreur scraping: {str(e)}")
            return False
    
    def generate_json(self):
        """Générer le fichier JSON"""
        self.log("\n💾 Génération JSON...")
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.resume_data, f, ensure_ascii=False, indent=2)
            
            self.log(f"✅ JSON généré: {self.output_file}")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur génération JSON: {str(e)}")
            return False
    
    def generate_report(self):
        """Générer rapport final"""
        self.log("\n" + "="*60)
        self.log("📊 RAPPORT DE SCRAPING RESUME BRVM")
        self.log("="*60)
        self.log(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.log("")
        self.log("Source scrapée:")
        self.log("  https://www.brvm.org/fr/resume")
        self.log("")
        self.log(f"Top 5 gagnants collectés: {len(self.resume_data['top_5_gagnants'])}")
        self.log(f"Flop 5 perdants collectés: {len(self.resume_data['flop_5_perdants'])}")
        self.log("")
        self.log("Fichiers générés:")
        self.log(f"  - {self.output_file} (données resume)")
        self.log(f"  - {self.log_file} (log détaillé)")
        self.log("="*60 + "\n")
    
    def run(self):
        """Exécuter le scraper"""
        self.log("\n" + "="*60)
        self.log("🚀 SCRAPER RESUME BRVM (TOP 5 + FLOP 5)")
        self.log("="*60)
        
        # Scraper
        scrape_ok = self.scrape_resume()
        
        if scrape_ok:
            # Générer JSON
            json_ok = self.generate_json()
        
        # Rapport final
        self.generate_report()
        
        self.log("✅ Scraper terminé!")

if __name__ == "__main__":
    scraper = BRVMResumeScraper()
    scraper.run()
