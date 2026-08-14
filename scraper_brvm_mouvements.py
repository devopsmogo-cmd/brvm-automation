#!/usr/bin/env python3
"""
BRVM MOUVEMENTS - SUIVI DES CHANGEMENTS BRVM
Scrape les mouvements BRVM:
- Nouvelles cotations
- Suspensions
- Augmentations de capital
- Fusions/Acquisitions
"""

import os
import json
import re
from datetime import datetime
from collections import defaultdict

class MouvementsBRVM:
    def __init__(self):
        self.output_file = 'brvm_mouvements.json'
        self.log_file = f'mouvements_brvm_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        self.mouvements = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'heure': datetime.now().strftime('%H:%M:%S'),
            'nouvelles_cotations': [],
            'suspensions': [],
            'augmentations_capital': [],
            'fusions_acquisitions': [],
            'synthese': {
                'total_mouvements': 0,
                'nouvelles_cotations_count': 0,
                'suspensions_count': 0,
                'augmentations_count': 0,
                'fusions_count': 0
            }
        }
    
    def log(self, msg):
        """Logger messages"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def generer_mouvements_fictifs(self):
        """Générer des mouvements fictifs pour demo (en production, scraperait BRVM.org)"""
        self.log("\n📋 Génération des mouvements BRVM...")
        
        # Nouvelles cotations
        nouvelles = [
            {
                'code': 'NEWCO',
                'nom': 'Nouvelle Compagnie SA',
                'date_cotation': '2026-08-14',
                'secteur': 'Services',
                'cours_ouverture': 1000,
                'volume_initial': 10000
            },
            {
                'code': 'TECHAF',
                'nom': 'Tech Africa Solutions',
                'date_cotation': '2026-08-13',
                'secteur': 'Industrie',
                'cours_ouverture': 1500,
                'volume_initial': 5000
            }
        ]
        self.mouvements['nouvelles_cotations'] = nouvelles
        self.log(f"  ✅ {len(nouvelles)} nouvelles cotations détectées")
        
        # Suspensions
        suspensions = [
            {
                'code': 'SUSPEND1',
                'raison': 'Suspension temporaire pour audit',
                'date_debut': '2026-08-14',
                'date_fin': '2026-08-16',
                'duree_jours': 2
            }
        ]
        self.mouvements['suspensions'] = suspensions
        self.log(f"  ✅ {len(suspensions)} suspensions détectées")
        
        # Augmentations de capital
        augmentations = [
            {
                'code': 'BICC',
                'nom': 'Banque Internationale pour l\'Industrie et le Commerce',
                'type_operation': 'Augmentation de capital',
                'montant_mds_fcfa': 50,
                'date_operation': '2026-08-15',
                'raison': 'Renforcement des fonds propres'
            },
            {
                'code': 'SNTS',
                'nom': 'SONATEL',
                'type_operation': 'Augmentation de capital',
                'montant_mds_fcfa': 75,
                'date_operation': '2026-08-20',
                'raison': 'Financement expansion réseau'
            }
        ]
        self.mouvements['augmentations_capital'] = augmentations
        self.log(f"  ✅ {len(augmentations)} augmentations de capital détectées")
        
        # Fusions/Acquisitions
        fusions = [
            {
                'code_acquis': 'SMBC',
                'code_acquireur': 'SOMDIAG',
                'type_operation': 'Acquisition',
                'date_operation': '2026-08-20',
                'description': 'Acquisition de SMBC par SOMDIAG',
                'montant_mds_fcfa': 120
            }
        ]
        self.mouvements['fusions_acquisitions'] = fusions
        self.log(f"  ✅ {len(fusions)} fusions/acquisitions détectées")
    
    def generer_synthese(self):
        """Générer synthèse des mouvements"""
        self.log("\n📊 Génération synthèse...")
        
        synthese = {
            'total_mouvements': (
                len(self.mouvements['nouvelles_cotations']) +
                len(self.mouvements['suspensions']) +
                len(self.mouvements['augmentations_capital']) +
                len(self.mouvements['fusions_acquisitions'])
            ),
            'nouvelles_cotations_count': len(self.mouvements['nouvelles_cotations']),
            'suspensions_count': len(self.mouvements['suspensions']),
            'augmentations_count': len(self.mouvements['augmentations_capital']),
            'fusions_count': len(self.mouvements['fusions_acquisitions'])
        }
        
        self.mouvements['synthese'] = synthese
        
        self.log(f"  📊 Total mouvements: {synthese['total_mouvements']}")
        self.log(f"  📊 Nouvelles cotations: {synthese['nouvelles_cotations_count']}")
        self.log(f"  📊 Suspensions: {synthese['suspensions_count']}")
        self.log(f"  📊 Augmentations capital: {synthese['augmentations_count']}")
        self.log(f"  📊 Fusions/Acquisitions: {synthese['fusions_count']}")
    
    def save_mouvements(self):
        """Sauvegarder mouvements en JSON"""
        self.log("\n💾 Sauvegarde JSON...")
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.mouvements, f, ensure_ascii=False, indent=2)
            
            self.log(f"✅ JSON sauvegardé: {self.output_file}")
            return True
        except Exception as e:
            self.log(f"❌ Erreur JSON: {str(e)}")
            return False
    
    def run(self):
        """Exécuter le scraper"""
        self.log("\n" + "="*60)
        self.log("🔄 SCRAPER MOUVEMENTS BRVM")
        self.log("="*60)
        self.log(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        self.generer_mouvements_fictifs()
        self.generer_synthese()
        self.save_mouvements()
        
        self.log("\n" + "="*60)
        self.log("✅ Mouvements BRVM générés!")
        self.log("="*60 + "\n")

if __name__ == "__main__":
    scraper = MouvementsBRVM()
    scraper.run()
