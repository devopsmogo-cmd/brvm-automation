#!/usr/bin/env python3
"""
BRVM RECOMMANDATIONS GENERATOR
Transforme les actualités en recommandations d'investissement intelligentes
Basé sur: Madis Invest + Sika Finance + Analyse de sentiment
"""

import os
import json
import re
from datetime import datetime

class RecommandationsGenerator:
    def __init__(self):
        self.analyses_file = 'brvm_analyses.json'
        self.dividendes_file = 'brvm_dividendes_historique.json'
        self.mapping_file = 'brvm_actions_mapping.json'
        self.output_file = 'brvm_recommandations.json'
        self.log_file = f'recommandations_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        self.recommendations = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'heure': datetime.now().strftime('%H:%M:%S'),
            'recommandations': [],
            'synthese': []
        }
        
        # Mots-clés pour déterminer le sentiment
        self.keywords_hausse = [
            'hausse', 'croissance', 'hausse', 'augment', 'positif', 'positiv', 'fort',
            'opportunit', 'achetez', 'acheter', 'surperform', 'outperform', 'recommand',
            'investir', 'potentiel', 'amélioration', 'progrès', 'bonne', 'bon'
        ]
        
        self.keywords_baisse = [
            'baisse', 'baiss', 'chut', 'négatif', 'faible', 'faible', 'vendez',
            'vendre', 'underperform', 'underweight', 'caution', 'prudenc', 'risque',
            'décli', 'détérior', 'mauvais', 'diffic', 'problèm', 'crise'
        ]
        
        # Secteurs et codes actions
        self.action_names = self.load_mapping()
        self.dividendes = self.load_dividendes()
    
    def log(self, msg):
        """Logger"""
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
        except:
            pass
        return {}
    
    def load_dividendes(self):
        """Charger historique dividendes"""
        try:
            if os.path.exists(self.dividendes_file):
                with open(self.dividendes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def load_analyses(self):
        """Charger analyses brutes"""
        try:
            if os.path.exists(self.analyses_file):
                with open(self.analyses_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {'madis_invest': [], 'sika_finance': []}
    
    def extract_codes_from_text(self, text):
        """Extraire codes d'actions du texte (XXXX, XXX-N, etc.)"""
        codes = []
        # Chercher patterns type CODE, CODE-N, XXX, etc.
        pattern = r'\b([A-Z]{2,5}(?:-\d+)?)\b'
        matches = re.findall(pattern, text)
        
        # Filtrer les codes connus
        for match in matches:
            if match in self.action_names or match in self.dividendes:
                if match not in codes:
                    codes.append(match)
        
        return codes
    
    def analyze_sentiment(self, text):
        """Analyser le sentiment du texte (hausse/baisse/neutre)"""
        text_lower = text.lower()
        
        hausse_count = sum(1 for kw in self.keywords_hausse if kw in text_lower)
        baisse_count = sum(1 for kw in self.keywords_baisse if kw in text_lower)
        
        if hausse_count > baisse_count:
            return 'HAUSSE'
        elif baisse_count > hausse_count:
            return 'BAISSE'
        else:
            return 'NEUTRE'
    
    def get_dividend_yield(self, code):
        """Récupérer le rendement dividend d'une action"""
        if code in self.dividendes:
            data = self.dividendes[code].get('historique', {})
            if data:
                derniers = list(data.values())[-3:]  # 3 dernières années
                if derniers:
                    rendements = []
                    for year_data in derniers:
                        div = year_data.get('dividende', 0)
                        cours = year_data.get('cours_base', 1)
                        if cours > 0:
                            rendements.append((div / cours) * 100)
                    if rendements:
                        return sum(rendements) / len(rendements)
        return None
    
    def generate_recommendations(self):
        """Générer recommandations basées sur analyses"""
        self.log("\n🤖 Génération des recommandations...")
        
        analyses = self.load_analyses()
        all_analyses = analyses.get('madis_invest', []) + analyses.get('sika_finance', [])
        
        for analyse in all_analyses:
            try:
                title = analyse.get('title', '')
                description = analyse.get('description', '')
                source = analyse.get('source', 'Inconnu')
                category = analyse.get('category', '')
                url = analyse.get('url', '')
                
                # Analyser le sentiment
                full_text = f"{title} {description}"
                sentiment = self.analyze_sentiment(full_text)
                
                # Extraire codes d'actions mentionnées
                codes_mentions = self.extract_codes_from_text(full_text)
                
                # Si codes mentionnées, générer recommandations
                if codes_mentions:
                    for code in codes_mentions:
                        yield_div = self.get_dividend_yield(code)
                        
                        # Déterminer recommandation
                        if sentiment == 'HAUSSE':
                            recommandation = 'ACHETER'
                            confiance = 'FORTE' if yield_div and yield_div > 3 else 'MOYENNE'
                        elif sentiment == 'BAISSE':
                            recommandation = 'VENDRE'
                            confiance = 'FORTE'
                        else:
                            recommandation = 'CONSERVER'
                            confiance = 'FAIBLE'
                        
                        self.recommendations['recommandations'].append({
                            'code': code,
                            'nom': self.action_names.get(code, code),
                            'recommandation': recommandation,
                            'confiance': confiance,
                            'raison': title[:80],
                            'source': source,
                            'categorie': category,
                            'sentiment': sentiment,
                            'rendement_dividend': yield_div,
                            'actualite': title,
                            'description': description[:150],
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
                        
                        self.log(f"  ✅ {recommandation}: {code} ({confiance}) - {title[:60]}...")
                
            except Exception as e:
                self.log(f"  ⚠️ Erreur analyse: {str(e)}")
        
        # Déduplication et tri par confiance
        seen = set()
        unique_recs = []
        for rec in self.recommendations['recommandations']:
            key = (rec['code'], rec['recommandation'])
            if key not in seen:
                seen.add(key)
                unique_recs.append(rec)
        
        # Trier par: Confiance > Sentiment > Rendement
        self.recommendations['recommandations'] = sorted(
            unique_recs,
            key=lambda x: (
                {'FORTE': 3, 'MOYENNE': 2, 'FAIBLE': 1}.get(x['confiance'], 0),
                {'HAUSSE': 3, 'NEUTRE': 2, 'BAISSE': 1}.get(x['sentiment'], 0),
                x['rendement_dividend'] or 0
            ),
            reverse=True
        )
        
        self.log(f"\n✅ {len(self.recommendations['recommandations'])} recommandations générées")
    
    def generate_synthese(self):
        """Générer synthèse des recommandations par type"""
        self.log("\n📊 Génération synthèse...")
        
        achats = [r for r in self.recommendations['recommandations'] if r['recommandation'] == 'ACHETER']
        ventes = [r for r in self.recommendations['recommandations'] if r['recommandation'] == 'VENDRE']
        conservations = [r for r in self.recommendations['recommandations'] if r['recommandation'] == 'CONSERVER']
        
        # Top 3 achats
        if achats:
            self.recommendations['synthese'].append({
                'type': 'TOP_ACHATS',
                'titre': '🟢 Recommandations d\'Achat (Basées sur l\'actualité)',
                'actions': achats[:3]
            })
        
        # Top 3 ventes
        if ventes:
            self.recommendations['synthese'].append({
                'type': 'TOP_VENTES',
                'titre': '🔴 Recommandations de Vente (Prudence)',
                'actions': ventes[:3]
            })
        
        self.log(f"  ✅ Synthèse: {len(achats)} achats, {len(ventes)} ventes, {len(conservations)} conservations")
    
    def generate_json(self):
        """Sauvegarder recommandations en JSON"""
        self.log("\n💾 Génération JSON...")
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.recommendations, f, ensure_ascii=False, indent=2)
            
            self.log(f"✅ JSON sauvegardé: {self.output_file}")
            return True
        except Exception as e:
            self.log(f"❌ Erreur JSON: {str(e)}")
            return False
    
    def run(self):
        """Exécuter le générateur"""
        self.log("\n" + "="*60)
        self.log("🤖 GÉNÉRATEUR DE RECOMMANDATIONS BRVM")
        self.log("="*60)
        self.log(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        self.generate_recommendations()
        self.generate_synthese()
        self.generate_json()
        
        self.log("\n" + "="*60)
        self.log("✅ Recommandations générées!")
        self.log("="*60 + "\n")

if __name__ == "__main__":
    generator = RecommandationsGenerator()
    generator.run()
