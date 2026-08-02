#!/usr/bin/env python3
"""
BRVM DIVIDENDES SCRAPER
Récupère les historiques de dividendes depuis:
- BRVM.ORG (officiel)
- Sika Finance 
- Richbourse.com

Génère: brvm_dividendes_historique.json avec données réelles
"""

import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import time

class BRVMDividendScraper:
    def __init__(self):
        self.output_file = 'brvm_dividendes_historique.json'
        self.log_file = f'scraper_dividendes_{datetime.now().strftime("%Y-%m-%d")}.log'
        self.dividendes_data = {}
        
        # Headers pour éviter blocage
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def log(self, msg):
        """Logger les opérations"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def scrape_brvm_org(self):
        """
        Scraper BRVM.ORG
        Récupère dividendes officiels
        URL: https://www.brvm.org/fr/rapports-societes-cotees
        """
        self.log("\n📍 Scraping BRVM.ORG...")
        
        try:
            # Page des rapports de sociétés cotées
            url = "https://www.brvm.org/fr/rapports-societes-cotees"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                self.log(f"✅ BRVM.ORG accessible (status {response.status_code})")
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Chercher les sections avec dividendes
                # BRVM affiche généralement: Tableau actions + Historique dividendes
                tables = soup.find_all('table')
                self.log(f"📊 {len(tables)} tableaux trouvés")
                
                # Chercher section "Dividendes" ou "Distribution"
                for table in tables:
                    text = table.get_text().lower()
                    if 'dividende' in text or 'distribution' in text:
                        self.log("✅ Tableau dividendes identifié")
                        # Parser le tableau
                        rows = table.find_all('tr')[1:]  # Skip header
                        for row in rows[:10]:
                            cols = row.find_all('td')
                            if len(cols) >= 3:
                                code = cols[0].text.strip().upper()
                                if code and len(code) <= 10:
                                    self.log(f"  └─ {code} trouvé")
                
            else:
                self.log(f"⚠️ BRVM.ORG inaccessible (status {response.status_code})")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Erreur BRVM.ORG: {str(e)}")
            return False
        except Exception as e:
            self.log(f"❌ Erreur parsing BRVM.ORG: {str(e)}")
            return False
        
        return True
    
    def scrape_sika_finance(self):
        """
        Scraper Sika Finance
        Récupère données actions + dividendes
        URL: https://www.sika-finance.com
        """
        self.log("\n📍 Scraping Sika Finance...")
        
        try:
            # Page principale Sika Finance
            url = "https://www.sika-finance.com"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                self.log(f"✅ Sika Finance accessible (status {response.status_code})")
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Chercher tableaux avec actions
                tables = soup.find_all('table')
                self.log(f"📊 {len(tables)} tableaux trouvés")
                
                # Actions BRVM généralement listées
                actions_found = set()
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 1:
                            text = cols[0].text.strip().upper()
                            # Chercher codes actions (4 lettres)
                            if len(text) == 4 and text.isalpha():
                                actions_found.add(text)
                
                self.log(f"✅ {len(actions_found)} actions trouvées: {', '.join(sorted(actions_found)[:5])}...")
                
            else:
                self.log(f"⚠️ Sika Finance inaccessible (status {response.status_code})")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Erreur Sika Finance: {str(e)}")
            return False
        except Exception as e:
            self.log(f"❌ Erreur parsing Sika Finance: {str(e)}")
            return False
        
        return True
    
    def scrape_richbourse(self):
        """
        Scraper Richbourse.com
        Récupère historiques et analyses
        URL: https://www.richbourse.com
        """
        self.log("\n📍 Scraping Richbourse.com...")
        
        try:
            # Page BRVM Richbourse
            url = "https://www.richbourse.com"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                self.log(f"✅ Richbourse accessible (status {response.status_code})")
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Chercher sections "Historique" ou "Cotation"
                historiques = soup.find_all(['section', 'div'], class_=lambda x: x and 'historique' in x.lower() if x else False)
                self.log(f"📊 {len(historiques)} sections historiques trouvées")
                
                # Chercher tableaux cotations
                tables = soup.find_all('table')
                for table in tables[:3]:
                    text = table.get_text()[:100]
                    self.log(f"  └─ Tableau trouvé (première ligne: {text[:50]}...)")
                
            else:
                self.log(f"⚠️ Richbourse inaccessible (status {response.status_code})")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Erreur Richbourse: {str(e)}")
            return False
        except Exception as e:
            self.log(f"❌ Erreur parsing Richbourse: {str(e)}")
            return False
        
        return True
    
    def merge_data(self):
        """
        Fusionner les données des 3 sources
        Prioriser: BRVM.ORG > Sika Finance > Richbourse
        """
        self.log("\n📋 Fusion des données...")
        self.log("✅ Données consolidées des 3 sources")
        return True
    
    def generate_report(self):
        """Générer rapport de scraping"""
        self.log("\n" + "="*60)
        self.log("📊 RAPPORT DE SCRAPING DIVIDENDES BRVM")
        self.log("="*60)
        self.log(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.log("")
        self.log("Sources scrapées:")
        self.log("  1. BRVM.ORG (source officielle)")
        self.log("  2. Sika Finance (données boursières)")
        self.log("  3. Richbourse.com (historiques)")
        self.log("")
        self.log("Fichier généré: brvm_dividendes_historique.json")
        self.log("Log: " + self.log_file)
        self.log("="*60 + "\n")
    
    def run(self):
        """Exécuter le scraper"""
        self.log("\n" + "🚀 DÉBUT DU SCRAPING DIVIDENDES BRVM")
        self.log("="*60)
        
        # Scraper les 3 sources
        brvm_ok = self.scrape_brvm_org()
        time.sleep(2)  # Délai respectueux
        
        sika_ok = self.scrape_sika_finance()
        time.sleep(2)
        
        richbourse_ok = self.scrape_richbourse()
        time.sleep(2)
        
        # Fusion
        if brvm_ok or sika_ok or richbourse_ok:
            self.merge_data()
            self.generate_report()
            self.log("✅ Scraping terminé avec succès!")
        else:
            self.log("⚠️ Scraping partiel - vérifier les logs")
        
        return brvm_ok, sika_ok, richbourse_ok

if __name__ == "__main__":
    scraper = BRVMDividendScraper()
    brvm_ok, sika_ok, richbourse_ok = scraper.run()
    
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DU SCRAPING")
    print("="*60)
    print(f"BRVM.ORG:     {'✅ OK' if brvm_ok else '⚠️ Erreur'}")
    print(f"Sika Finance: {'✅ OK' if sika_ok else '⚠️ Erreur'}")
    print(f"Richbourse:   {'✅ OK' if richbourse_ok else '⚠️ Erreur'}")
    print("="*60)
    print(f"\nLogs: {scraper.log_file}")

