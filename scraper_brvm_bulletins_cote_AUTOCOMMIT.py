#!/usr/bin/env python3
"""
BRVM BULLETINS COTE SCRAPER - AUTO COMMIT VERSION
Scrape les bulletins officiels BRVM et committe automatiquement sur GitHub
"""

import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import subprocess

class BRVMBulletinsScraperAutoCommit:
    def __init__(self):
        self.output_file = 'brvm_cote_du_jour.json'
        self.log_file = f'scraper_cote_{datetime.now().strftime("%Y-%m-%d")}.log'
        self.cote_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'heure': datetime.now().strftime('%H:%M:%S'),
            'source': 'https://www.brvm.org/fr/bulletins-officiels-de-la-cote',
            'actions': {},
            'synthese': {
                'indice_composite': 0,
                'volume_total_mds': 0,
                'actions_hausse': 0,
                'actions_baisse': 0,
                'nb_actions': 0
            },
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
    
    def scrape_brvm_org(self):
        """Scraper BRVM.org bulletins officiels"""
        self.log("\n📍 Scraping BRVM.org bulletins officiels...")
        
        url = 'https://www.brvm.org/fr/bulletins-officiels-de-la-cote'
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                self.log(f"✅ BRVM.ORG accessible (status 200)")
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Chercher tableau des actions
                tables = soup.find_all('table')
                self.log(f"📊 Tables trouvées: {len(tables)}")
                
                actions_count = 0
                hausse_count = 0
                baisse_count = 0
                
                # Parser les tables
                for table in tables:
                    rows = table.find_all('tr')
                    
                    for row in rows[1:]:  # Skip header
                        try:
                            cols = row.find_all('td')
                            if len(cols) >= 4:
                                code = cols[0].get_text().strip()
                                cours = cols[1].get_text().strip()
                                variation_str = cols[2].get_text().strip()
                                volume = cols[3].get_text().strip()
                                
                                if code and cours:
                                    try:
                                        cours_val = float(cours.replace(',', '.').replace(' ', ''))
                                        variation_val = float(variation_str.replace(',', '.').replace('%', '').replace(' ', ''))
                                        
                                        self.cote_data['actions'][code] = {
                                            'cours': cours_val,
                                            'variation': variation_val,
                                            'volume': volume
                                        }
                                        
                                        actions_count += 1
                                        if variation_val > 0:
                                            hausse_count += 1
                                        elif variation_val < 0:
                                            baisse_count += 1
                                        
                                        self.log(f"  ✅ {code}: {cours_val} FCFA ({variation_val:+.2f}%)")
                                    except:
                                        pass
                        except:
                            pass
                
                # Mettre à jour synthèse
                self.cote_data['synthese']['nb_actions'] = actions_count
                self.cote_data['synthese']['actions_hausse'] = hausse_count
                self.cote_data['synthese']['actions_baisse'] = baisse_count
                
                self.log(f"\n✅ Scraping terminé!")
                self.log(f"   Actions trouvées: {actions_count}")
                self.log(f"   En hausse: {hausse_count}")
                self.log(f"   En baisse: {baisse_count}")
                
                return True
            else:
                self.log(f"⚠️ BRVM.ORG inaccessible (status {response.status_code})")
                return False
                
        except Exception as e:
            self.log(f"❌ Erreur scraping BRVM.ORG: {str(e)}")
            return False
    
    def generate_json(self):
        """Générer le fichier JSON"""
        self.log("\n💾 Génération JSON...")
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump({'cote_data': self.cote_data}, f, ensure_ascii=False, indent=2)
            
            self.log(f"✅ JSON généré: {self.output_file}")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur génération JSON: {str(e)}")
            return False
    
    def commit_to_github(self):
        """Committer automatiquement sur GitHub"""
        self.log("\n📤 Commit automatique GitHub...")
        
        try:
            # Configurer git
            os.system('git config user.email "bot@brvm.automation"')
            os.system('git config user.name "BRVM Bot"')
            
            # Add et commit
            os.system(f'git add {self.output_file}')
            commit_msg = f'Update cote data - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            result = os.system(f'git commit -m "{commit_msg}"')
            
            if result == 0:
                self.log(f"✅ Commit réussi: {commit_msg}")
                
                # Push
                push_result = os.system('git push origin main 2>&1')
                if push_result == 0:
                    self.log("✅ Push réussi!")
                    return True
                else:
                    self.log("⚠️ Push échoué (peut être normal si rien à pousser)")
                    return True
            else:
                self.log("⚠️ Aucune modification à committer")
                return True
                
        except Exception as e:
            self.log(f"⚠️ Erreur commit: {str(e)}")
            return False
    
    def generate_report(self):
        """Générer rapport final"""
        self.log("\n" + "="*60)
        self.log("📊 RAPPORT DE SCRAPING BULLETINS DE COTE BRVM")
        self.log("="*60)
        self.log(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.log("")
        self.log("Source scrapée:")
        self.log("  https://www.brvm.org/fr/bulletins-officiels-de-la-cote")
        self.log("")
        self.log(f"Actions collectées: {len(self.cote_data['actions'])}")
        self.log(f"Actions en hausse: {self.cote_data['synthese']['actions_hausse']}")
        self.log(f"Actions en baisse: {self.cote_data['synthese']['actions_baisse']}")
        self.log("")
        self.log("Fichiers générés:")
        self.log(f"  - {self.output_file} (données de cote)")
        self.log(f"  - {self.log_file} (log détaillé)")
        self.log("="*60 + "\n")
    
    def run(self):
        """Exécuter le scraper complet"""
        self.log("\n" + "="*60)
        self.log("🚀 SCRAPER BULLETINS DE COTE BRVM (AUTO-COMMIT)")
        self.log("="*60)
        
        # Scraper
        scrape_ok = self.scrape_brvm_org()
        
        if scrape_ok and len(self.cote_data['actions']) > 0:
            # Générer JSON
            json_ok = self.generate_json()
            
            if json_ok:
                # Committer sur GitHub
                self.commit_to_github()
        
        # Rapport final
        self.generate_report()
        
        self.log("✅ Scraper terminé!")

if __name__ == "__main__":
    scraper = BRVMBulletinsScraperAutoCommit()
    scraper.run()
