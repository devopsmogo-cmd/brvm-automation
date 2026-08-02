#!/usr/bin/env python3
"""
BRVM BULLETINS DE COTE SCRAPER
Récupère les bulletins officiels de la cote depuis:
https://www.brvm.org/fr/bulletins-officiels-de-la-cote

Données extraites:
- Prix de clôture
- Volumes échangés
- Variations quotidiennes
- Synthèse marché (indice, volume total)
- Données temps réel post-clôture (15h30)

Génère: brvm_cote_du_jour.json avec données officielles fraîches
"""

import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import time
import re

class BRVMBulletinsCoteScraper:
    def __init__(self):
        self.base_url = "https://www.brvm.org/fr/bulletins-officiels-de-la-cote"
        self.output_file = 'brvm_cote_du_jour.json'
        self.log_file = f'scraper_cote_{datetime.now().strftime("%Y-%m-%d")}.log'
        self.cote_data = {}
        
        # Headers pour éviter blocage
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'fr-FR,fr;q=0.9',
            'Referer': 'https://www.brvm.org/'
        }
    
    def log(self, msg):
        """Logger les opérations"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def scrape_bulletins_page(self):
        """
        Scraper la page des bulletins de cote
        https://www.brvm.org/fr/bulletins-officiels-de-la-cote
        """
        self.log("\n📍 Scraping bulletins de cote BRVM.ORG...")
        
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                self.log(f"✅ Page accessible (status {response.status_code})")
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Chercher les bulletins les plus récents
                # BRVM affiche généralement les bulletins dans des sections
                
                # Chercher liens vers PDF/documents des bulletins
                links = soup.find_all('a')
                bulletin_links = []
                
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text().strip()
                    
                    # Chercher liens contenant "bulletin", "cote", "officiel"
                    if any(keyword in text.lower() for keyword in ['bulletin', 'cote', 'officiel', 'cotation']):
                        if any(ext in href.lower() for ext in ['.pdf', 'bulletin']):
                            bulletin_links.append({
                                'titre': text,
                                'url': href,
                                'date': self.extract_date_from_text(text)
                            })
                
                self.log(f"📊 {len(bulletin_links)} bulletins trouvés")
                
                for i, bulletin in enumerate(bulletin_links[:5], 1):
                    self.log(f"  {i}. {bulletin['titre']} - {bulletin['date']}")
                
                # Chercher aussi les tableaux avec données de cote
                tables = soup.find_all('table')
                self.log(f"📊 {len(tables)} tableaux trouvés")
                
                self.parse_cote_tables(tables)
                
            else:
                self.log(f"⚠️ Page inaccessible (status {response.status_code})")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Erreur connexion: {str(e)}")
            return False
        except Exception as e:
            self.log(f"❌ Erreur parsing: {str(e)}")
            return False
        
        return True
    
    def extract_date_from_text(self, text):
        """Extraire date du texte du bulletin"""
        # Chercher pattern dates (JJ/MM/YYYY)
        match = re.search(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', text)
        if match:
            return f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
        return "Date inconnue"
    
    def parse_cote_tables(self, tables):
        """Parser les tableaux de données de cote"""
        self.log("\n📋 Parsing tableaux de cote...")
        
        actions_found = {}
        
        for table_idx, table in enumerate(tables[:10]):  # Parser premiers 10 tableaux
            rows = table.find_all('tr')
            
            if len(rows) > 2:  # Au moins un header + 1 data
                # Vérifier si c'est un tableau de cote (contient CODE, COURS, VARIATION)
                header_text = ' '.join([col.get_text().strip().upper() for col in rows[0].find_all(['th', 'td'])])
                
                is_cote_table = any(kw in header_text for kw in ['CODE', 'COURS', 'PRIX', 'VARIATION', 'VOLUME'])
                
                if is_cote_table:
                    self.log(f"  ✅ Tableau {table_idx + 1}: Tableau de cote identifié")
                    
                    # Parser lignes de données
                    for row in rows[1:]:
                        cols = row.find_all(['td', 'th'])
                        if len(cols) >= 3:
                            try:
                                # Extraction données génériques
                                col_texts = [col.get_text().strip() for col in cols]
                                
                                # Chercher code action (généralement première colonne)
                                code = col_texts[0] if col_texts else ''
                                
                                if code and len(code) <= 10 and code.isalpha():
                                    # Extraction prix/variation
                                    prix_str = col_texts[1] if len(col_texts) > 1 else '0'
                                    variation_str = col_texts[2] if len(col_texts) > 2 else '0%'
                                    volume_str = col_texts[3] if len(col_texts) > 3 else '0'
                                    
                                    # Nettoyer les valeurs
                                    try:
                                        prix = float(re.sub(r'[^\d.,]', '', prix_str.replace(' ', '')).replace(',', '.'))
                                        variation = float(re.sub(r'[^\d.,\-]', '', variation_str).replace(',', '.'))
                                        volume = re.sub(r'[^\d.,]', '', volume_str.replace(' ', ''))
                                        
                                        actions_found[code] = {
                                            'cours': prix,
                                            'variation': variation,
                                            'volume': volume
                                        }
                                        
                                        self.log(f"    └─ {code}: {prix} FCFA ({variation:+.2f}%) - Volume: {volume}")
                                        
                                    except ValueError:
                                        pass
                                        
                            except Exception as e:
                                pass
        
        if actions_found:
            self.log(f"\n✅ {len(actions_found)} actions extraites avec succès")
            self.cote_data['actions'] = actions_found
            self.cote_data['nb_actions'] = len(actions_found)
        else:
            self.log("⚠️ Aucune données de cote trouvée dans les tableaux")
    
    def scrape_synthese_marche(self):
        """
        Scraper les informations synthèse du marché
        Indice composite, volume total, etc.
        """
        self.log("\n📊 Extraction synthèse marché...")
        
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Chercher sections de synthèse
            synthese_data = {}
            
            # Chercher texte contenant "Indice", "Volume", etc.
            all_text = soup.get_text()
            
            # Extraction indice (chercher "Indice: XXXXX" ou "Composite: XXXXX")
            indice_match = re.search(r'[Ii]ndice[^0-9]*(\d+[.,]\d+)', all_text)
            if indice_match:
                indice = float(indice_match.group(1).replace(',', '.'))
                synthese_data['indice_composite'] = indice
                self.log(f"  ├─ Indice: {indice}")
            
            # Extraction volume total (chercher "Volume: X Mds" ou "XXXX Mds FCFA")
            volume_match = re.search(r'[Vv]olume[^0-9]*(\d+[.,]\d+)\s*(?:Mds|milliards)', all_text)
            if volume_match:
                volume = float(volume_match.group(1).replace(',', '.'))
                synthese_data['volume_total_mds'] = volume
                self.log(f"  ├─ Volume total: {volume} Mds FCFA")
            
            # Extraction hausse/baisse
            hausse_match = re.search(r'[Hh]ausse[^0-9]*(\d+)', all_text)
            if hausse_match:
                hausse = int(hausse_match.group(1))
                synthese_data['actions_hausse'] = hausse
                self.log(f"  ├─ Actions en hausse: {hausse}")
            
            baisse_match = re.search(r'[Bb]aisse[^0-9]*(\d+)', all_text)
            if baisse_match:
                baisse = int(baisse_match.group(1))
                synthese_data['actions_baisse'] = baisse
                self.log(f"  ├─ Actions en baisse: {baisse}")
            
            self.cote_data['synthese'] = synthese_data
            
        except Exception as e:
            self.log(f"⚠️ Erreur extraction synthèse: {str(e)}")
    
    def extract_pdf_data(self):
        """
        Optionnel: Extraire données depuis PDF des bulletins
        (Nécessite librairie PyPDF2)
        """
        self.log("\n📄 Extraction données PDF (si disponibles)...")
        self.log("  ℹ️ Note: Scraping PDF en développement")
        self.log("  └─ Pour maintenant, utilise données HTML")
    
    def generate_json_output(self):
        """Générer le fichier JSON de sortie"""
        self.log("\n💾 Génération JSON de sortie...")
        
        output = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'heure': datetime.now().strftime('%H:%M:%S'),
            'source': 'BRVM.ORG - Bulletins Officiels de la Cote',
            'url': self.base_url,
            'cote_data': self.cote_data,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            
            self.log(f"✅ JSON généré: {self.output_file}")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur génération JSON: {str(e)}")
            return False
    
    def generate_report(self):
        """Générer rapport de scraping"""
        self.log("\n" + "="*60)
        self.log("📊 RAPPORT DE SCRAPING BULLETINS DE COTE")
        self.log("="*60)
        self.log(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.log("")
        self.log("Source: https://www.brvm.org/fr/bulletins-officiels-de-la-cote")
        self.log("Données extraites:")
        self.log(f"  ├─ Actions trouvées: {self.cote_data.get('nb_actions', 0)}")
        self.log(f"  ├─ Indice: {self.cote_data.get('synthese', {}).get('indice_composite', 'N/A')}")
        self.log(f"  ├─ Volume: {self.cote_data.get('synthese', {}).get('volume_total_mds', 'N/A')} Mds")
        self.log("")
        self.log("Fichiers générés:")
        self.log(f"  ├─ {self.output_file} (données de cote)")
        self.log(f"  └─ {self.log_file} (log détaillé)")
        self.log("="*60 + "\n")
    
    def run(self):
        """Exécuter le scraper complet"""
        self.log("\n" + "="*60)
        self.log("🚀 SCRAPER BULLETINS DE COTE BRVM")
        self.log("="*60)
        
        # Scraper bulletins
        bulletins_ok = self.scrape_bulletins_page()
        time.sleep(2)  # Délai respectueux
        
        # Scraper synthèse
        if bulletins_ok:
            self.scrape_synthese_marche()
        
        # Générer JSON
        json_ok = self.generate_json_output()
        
        # Rapport final
        self.generate_report()
        
        return bulletins_ok and json_ok

if __name__ == "__main__":
    scraper = BRVMBulletinsCoteScraper()
    success = scraper.run()
    
    print("\n" + "="*60)
    print("✅ RÉSUMÉ" if success else "⚠️ RÉSUMÉ")
    print("="*60)
    if success:
        print("✅ Scraping terminé avec succès!")
        print(f"📊 Fichier: brvm_cote_du_jour.json")
        print(f"📝 Log: {scraper.log_file}")
    else:
        print("⚠️ Scraping avec erreurs - Vérifier logs")
    print("="*60)

