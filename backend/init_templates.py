import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path
import uuid

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

TEMPLATES_JAF = [
    {
        "template_id": f"tpl_{uuid.uuid4().hex[:8]}",
        "name": "Garde alternée",
        "description": "Demande de résidence alternée des enfants",
        "type": "jaf",
        "category": "Résidence des enfants",
        "faits_template": """Les parties se sont mariées le [DATE] et ont eu [NOMBRE] enfant(s) : [PRÉNOMS ET DATES DE NAISSANCE].

Depuis le [DATE], les parties vivent séparément. Durant cette période de séparation, les enfants ont résidé [PRÉCISER LA SITUATION ACTUELLE].

Le demandeur dispose d'un logement adapté à l'accueil des enfants, situé [ADRESSE], comprenant [DESCRIPTION DU LOGEMENT].

Les deux parents exercent une activité professionnelle compatible avec la garde des enfants : [PRÉCISER LES HORAIRES ET MÉTIERS].

Les enfants sont scolarisés à [ÉTABLISSEMENT], situé à équidistance des domiciles parentaux.

Les deux parents entretiennent de bonnes relations avec les enfants et sont impliqués dans leur éducation.""",
        "demandes_template": """PAR CES MOTIFS,

Plaise au Tribunal :

1. FIXER la résidence des enfants en alternance au domicile de chacun des parents selon le rythme suivant : [une semaine sur deux / autre rythme à préciser] ;

2. DIRE que les alternances se dérouleront du [JOUR] soir après l'école au [JOUR] soir après l'école ;

3. FIXER les modalités de partage des vacances scolaires par moitié, les années paires/impaires ;

4. RAPPELER que chaque parent conserve l'exercice conjoint de l'autorité parentale ;

5. CONDAMNER le défendeur aux entiers dépens.

SOUS RÉSERVE DE TOUS DROITS""",
        "articles_pertinents": ["371", "371-1", "373-2", "373-2-1"]
    },
    {
        "template_id": f"tpl_{uuid.uuid4().hex[:8]}",
        "name": "Pension alimentaire",
        "description": "Fixation ou révision de pension alimentaire",
        "type": "jaf",
        "category": "Obligation alimentaire",
        "faits_template": """Les parties ont eu [NOMBRE] enfant(s) ensemble : [PRÉNOMS ET DATES DE NAISSANCE].

Par [JUGEMENT/ORDONNANCE] du [DATE], la résidence habituelle des enfants a été fixée chez [PARENT] et une pension alimentaire de [MONTANT] euros par enfant et par mois a été fixée à la charge de [PARENT DÉBITEUR].

Depuis lors, la situation financière [du demandeur / du défendeur] a substantiellement évolué :
[DÉTAILLER LES CHANGEMENTS : perte d'emploi, nouvelle situation professionnelle, charges supplémentaires, etc.]

Les ressources actuelles du demandeur s'élèvent à [MONTANT] euros nets mensuels.
Les ressources du défendeur s'élèvent à [MONTANT] euros nets mensuels.

Les besoins des enfants se sont accrus avec [ÂGE / SCOLARITÉ / ACTIVITÉS EXTRA-SCOLAIRES].""",
        "demandes_template": """PAR CES MOTIFS,

Plaise au Tribunal :

1. FIXER la contribution à l'entretien et l'éducation des enfants à la somme de [MONTANT] euros par enfant et par mois ;

2. DIRE que cette pension sera versée mensuellement et d'avance entre les mains de [PARENT CRÉANCIER] ;

3. DIRE que cette pension sera indexée annuellement selon l'indice INSEE ;

4. DIRE que cette pension produira intérêts au taux légal à compter de la présente décision ;

5. CONDAMNER le défendeur aux entiers dépens.

SOUS RÉSERVE DE TOUS DROITS""",
        "articles_pertinents": ["371-2", "373-2"]
    },
    {
        "template_id": f"tpl_{uuid.uuid4().hex[:8]}",
        "name": "Autorité parentale exclusive",
        "description": "Demande de retrait de l'autorité parentale",
        "type": "jaf",
        "category": "Autorité parentale",
        "faits_template": """Les parties sont les parents de [PRÉNOM], né(e) le [DATE].

L'autorité parentale est actuellement exercée conjointement par les deux parents.

Toutefois, depuis [DATE/PÉRIODE], le défendeur a adopté un comportement incompatible avec l'exercice de l'autorité parentale, caractérisé par :

- [FAIT GRAVE N°1 : négligence, violence, manquement aux obligations, désintérêt, etc.]
- [FAIT GRAVE N°2]
- [FAIT GRAVE N°3]

[Si applicable : Des signalements ont été effectués auprès de [SERVICES SOCIAUX / POLICE / etc.] les [DATES].]

Ces comportements mettent en danger la sécurité, la santé et la moralité de l'enfant au sens de l'article 371 du Code Civil.

L'intérêt supérieur de l'enfant commande que l'autorité parentale soit exercée exclusivement par le demandeur.""",
        "demandes_template": """PAR CES MOTIFS,

Plaise au Tribunal :

1. RETIRER au défendeur l'exercice de l'autorité parentale sur l'enfant [PRÉNOM] ;

2. CONFIER l'exercice exclusif de l'autorité parentale au demandeur ;

3. FIXER la résidence habituelle de l'enfant au domicile du demandeur ;

4. [Si applicable] SUSPENDRE / LIMITER le droit de visite et d'hébergement du défendeur ;

5. CONDAMNER le défendeur aux entiers dépens.

SOUS RÉSERVE DE TOUS DROITS""",
        "articles_pertinents": ["371", "371-1", "373-2"]
    },
    {
        "template_id": f"tpl_{uuid.uuid4().hex[:8]}",
        "name": "Divorce pour faute",
        "description": "Demande de divorce aux torts exclusifs du conjoint",
        "type": "jaf",
        "category": "Divorce",
        "faits_template": """Les époux se sont mariés le [DATE] à [LIEU].

[Si enfants : De cette union sont nés [NOMBRE] enfant(s) : [PRÉNOMS ET DATES DE NAISSANCE].]

Depuis [DATE/PÉRIODE], le défendeur a commis des faits constitutifs de violations graves et renouvelées des devoirs et obligations du mariage, rendant intolérable le maintien de la vie commune :

1. MANQUEMENT AU DEVOIR DE RESPECT :
[Détailler : violences verbales, humiliations, comportement dégradant, etc.]

2. MANQUEMENT AU DEVOIR DE FIDÉLITÉ :
[Si applicable : relations extra-conjugales avérées, preuves, dates, etc.]

3. MANQUEMENT AU DEVOIR D'ASSISTANCE :
[Si applicable : abandon du domicile conjugal, refus de contribuer aux charges du mariage, etc.]

Ces faits sont établis par [PRÉCISER LES PREUVES : témoignages, constats d'huissier, SMS, courriels, main courante, certificats médicaux, etc.].

Le demandeur a été contraint de quitter le domicile conjugal le [DATE] / vit séparé depuis le [DATE].""",
        "demandes_template": """PAR CES MOTIFS,

Plaise au Tribunal :

1. PRONONCER le divorce des époux aux torts exclusifs du défendeur ;

2. DIRE que les fautes du défendeur ont rendu intolérable le maintien de la vie commune ;

3. [Si applicable] ATTRIBUER la jouissance du domicile conjugal au demandeur ;

4. [Si applicable] FIXER une prestation compensatoire en faveur du demandeur ;

5. [Si enfants] STATUER sur les modalités d'exercice de l'autorité parentale et la résidence des enfants ;

6. CONDAMNER le défendeur aux entiers dépens ;

7. CONDAMNER le défendeur à verser au demandeur la somme de [MONTANT] euros au titre de l'article 700 du Code de Procédure Civile.

SOUS RÉSERVE DE TOUS DROITS""",
        "articles_pertinents": ["212", "213", "242"]
    },
    {
        "template_id": f"tpl_{uuid.uuid4().hex[:8]}",
        "name": "Prestation compensatoire",
        "description": "Demande de prestation compensatoire",
        "type": "jaf",
        "category": "Divorce",
        "faits_template": """Les époux se sont mariés le [DATE], soit [DURÉE] années de mariage.

Le divorce crée une disparité importante dans les conditions de vie respectives des époux.

SITUATION DU DEMANDEUR :
- Âge : [ÂGE] ans
- Situation professionnelle : [EMPLOI / SANS EMPLOI / RETRAITE]
- Revenus mensuels : [MONTANT] euros nets
- Patrimoine : [DÉCRIRE]
- État de santé : [PRÉCISER si pertinent]
- Qualification professionnelle : [NIVEAU]

SITUATION DU DÉFENDEUR :
- Âge : [ÂGE] ans  
- Situation professionnelle : [EMPLOI]
- Revenus mensuels : [MONTANT] euros nets
- Patrimoine : [DÉCRIRE]
- Capacité contributive élevée

Pendant le mariage, le demandeur [a sacrifié sa carrière / s'est consacré au foyer / a soutenu la carrière du conjoint], ce qui explique l'écart actuel de revenus.

La disparité créée par la rupture du mariage justifie l'allocation d'une prestation compensatoire.""",
        "demandes_template": """PAR CES MOTIFS,

Plaise au Tribunal :

1. CONDAMNER le défendeur à verser au demandeur une prestation compensatoire d'un montant de [MONTANT] euros ;

2. DIRE que cette prestation sera versée [sous forme de capital / sous forme de rente / en nature par attribution de biens] ;

3. [Si capital] FIXER les modalités de versement : [versement unique / échelonné sur X années] ;

4. DIRE que cette prestation est destinée à compenser la disparité créée par la rupture du mariage dans les conditions de vie respectives ;

5. CONDAMNER le défendeur aux entiers dépens.

SOUS RÉSERVE DE TOUS DROITS""",
        "articles_pertinents": ["270"]
    }
]

