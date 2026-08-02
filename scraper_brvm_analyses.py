#!/usr/bin/env python3
"""
BRVM ANALYSES SCRAPER
Récupère analyses trading depuis Madis Invest et Sika Finance

Sources:
- Madis Invest (4 sources)
  ├─ https://madisinvest.com/actualites/boursiere
  ├─ https://madisinvest.com/actualites/secteur-boursier
  ├─ https://madisinvest.com/actualites/macro-economie
  └─ https://madisinvest.com/actualites/economie

- Sika Finance (4 sources)
  ├─ https://www.sikafinance.com/bourse/
  ├─ https://www.sikafinance.com/marches/actualites_bourse_brvm
  ├─ https://www.sikafinance.com/marches/communiques_brvm
  └─ https://www.sikafinance.com/marches/dividendes

Génère: brvm_analyses.json
"""

import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import time

class BRVMAnalysesScraper:
    def __init__(self):
        self.output_file = 'brvm_analyses.json'
        self.log_file = f'scraper_analyses_{datetime.now().strftime("%Y-%m-%d")}.log'
        self.analyses_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'heure': datetime.now().strftime('%H:%M:%S'),
            'madis_invest': [],
            'sika_finance': [],
            'timestamp': datetime.now().isoformat()
        }
        
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
    
    def scrape_madis_invest(self):
        """Scraper Madis Invest"""
        self.log("\n📍 Scraping Madis Invest...")
        
        urls = {
            'boursiere': 'https://madisinvest.com/actualites/boursiere',
            'secteur_boursier': 'https://madisinvest.com/actualites/secteur-boursier',
            'macro_economie': 'https://madisinvest.com/actualites/macro-economie',
            'economie': 'https://madisinvest.com/actualites/economie'
        }
        
        for category, url in urls.items():
            try:
                self.log(f"  Scraping: {category}...")
                response = requests.get(url, headers=self.headers, timeout=10)
                response.encoding = 'utf-8'
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Chercher articles/analyses
                    articles = soup.find_all(['article', 'div'], class_=lambda x: x and 'article' in x.lower() if x else False)
                    
                    for article in articles[:3]:  # Top 3 par catégorie
                        try:
                            title = article.find(['h2', 'h3', 'a'])
                            if title:
                                title_text = title.get_text().strip()
                                
                                # Chercher description/contenu
                                desc = article.find(['p', 'span'])
                                desc_text = desc.get_text().strip() if desc else ''
                                
                                if title_text:
                                    self.analyses_data['madis_invest'].append({
                                        'category': category,
                                        'title': title_text,
                                        'description': desc_text[:200],  # 200 chars max
                                        'source': 'Madis Invest',
                                        'url': url,
                                        'date': datetime.now().strftime('%Y-%m-%d')
                                    })
                                    self.log(f"    ✅ {title_text[:60]}...")
                        except:
                            pass
                    
                    self.log(f"  ✅ {category} OK - {len(articles)} articles trouvés")
                else:
                    self.log(f"  ⚠️ {category} inaccessible (status {response.status_code})")
                
                time.sleep(1)  # Délai respectueux
                
            except Exception as e:
                self.log(f"  ❌ Erreur {category}: {str(e)}")
    
    def scrape_sika_finance(self):
        """Scraper Sika Finance"""
        self.log("\n📍 Scraping Sika Finance...")
        
        urls = {
            'bourse': 'https://www.sikafinance.com/bourse/',
            'actualites_brvm': 'https://www.sikafinance.com/marches/actualites_bourse_brvm',
            'communiques': 'https://www.sikafinance.com/marches/communiques_brvm',
            'dividendes': 'https://www.sikafinance.com/marches/dividendes'
        }
        
        for category, url in urls.items():
            try:
                self.log(f"  Scraping: {category}...")
                response = requests.get(url, headers=self.headers, timeout=10)
                response.encoding = 'utf-8'
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Chercher actualités/communiqués
                    items = soup.find_all(['div', 'li'], class_=lambda x: x and any(k in x.lower() for k in ['item', 'article', 'news']) if x else False)
                    
                    for item in items[:3]:  # Top 3 par catégorie
                        try:
                            title = item.find(['h3', 'h4', 'a', 'strong'])
                            if title:
                                title_text = title.get_text().strip()
                                
                                # Chercher contenu
                                desc = item.find(['p', 'span', 'small'])
                                desc_text = desc.get_text().strip() if desc else ''
                                
                                if title_text:
                                    self.analyses_data['sika_finance'].append({
                                        'category': category,
                                        'title': title_text,
                                        'description': desc_text[:200],
                                        'source': 'Sika Finance',
                                        'url': url,
                                        'date': datetime.now().strftime('%Y-%m-%d')
                                    })
                                    self.log(f"    ✅ {title_text[:60]}...")
                        except:
                            pass
                    
                    self.log(f"  ✅ {category} OK - {len(items)} items trouvés")
                else:
                    self.log(f"  ⚠️ {category} inaccessible (status {response.status_code})")
                
                time.sleep(1)  # Délai respectueux
                
            except Exception as e:
                self.log(f"  ❌ Erreur {category}: {str(e)}")
    
    def generate_json(self):
        """Générer le fichier JSON de sortie"""
        self.log("\n💾 Génération JSON...")
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.analyses_data, f, ensure_ascii=False, indent=2)
            
            self.log(f"✅ JSON généré: {self.output_file}")
            self.log(f"  - Madis Invest: {len(self.analyses_data['madis_invest'])} analyses")
            self.log(f"  - Sika Finance: {len(self.analyses_data['sika_finance'])} analyses")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur génération JSON: {str(e)}")
            return False
    
    def generate_report(self):
        """Générer rapport de scraping"""
        self.log("\n" + "="*60)
        self.log("📊 RAPPORT DE SCRAPING ANALYSES BRVM")
        self.log("="*60)
        self.log(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.log("")
        self.log("Sources scrapées:")
        self.log("  1. Madis Invest (4 catégories)")
        self.log("  2. Sika Finance (4 catégories)")
        self.log("")
        self.log(f"Analyses collectées: {len(self.analyses_data['madis_invest']) + len(self.analyses_data['sika_finance'])}")
        self.log("")
        self.log("Fichier généré: brvm_analyses.json")
        self.log("Log: " + self.log_file)
        self.log("="*60 + "\n")
    
    def run(self):
        """Exécuter le scraper"""
        self.log("\n" + "="*60)
        self.log("🚀 SCRAPER ANALYSES BRVM")
        self.log("="*60)
        
        # Scraper les 2 sources
        self.scrape_madis_invest()
        self.scrape_sika_finance()
        
        # Générer JSON
        json_ok = self.generate_json()
        
        # Rapport final
        self.generate_report()
        
        if json_ok:
            self.log("✅ Scraping terminé avec succès!")
        else:
            self.log("⚠️ Scraping avec erreurs - Vérifier logs")
        
        return json_ok

if __name__ == "__main__":
    scraper = BRVMAnalysesScraper()
    success = scraper.run()
    
    print("\n" + "="*60)
    print("📊 RÉSUMÉ SCRAPING ANALYSES")
    print("="*60)
    if success:
        print("✅ Scraping réussi!")
        print(f"📄 Fichier: brvm_analyses.json")
        print(f"📝 Log: scraper_analyses_{datetime.now().strftime('%Y-%m-%d')}.log")
    else:
        print("⚠️ Erreurs de scraping - Voir logs")
    print("="*60)

