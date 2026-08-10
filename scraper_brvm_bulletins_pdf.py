#!/usr/bin/env python3
"""
BRVM BULLETINS PDF SCRAPER
Télécharge et extrait le PDF du bulletin du jour depuis /fr/bulletins-officiels-de-la-cote
"""

import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re

class BRVMBulletinsPDFScraper:
    def __init__(self):
        self.output_dir = os.path.expanduser('~/brvm_reports')
        self.data_file = 'brvm_bulletin_pdf_data.json'
        self.log_file = f'scraper_bulletins_pdf_{datetime.now().strftime("%Y-%m-%d")}.log'
        self.date_today = datetime.now().strftime('%Y-%m-%d')
        self.date_french = datetime.now().strftime('%d %B %Y').replace('August', 'août').lower()
        
        self.pdf_data = {
            'date': self.date_today,
            'heure': datetime.now().strftime('%H:%M:%S'),
            'source': 'https://www.brvm.org/fr/bulletins-officiels-de-la-cote',
            'pdf_url': None,
            'pdf_telecharged': False,
            'pdf_path': None,
            'timestamp': datetime.now().isoformat()
        }
        
        os.makedirs(self.output_dir, exist_ok=True)
        
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
    
    def trouver_pdf_du_jour(self):
        """Trouver le lien du PDF du jour"""
        self.log("\n📍 Recherche du PDF du jour...")
        
        url = 'https://www.brvm.org/fr/bulletins-officiels-de-la-cote'
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                self.log(f"✅ Page accessible (status 200)")
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Chercher les liens "Télécharger"
                liens = soup.find_all('a', string=re.compile(r'Télécharger', re.IGNORECASE))
                
                self.log(f"📄 {len(liens)} liens de téléchargement trouvés")
                
                # Chercher le PDF du jour
                for lien in liens:
                    parent = lien.find_parent(['div', 'p', 'li'])
                    if parent:
                        text = parent.get_text()
                        
                        # Vérifier si c'est le PDF du jour
                        if 'aujourd' in text.lower() or self.date_today.replace('-', '') in text:
                            pdf_url = lien.get('href')
                            if pdf_url:
                                if not pdf_url.startswith('http'):
                                    pdf_url = 'https://www.brvm.org' + pdf_url
                                
                                self.log(f"✅ PDF du jour trouvé!")
                                self.log(f"   URL: {pdf_url}")
                                self.pdf_data['pdf_url'] = pdf_url
                                return pdf_url
                
                # Si pas trouvé par date, prendre le premier (le plus récent)
                if liens:
                    for lien in liens:
                        pdf_url = lien.get('href')
                        if pdf_url:
                            if not pdf_url.startswith('http'):
                                pdf_url = 'https://www.brvm.org' + pdf_url
                            
                            self.log(f"⚠️ PDF le plus récent utilisé (date exacte non trouvée)")
                            self.log(f"   URL: {pdf_url}")
                            self.pdf_data['pdf_url'] = pdf_url
                            return pdf_url
                
                self.log(f"❌ Aucun PDF trouvé")
                return None
            else:
                self.log(f"⚠️ Page inaccessible (status {response.status_code})")
                return None
                
        except Exception as e:
            self.log(f"❌ Erreur recherche PDF: {str(e)}")
            return None
    
    def telecharger_pdf(self, pdf_url):
        """Télécharger le PDF"""
        self.log("\n📥 Téléchargement du PDF...")
        
        try:
            response = requests.get(pdf_url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                # Nom du fichier
                filename = f"boc_{self.date_today}.pdf"
                filepath = os.path.join(self.output_dir, filename)
                
                # Sauvegarder
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                self.log(f"✅ PDF téléchargé avec succès!")
                self.log(f"   Taille: {len(response.content) / 1024:.1f} KB")
                self.log(f"   Chemin: {filepath}")
                
                self.pdf_data['pdf_telecharged'] = True
                self.pdf_data['pdf_path'] = filepath
                return filepath
            else:
                self.log(f"⚠️ Erreur téléchargement (status {response.status_code})")
                return None
                
        except Exception as e:
            self.log(f"❌ Erreur téléchargement: {str(e)}")
            return None
    
    def generate_json(self):
        """Générer le fichier JSON"""
        self.log("\n💾 Génération JSON...")
        
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.pdf_data, f, ensure_ascii=False, indent=2)
            
            self.log(f"✅ JSON généré: {self.data_file}")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur génération JSON: {str(e)}")
            return False
    
    def generate_report(self):
        """Générer rapport final"""
        self.log("\n" + "="*60)
        self.log("📊 RAPPORT DE SCRAPING BULLETINS PDF BRVM")
        self.log("="*60)
        self.log(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.log("")
        self.log("Source scrapée:")
        self.log("  https://www.brvm.org/fr/bulletins-officiels-de-la-cote")
        self.log("")
        self.log(f"PDF trouvé: {'✅ Oui' if self.pdf_data['pdf_url'] else '❌ Non'}")
        self.log(f"PDF téléchargé: {'✅ Oui' if self.pdf_data['pdf_telecharged'] else '❌ Non'}")
        if self.pdf_data['pdf_path']:
            self.log(f"Chemin local: {self.pdf_data['pdf_path']}")
        self.log("")
        self.log("Fichiers générés:")
        self.log(f"  - {self.data_file} (métadonnées PDF)")
        self.log(f"  - {self.log_file} (log détaillé)")
        if self.pdf_data['pdf_telecharged']:
            self.log(f"  - boc_{self.date_today}.pdf (bulletin officiel)")
        self.log("="*60 + "\n")
    
    def run(self):
        """Exécuter le scraper"""
        self.log("\n" + "="*60)
        self.log("🚀 SCRAPER BULLETINS PDF BRVM")
        self.log("="*60)
        
        # Trouver PDF du jour
        pdf_url = self.trouver_pdf_du_jour()
        
        if pdf_url:
            # Télécharger
            self.telecharger_pdf(pdf_url)
        
        # Générer JSON
        self.generate_json()
        
        # Rapport final
        self.generate_report()
        
        self.log("✅ Scraper terminé!")

if __name__ == "__main__":
    scraper = BRVMBulletinsPDFScraper()
    scraper.run()