TEMPLATES_PENAL = [
    {
        "template_id": f"tpl_{uuid.uuid4().hex[:8]}",
        "name": "Défense - Vol simple",
        "description": "Conclusions en défense pour des faits de vol",
        "type": "penal",
        "category": "Défense",
        "faits_template": """Le prévenu est poursuivi du chef de vol, faits prévus et réprimés par l'article 311-1 du Code Pénal.

Il lui est reproché d'avoir, le [DATE], à [LIEU], soustrait frauduleusement [DESCRIPTION DES BIENS] appartenant à [VICTIME].

LE CONTEXTE DES FAITS :
[Exposer la version du prévenu : contexte social, situation personnelle, circonstances atténuantes]

LE PRÉVENU CONTESTE / RECONNAÎT partiellement les faits :
[Développer : absence d'intention frauduleuse, erreur, contrainte, etc.]

ÉLÉMENTS À DÉCHARGE :
- [ÉLÉMENT 1 : absence de preuves matérielles, témoignages contradictoires, etc.]
- [ÉLÉMENT 2 : situation de détresse, nécessité, etc.]
- [ÉLÉMENT 3]

SITUATION PERSONNELLE DU PRÉVENU :
- Âge : [ÂGE] ans, [situation familiale]
- Profession : [PRÉCISER]
- Casier judiciaire : [vierge / quasi-vierge / antécédents]
- Situation sociale stable / précaire
- [Si applicable : prise de conscience, indemnisation de la victime, démarches de réinsertion]""",
        "demandes_template": """PAR CES MOTIFS,

Plaise à la Juridiction :

À TITRE PRINCIPAL :
1. RELAXER purement et simplement le prévenu des fins de la poursuite ;

À TITRE SUBSIDIAIRE :
2. ÉCARTER toute peine d'emprisonnement ;
3. PRONONCER une peine d'amende [ou de travail d'intérêt général] ;
4. ASSORTIR toute peine éventuellement prononcée du sursis [simple / avec mise à l'épreuve] ;

À TITRE INFINIMENT SUBSIDIAIRE :
5. FAIRE application des circonstances atténuantes ;
6. TENIR COMPTE de la situation personnelle du prévenu, de [ses efforts de réinsertion / son absence d'antécédents / sa prise de conscience] ;

SOUS RÉSERVE DE TOUS DROITS""",
        "articles_pertinents": ["311-1", "121-3"]
    },
    {
        "template_id": f"tpl_{uuid.uuid4().hex[:8]}",
        "name": "Défense - Violences",
        "description": "Conclusions en défense pour violences",
        "type": "penal",
        "category": "Défense",
        "faits_template": """Le prévenu est poursuivi du chef de violences volontaires [ayant entraîné une ITT de X jours / sans ITT].

Il lui est reproché d'avoir, le [DATE], à [LIEU], porté des coups à [VICTIME], lui causant [DESCRIPTION DES BLESSURES].

LE CONTEXTE DES FAITS :
Les faits se sont déroulés dans le contexte suivant : [PRÉCISER : dispute, provocation, consommation d'alcool, etc.]

LA VERSION DU PRÉVENU :
[Exposer : légitime défense, provocation grave de la victime, geste involontaire, exagération des faits, etc.]

Le prévenu [CONTESTE formellement / RECONNAÎT] avoir porté des coups mais soutient que :
- [ARGUMENT 1 : il a agi en légitime défense]
- [ARGUMENT 2 : il a été gravement provoqué]
- [ARGUMENT 3 : les blessures sont minimes/exagérées]

ÉLÉMENTS À DÉCHARGE :
- Certificats médicaux du prévenu attestant [de blessures / de son propre état]
- Témoignages corroborant la version du prévenu
- [Absence d'antécédents judiciaires]

SITUATION PERSONNELLE :
- Le prévenu exprime [ses regrets / conteste toute violence disproportionnée]
- Situation familiale et professionnelle stable
- Aucun antécédent de violence""",
        "demandes_template": """PAR CES MOTIFS,

Plaise à la Juridiction :

À TITRE PRINCIPAL :
1. DIRE ET JUGER que les faits se sont déroulés dans un contexte de légitime défense ;
2. RELAXER purement et simplement le prévenu des fins de la poursuite ;

À TITRE SUBSIDIAIRE :
3. DIRE que le prévenu a été gravement provoqué par la victime ;
4. RETENIR les circonstances atténuantes ;
5. ÉCARTER toute peine d'emprisonnement ;
6. PRONONCER une peine d'amende mesurée assortie du sursis ;

À TITRE INFINIMENT SUBSIDIAIRE :
7. PRONONCER une peine d'emprisonnement avec sursis [simple / avec mise à l'épreuve] ;

SOUS RÉSERVE DE TOUS DROITS""",
        "articles_pertinents": ["122-5", "121-3"]
    },
    {
        "template_id": f"tpl_{uuid.uuid4().hex[:8]}",
        "name": "Partie civile - Vol avec préjudice",
        "description": "Constitution de partie civile pour vol",
        "type": "penal",
        "category": "Partie civile",
        "faits_template": """La partie civile a été victime d'un vol commis le [DATE] à [LIEU] par le prévenu.

LES FAITS :
Le [DATE], le prévenu a soustrait frauduleusement les biens suivants appartenant à la partie civile :
- [BIEN 1 : description et valeur]
- [BIEN 2 : description et valeur]
- [BIEN 3 : description et valeur]

Valeur totale des biens dérobés : [MONTANT] euros.

LES PRÉJUDICES SUBIS :

1. PRÉJUDICE MATÉRIEL :
- Valeur des biens volés non restitués : [MONTANT] euros
- Frais de remplacement : [MONTANT] euros
- [Autres frais : serrurerie, réparations, etc.] : [MONTANT] euros
TOTAL PRÉJUDICE MATÉRIEL : [MONTANT] euros

2. PRÉJUDICE MORAL :
La partie civile a subi un important préjudice moral du fait de :
- [Sentiment d'insécurité au domicile]
- [Atteinte à la vie privée]
- [Perte d'objets à valeur sentimentale]
- [Troubles psychologiques : angoisse, stress, troubles du sommeil]

Ce préjudice moral est évalué à [MONTANT] euros.

LA RESPONSABILITÉ DU PRÉVENU EST ÉTABLIE par [preuves, témoignages, aveux, etc.].""",
        "demandes_template": """PAR CES MOTIFS,

Plaise à la Juridiction :

SUR L'ACTION PUBLIQUE :
1. DÉCLARER le prévenu coupable des faits qui lui sont reprochés ;
2. Le CONDAMNER à une peine en rapport avec la gravité des faits ;

SUR L'ACTION CIVILE :
3. RECEVOIR la constitution de partie civile de [NOM] ;
4. DÉCLARER le prévenu entièrement responsable du préjudice subi ;
5. CONDAMNER le prévenu à payer à la partie civile les sommes suivantes :
   - [MONTANT] euros au titre du préjudice matériel
   - [MONTANT] euros au titre du préjudice moral
   SOIT UN TOTAL DE [MONTANT] euros
6. DIRE que ces sommes porteront intérêts au taux légal à compter de la décision ;
7. CONDAMNER le prévenu aux entiers dépens ;
8. CONDAMNER le prévenu à payer à la partie civile la somme de [MONTANT] euros au titre de l'article 475-1 du Code de Procédure Pénale.

SOUS RÉSERVE DE TOUS DROITS""",
        "articles_pertinents": ["311-1"]
    },
    {
        "template_id": f"tpl_{uuid.uuid4().hex[:8]}",
        "name": "Légitime défense",
        "description": "Moyen de défense - légitime défense",
        "type": "penal",
        "category": "Défense",
        "faits_template": """Le prévenu est poursuivi du chef de [QUALIFICATION : coups et blessures / violences / etc.].

Cependant, les faits reprochés ont été commis en état de LÉGITIME DÉFENSE, ce qui exclut toute responsabilité pénale en application de l'article 122-5 du Code Pénal.

LE CONTEXTE DES FAITS :
Le [DATE] à [LIEU], le prévenu a été confronté à une agression caractérisée de la part de [AGRESSEUR/VICTIME].

L'AGRESSION INITIALE :
[Décrire précisément l'attaque subie par le prévenu :
- Nature de l'agression : coups, menaces avec arme, tentative d'intrusion, etc.
- Caractère immédiat et injustifié de l'agression
- Danger réel et actuel pour le prévenu ou un tiers]

LA RIPOSTE DU PRÉVENU :
Face à cette agression injustifiée et dans l'impossibilité de se soustraire autrement au danger, le prévenu a riposté en [DÉCRIRE LA RIPOSTE].

Cette riposte était :
- NÉCESSAIRE : aucun autre moyen de se protéger
- IMMÉDIATE : concomitante à l'agression
- PROPORTIONNÉE : [argumenter sur la proportionnalité]

LES CONDITIONS DE LA LÉGITIME DÉFENSE SONT RÉUNIES :
1. Agression injustifiée et actuelle
2. Riposte nécessaire à la défense
3. Moyens employés proportionnés
4. Concomitance entre l'agression et la riposte

PREUVES :
- [Témoignages]
- [Certificats médicaux du prévenu]
- [Éléments matériels]""",
        "demandes_template": """PAR CES MOTIFS,

Plaise à la Juridiction :

1. DIRE ET JUGER que le prévenu a agi en état de légitime défense ;

2. CONSTATER que les conditions légales de la légitime défense prévues à l'article 122-5 du Code Pénal sont réunies :
   - Agression injustifiée et actuelle
   - Nécessité de la riposte
   - Proportionnalité des moyens employés
   - Concomitance de la riposte

3. DIRE que la légitime défense constitue un fait justificatif excluant toute responsabilité pénale ;

4. En conséquence, RELAXER purement et simplement le prévenu des fins de la poursuite ;

5. DÉBOUTER la partie civile éventuelle de toutes ses demandes ;

6. CONDAMNER [la partie civile / l'État] aux entiers dépens ;

7. CONDAMNER [la partie civile / l'État] à verser au prévenu la somme de [MONTANT] euros au titre de l'article 475-1 du Code de Procédure Pénale.

SOUS RÉSERVE DE TOUS DROITS""",
        "articles_pertinents": ["122-5"]
    }
]

async def init_templates():
    existing = await db.conclusion_templates.count_documents({})
    
    if existing > 0:
        print(f"{existing} templates déjà présents dans la base")
        return
    
    all_templates = TEMPLATES_JAF + TEMPLATES_PENAL
    
    if all_templates:
        await db.conclusion_templates.insert_many(all_templates)
        print(f"{len(all_templates)} templates insérés avec succès")
        print(f"  - {len(TEMPLATES_JAF)} templates JAF")
        print(f"  - {len(TEMPLATES_PENAL)} templates pénaux")
    
    await db.conclusion_templates.create_index("template_id", unique=True)
    await db.conclusion_templates.create_index("type")
    await db.conclusion_templates.create_index("category")
    
    print("Initialisation des templates terminée")

if __name__ == "__main__":
    asyncio.run(init_templates())