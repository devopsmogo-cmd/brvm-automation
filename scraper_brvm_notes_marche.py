#!/usr/bin/env python3
"""
BRVM NOTES DE MARCHE - ANALYSE D'IMPACT MACRO
Analyse l'impact des événements macro sur BRVM
Génère des notes avec secteurs impactés et actions recommandées
"""

import os
import json
import re
from datetime import datetime

class NotesMarche:
    def __init__(self):
        self.analyses_file = 'brvm_analyses.json'
        self.mapping_file = 'brvm_actions_mapping.json'
        self.output_file = 'brvm_notes_marche.json'
        self.log_file = f'notes_marche_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        self.notes = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'heure': datetime.now().strftime('%H:%M:%S'),
            'notes': [],
            'synthese_globale': {
                'sentiment_overall': 'NEUTRE',
                'impact_overall': 'MOYEN',
                'risque_global': 'MOYEN',
                'notes_positives': 0,
                'notes_negatives': 0,
                'notes_neutres': 0
            }
        }
        
        # Mapping SECTEUR → Codes actions
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
        
        # Mots-clés pour analyser l'impact
        self.impact_keywords = {
            "FORT": ["croissance", "expansion", "hausse", "boost", "dynamique", "potentiel", "opportunité", "investissement"],
            "MOYEN": ["stable", "croissance modérée", "légère hausse", "amélioration"],
            "FAIBLE": ["légère baisse", "stagnation", "ralentissement"]
        }
        
        # Mots-clés pour détecter secteurs
        self.secteur_keywords = {
            "Bancaire": ["bancaire", "banque", "crédit", "finance", "financier", "services financiers"],
            "Télécom": ["télécom", "téléphone", "mobile", "internet", "réseau", "telecom"],
            "Services": ["service", "hôtel", "tourisme", "restauration"],
            "Industrie": ["industrie", "usine", "manufacture", "production", "manufacturière"],
            "Distribution": ["distribution", "commerce", "vente", "détail"],
            "Énergie": ["énergie", "pétrole", "gaz", "électricité", "énergétique"],
            "Transports": ["transport", "logistique", "fret"],
            "Immobilier": ["immobilier", "immeubles", "construction", "bâtiment"],
            "Agro-alimentaire": ["agriculture", "agro", "alimentaire", "sucre", "huile"],
            "Chimie": ["chimie", "chimique", "pharmacie"],
        }
        
        self.analyses_data = self.load_analyses()
    
    def log(self, msg):
        """Logger messages"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def load_analyses(self):
        """Charger analyses brutes"""
        try:
            if os.path.exists(self.analyses_file):
                with open(self.analyses_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.log(f"⚠️ Erreur chargement analyses: {e}")
        return {'madis_invest': [], 'sika_finance': []}
    
    def analyze_sentiment(self, text):
        """Analyser sentiment (POSITIF/NÉGATIF/NEUTRE)"""
        if not text:
            return "NEUTRE"
        
        text_lower = text.lower()
        
        keywords_positifs = [
            'hausse', 'croissance', 'augment', 'positif', 'fort', 'favorable',
            'opportunit', 'achetez', 'acheter', 'surperform', 'outperform',
            'investir', 'potentiel', 'amélioration', 'progrès', 'bonne', 'bon',
            'essor', 'dynamique', 'expansion', 'essor'
        ]
        
        keywords_negatifs = [
            'baisse', 'chut', 'négatif', 'faible', 'vendez', 'vendre',
            'underperform', 'underweight', 'caution', 'prudenc', 'risque',
            'décli', 'détérior', 'mauvais', 'diffic', 'problèm', 'crise',
            'recul', 'défavorable', 'pression'
        ]
        
        pos_count = sum(1 for kw in keywords_positifs if kw in text_lower)
        neg_count = sum(1 for kw in keywords_negatifs if kw in text_lower)
        
        if pos_count > neg_count:
            return "POSITIF"
        elif neg_count > pos_count:
            return "NÉGATIF"
        else:
            return "NEUTRE"
    
    def estimate_impact(self, text):
        """Estimer impact (FORT/MOYEN/FAIBLE)"""
        if not text:
            return "MOYEN"
        
        text_lower = text.lower()
        
        keywords_fort = [
            'croissance', 'expansion', 'hausse majeure', 'boost', 'dynamique forte',
            'potentiel énorme', 'opportunité majeure', 'impact significatif'
        ]
        
        keywords_faible = [
            'légère baisse', 'stagnation', 'ralentissement léger', 'stable'
        ]
        
        fort_count = sum(1 for kw in keywords_fort if kw in text_lower)
        faible_count = sum(1 for kw in keywords_faible if kw in text_lower)
        
        if fort_count > faible_count:
            return "FORT"
        elif faible_count > 0:
            return "FAIBLE"
        else:
            return "MOYEN"
    
    def estimate_probability(self, sentiment, source):
        """Estimer probabilité d'impact (0.0 à 1.0)"""
        # Madis Invest est plus fiable que Sika Finance
        source_score = 0.85 if "Madis" in source else 0.75
        
        sentiment_score = {
            "POSITIF": 0.85,
            "NÉGATIF": 0.80,
            "NEUTRE": 0.50
        }.get(sentiment, 0.50)
        
        return round(source_score * sentiment_score, 2)
    
    def identify_sectors(self, text):
        """Identifier secteurs affectés"""
        if not text:
            return []
        
        text_lower = text.lower()
        sectors = []
        
        for secteur, keywords in self.secteur_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if secteur not in sectors:
                        sectors.append(secteur)
                    break
        
        return sectors
    
    def get_actions_for_sectors(self, sectors):
        """Récupérer codes actions pour les secteurs"""
        actions = []
        for secteur in sectors:
            codes = self.secteurs_mapping.get(secteur, [])
            actions.extend(codes)
        return list(set(actions))  # Retirer les doublons
    
    def estimate_horizon(self, sentiment, impact):
        """Estimer horizon temporel"""
        if sentiment == "POSITIF" and impact == "FORT":
            return "court_terme"  # 1-3 mois
        elif sentiment == "NÉGATIF":
            return "moyen_terme"  # 3-6 mois
        else:
            return "moyen_terme"  # 3-6 mois par défaut
    
    def deduce_risk(self, sentiment):
        """Déduire niveau de risque"""
        if sentiment == "POSITIF":
            return "FAIBLE"
        elif sentiment == "NÉGATIF":
            return "ÉLEVÉ"
        else:
            return "MOYEN"
    
    def generer_notes(self):
        """Générer notes de marché"""
        self.log("\n📰 Génération des notes de marché...")
        
        # Combiner toutes les analyses
        all_analyses = self.analyses_data.get('madis_invest', []) + \
                       self.analyses_data.get('sika_finance', [])
        
        for analyse in all_analyses:
            try:
                title = analyse.get('title', '')
                description = analyse.get('description', '')
                source = analyse.get('source', 'Inconnu')
                
                if not title:
                    continue
                
                # Analyser sentiment
                sentiment = self.analyze_sentiment(title + " " + description)
                
                # Estimer impact
                impact = self.estimate_impact(title + " " + description)
                
                # Identifier secteurs
                secteurs = self.identify_sectors(title + " " + description)
                
                # Récupérer actions impactées
                actions = self.get_actions_for_sectors(secteurs)
                
                # Calculer probabilité
                probabilite = self.estimate_probability(sentiment, source)
                
                # Créer note
                note = {
                    'titre': title,
                    'source': source,
                    'sentiment': sentiment,
                    'impact_brvm': impact,
                    'secteurs_beneficiaires': secteurs if sentiment == "POSITIF" else [],
                    'secteurs_affectes_negativement': secteurs if sentiment == "NÉGATIF" else [],
                    'actions_impactees': actions,
                    'probabilite': probabilite,
                    'horizon': self.estimate_horizon(sentiment, impact),
                    'risque': self.deduce_risk(sentiment),
                    'description': description[:200],
                    'synthese': self.generer_synthese_note(title, sentiment, impact, secteurs)
                }
                
                self.notes['notes'].append(note)
                
                self.log(f"  ✅ {sentiment}: {title[:60]}... ({impact} impact)")
                
            except Exception as e:
                self.log(f"  ⚠️ Erreur note: {str(e)}")
        
        # Trier par impact (FORT > MOYEN > FAIBLE)
        self.notes['notes'].sort(
            key=lambda x: {'FORT': 3, 'MOYEN': 2, 'FAIBLE': 1}.get(x['impact_brvm'], 0),
            reverse=True
        )
        
        self.log(f"\n✅ {len(self.notes['notes'])} notes générées")
    
    def generer_synthese_note(self, titre, sentiment, impact, secteurs):
        """Générer synthèse une ligne pour chaque note"""
        if not secteurs:
            secteurs_text = "secteurs divers"
        else:
            secteurs_text = ", ".join(secteurs[:2])
            if len(secteurs) > 2:
                secteurs_text += f" et {len(secteurs)-2} autres"
        
        if sentiment == "POSITIF":
            return f"Impact positif pour {secteurs_text}. À suivre pour opportunités."
        elif sentiment == "NÉGATIF":
            return f"Impact négatif pour {secteurs_text}. À surveiller."
        else:
            return f"Impact neutre. Pas d'action immédiate requise."
    
    def generer_synthese_globale(self):
        """Générer synthèse globale"""
        self.log("\n📊 Génération synthèse globale...")
        
        positives = [n for n in self.notes['notes'] if n['sentiment'] == 'POSITIF']
        negatives = [n for n in self.notes['notes'] if n['sentiment'] == 'NÉGATIF']
        neutres = [n for n in self.notes['notes'] if n['sentiment'] == 'NEUTRE']
        
        # Sentiment global
        if len(positives) > len(negatives):
            sentiment_global = "POSITIF"
        elif len(negatives) > len(positives):
            sentiment_global = "NÉGATIF"
        else:
            sentiment_global = "NEUTRE"
        
        # Impact global
        forts = [n for n in self.notes['notes'] if n['impact_brvm'] == 'FORT']
        if len(forts) >= 2:
            impact_global = "FORT"
        elif len(forts) >= 1:
            impact_global = "MOYEN"
        else:
            impact_global = "FAIBLE"
        
        # Risque global
        if len(negatives) > 1:
            risque_global = "ÉLEVÉ"
        elif len(negatives) > 0:
            risque_global = "MOYEN"
        else:
            risque_global = "FAIBLE"
        
        self.notes['synthese_globale'] = {
            'sentiment_overall': sentiment_global,
            'impact_overall': impact_global,
            'risque_global': risque_global,
            'notes_positives': len(positives),
            'notes_negatives': len(negatives),
            'notes_neutres': len(neutres)
        }
        
        self.log(f"  📊 Sentiment global: {sentiment_global}")
        self.log(f"  📊 Impact global: {impact_global}")
        self.log(f"  📊 Risque global: {risque_global}")
    
    def save_notes(self):
        """Sauvegarder notes en JSON"""
        self.log("\n💾 Sauvegarde JSON...")
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, ensure_ascii=False, indent=2)
            
            self.log(f"✅ JSON sauvegardé: {self.output_file}")
            return True
        except Exception as e:
            self.log(f"❌ Erreur JSON: {str(e)}")
            return False
    
    def run(self):
        """Exécuter le générateur"""
        self.log("\n" + "="*60)
        self.log("📰 GÉNÉRATEUR DE NOTES DE MARCHE BRVM")
        self.log("="*60)
        self.log(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        self.generer_notes()
        self.generer_synthese_globale()
        self.save_notes()
        
        self.log("\n" + "="*60)
        self.log("✅ Notes de marché générées!")
        self.log("="*60 + "\n")

if __name__ == "__main__":
    generator = NotesMarche()
    generator.run()
