#!/usr/bin/env python3
"""
BRVM PROPOSITIONS D'INVESTISSEMENT PAR SECTEUR
Génère des propositions d'investissement groupées par secteur
Basé sur les analyses Madis Invest + Sika Finance
"""

import os
import json
import re
from datetime import datetime
from collections import defaultdict

class PropositionsInvestissement:
    def __init__(self):
        self.analyses_file = 'brvm_analyses.json'
        self.mapping_file = 'brvm_actions_mapping.json'
        self.output_file = 'brvm_propositions.json'
        self.log_file = f'propositions_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        self.propositions = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'heure': datetime.now().strftime('%H:%M:%S'),
            'propositions': [],
            'synthese': {
                'secteurs_a_acheter': 0,
                'secteurs_a_vendre': 0,
                'secteurs_a_conserver': 0,
                'actions_impactees_total': 0
            }
        }
        
        # Mapping SECTEUR → Codes actions BRVM
        self.secteurs_mapping = {
            "Bancaire": ["BICC", "BICB", "NSBC", "BOAB", "ECOC"],
            "Télécom": ["SNTS", "ORGT", "CIEC"],
            "Services": ["ORAC", "SEMC", "SMBC"],
            "Industrie": ["ETIT", "FTSC", "TRACTAFRIC"],
            "Distribution": ["SOMDIAG", "CABC"],
            "Énergie": ["PALM", "NAPHTA"],
            "Transports": ["TRAPHIC"],
            "Immobilier": ["SICAF"],
            "Agro-alimentaire": ["TRITURAF", "SUCAF"],
            "Chimie": [],
        }
        
        # Mots-clés pour détecter secteurs
        self.secteur_keywords = {
            "Bancaire": ["bancaire", "banque", "crédit", "finance", "financier"],
            "Télécom": ["télécom", "téléphone", "mobile", "internet", "réseau"],
            "Services": ["service", "hôtel", "tourisme", "restauration"],
            "Industrie": ["industrie", "usine", "manufacture", "production"],
            "Distribution": ["distribution", "commerce", "vente", "détail"],
            "Énergie": ["énergie", "pétrole", "gaz", "électricité"],
            "Transports": ["transport", "logistique", "fret"],
            "Immobilier": ["immobilier", "immeubles", "construction", "bâtiment"],
            "Agro-alimentaire": ["agriculture", "agro", "alimentaire", "sucre", "huile"],
            "Chimie": ["chimie", "chimique", "pharmacie"],
        }
        
        self.actions_mapping = self.load_mapping()
        self.analyses_data = self.load_analyses()
    
    def log(self, msg):
        """Logger messages"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def load_mapping(self):
        """Charger mapping actions"""
        try:
            if os.path.exists(self.mapping_file):
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.log(f"⚠️ Erreur chargement mapping: {e}")
        return {}
    
    def load_analyses(self):
        """Charger analyses brutes"""
        try:
            if os.path.exists(self.analyses_file):
                with open(self.analyses_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.log(f"⚠️ Erreur chargement analyses: {e}")
        return {'madis_invest': [], 'sika_finance': []}
    
    def detect_secteur(self, text):
        """Détecter secteur dans le texte"""
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Chercher les mots-clés de secteur
        for secteur, keywords in self.secteur_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return secteur
        
        return None
    
    def analyze_sentiment(self, text):
        """Analyser le sentiment (hausse/baisse/neutre)"""
        if not text:
            return "NEUTRE"
        
        text_lower = text.lower()
        
        keywords_hausse = [
            'hausse', 'croissance', 'augment', 'positif', 'fort',
            'opportunit', 'achetez', 'acheter', 'surperform', 'outperform',
            'investir', 'potentiel', 'amélioration', 'progrès', 'bonne', 'bon',
            'hausse', 'essor', 'dynamique', 'favorable'
        ]
        
        keywords_baisse = [
            'baisse', 'chut', 'négatif', 'faible', 'vendez',
            'vendre', 'underperform', 'underweight', 'caution', 'prudenc',
            'risque', 'décli', 'détérior', 'mauvais', 'diffic', 'problèm',
            'crise', 'baisse', 'recul', 'défavorable'
        ]
        
        hausse_count = sum(1 for kw in keywords_hausse if kw in text_lower)
        baisse_count = sum(1 for kw in keywords_baisse if kw in text_lower)
        
        if hausse_count > baisse_count:
            return "HAUSSE"
        elif baisse_count > hausse_count:
            return "BAISSE"
        else:
            return "NEUTRE"
    
    def calculate_confiance(self, sentiment, source):
        """Calculer niveau de confiance"""
        # FORTE pour Madis (plus fiable), MOYENNE pour Sika
        source_score = 2 if "Madis" in source else 1.5
        
        sentiment_score = {
            "HAUSSE": 2,
            "BAISSE": 2,
            "NEUTRE": 1
        }.get(sentiment, 1)
        
        score = source_score * sentiment_score
        
        if score >= 3.5:
            return "FORTE"
        elif score >= 2.5:
            return "MOYENNE"
        else:
            return "FAIBLE"
    
    def get_recommandation(self, sentiment):
        """Déduire recommandation du sentiment"""
        if sentiment == "HAUSSE":
            return "ACHETER"
        elif sentiment == "BAISSE":
            return "VENDRE"
        else:
            return "CONSERVER"
    
    def generer_propositions(self):
        """Générer propositions par secteur"""
        self.log("\n🤖 Génération des propositions par secteur...")
        
        # Combiner toutes les analyses
        all_analyses = self.analyses_data.get('madis_invest', []) + \
                       self.analyses_data.get('sika_finance', [])
        
        # Grouper par secteur
        propositions_par_secteur = defaultdict(list)
        
        for analyse in all_analyses:
            try:
                title = analyse.get('title', '')
                description = analyse.get('description', '')
                source = analyse.get('source', 'Inconnu')
                
                # Analyser le secteur
                secteur = self.detect_secteur(title + " " + description)
                if not secteur:
                    continue
                
                # Analyser le sentiment
                sentiment = self.analyze_sentiment(title + " " + description)
                
                # Récupérer les codes du secteur
                codes = self.secteurs_mapping.get(secteur, [])
                if not codes:
                    self.log(f"  ⚠️ Pas de codes pour secteur: {secteur}")
                    continue
                
                # Générer la proposition
                recommandation = self.get_recommandation(sentiment)
                confiance = self.calculate_confiance(sentiment, source)
                
                proposition = {
                    'secteur': secteur,
                    'actions': codes[:5],  # Top 5 du secteur
                    'recommandation': recommandation,
                    'confiance': confiance,
                    'sentiment': sentiment,
                    'raison': title[:100],
                    'source': source,
                    'description': description[:150],
                    'horizon': self.deduce_horizon(sentiment),
                    'risque': self.deduce_risque(sentiment)
                }
                
                propositions_par_secteur[secteur].append(proposition)
                
                self.log(f"  ✅ {recommandation}: Secteur {secteur} ({confiance})")
                
            except Exception as e:
                self.log(f"  ⚠️ Erreur proposition: {str(e)}")
        
        # Créer une proposition unique par secteur (consolidée)
        for secteur, props in propositions_par_secteur.items():
            if props:
                # Prendre la première proposition du secteur (la plus récente)
                prop = props[0]
                self.propositions['propositions'].append(prop)
        
        # Trier par confiance (FORTE > MOYENNE > FAIBLE)
        self.propositions['propositions'].sort(
            key=lambda x: {'FORTE': 3, 'MOYENNE': 2, 'FAIBLE': 1}.get(x['confiance'], 0),
            reverse=True
        )
        
        self.log(f"\n✅ {len(self.propositions['propositions'])} propositions générées")
    
    def deduce_horizon(self, sentiment):
        """Déduire horizon de temps"""
        # Sentiment positif = court terme (réaction rapide du marché)
        # Sentiment négatif = moyen terme (correction progressive)
        if sentiment == "HAUSSE":
            return "court_terme"  # 1-3 mois
        elif sentiment == "BAISSE":
            return "moyen_terme"  # 3-6 mois
        else:
            return "moyen_terme"
    
    def deduce_risque(self, sentiment):
        """Déduire niveau de risque"""
        if sentiment == "HAUSSE":
            return "FAIBLE"
        elif sentiment == "BAISSE":
            return "ÉLEVÉ"
        else:
            return "MOYEN"
    
    def generer_synthese(self):
        """Générer synthèse des propositions"""
        self.log("\n📊 Génération synthèse...")
        
        achats = [p for p in self.propositions['propositions'] if p['recommandation'] == 'ACHETER']
        ventes = [p for p in self.propositions['propositions'] if p['recommandation'] == 'VENDRE']
        conservations = [p for p in self.propositions['propositions'] if p['recommandation'] == 'CONSERVER']
        
        # Compter les actions impactées
        actions_total = len(set(
            code for prop in self.propositions['propositions']
            for code in prop.get('actions', [])
        ))
        
        self.propositions['synthese'] = {
            'secteurs_a_acheter': len(achats),
            'secteurs_a_vendre': len(ventes),
            'secteurs_a_conserver': len(conservations),
            'actions_impactees_total': actions_total,
            'total_propositions': len(self.propositions['propositions'])
        }
        
        self.log(f"  📊 Synthèse: {len(achats)} achats, {len(ventes)} ventes, {len(conservations)} conservations")
        self.log(f"  🎯 {actions_total} actions impactées au total")
    
    def save_propositions(self):
        """Sauvegarder propositions en JSON"""
        self.log("\n💾 Sauvegarde JSON...")
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.propositions, f, ensure_ascii=False, indent=2)
            
            self.log(f"✅ JSON sauvegardé: {self.output_file}")
            return True
        except Exception as e:
            self.log(f"❌ Erreur JSON: {str(e)}")
            return False
    
    def run(self):
        """Exécuter le générateur"""
        self.log("\n" + "="*60)
        self.log("🤖 GÉNÉRATEUR DE PROPOSITIONS PAR SECTEUR")
        self.log("="*60)
        self.log(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        self.generer_propositions()
        self.generer_synthese()
        self.save_propositions()
        
        self.log("\n" + "="*60)
        self.log("✅ Propositions générées!")
        self.log("="*60 + "\n")

if __name__ == "__main__":
    generator = PropositionsInvestissement()
    generator.run()
