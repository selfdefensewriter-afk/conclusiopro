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

ARTICLES_FAMILLE = [
    {
        "article_id": f"art_{uuid.uuid4().hex[:8]}",
        "numero": "371",
        "titre": "Autorité parentale - Principe",
        "contenu": "L'enfant, à tout âge, doit honneur et respect à ses père et mère. L'autorité parentale est un ensemble de droits et de devoirs ayant pour finalité l'intérêt de l'enfant. Elle appartient aux parents jusqu'à la majorité ou l'émancipation de l'enfant pour le protéger dans sa sécurité, sa santé et sa moralité, pour assurer son éducation et permettre son développement, dans le respect dû à sa personne.",
        "categorie": "famille"
    },
    {
        "article_id": f"art_{uuid.uuid4().hex[:8]}",
        "numero": "371-1",
        "titre": "Exercice en commun de l'autorité parentale",
        "contenu": "L'autorité parentale est exercée en commun par les deux parents. L'exercice de l'autorité parentale implique que les parents doivent prendre ensemble les décisions importantes concernant la santé, l'orientation scolaire, l'éducation religieuse et le changement de résidence de l'enfant.",
        "categorie": "famille"
    },
    {
        "article_id": f"art_{uuid.uuid4().hex[:8]}",
        "numero": "373-2",
        "titre": "Séparation des parents et autorité parentale",
        "contenu": "La séparation des parents est sans incidence sur les règles de dévolution de l'exercice de l'autorité parentale. Chacun des père et mère doit maintenir des relations personnelles avec l'enfant et respecter les liens de celui-ci avec l'autre parent.",
        "categorie": "famille"
    },
    {
        "article_id": f"art_{uuid.uuid4().hex[:8]}",
        "numero": "373-2-1",
        "titre": "Résidence de l'enfant",
        "contenu": "Si les parents ne parviennent pas à un accord sur le mode de résidence de l'enfant, le juge peut ordonner une résidence alternée ou fixer la résidence habituelle de l'enfant chez l'un des parents.",
        "categorie": "famille"
    },
    {
        "article_id": f"art_{uuid.uuid4().hex[:8]}",
        "numero": "212",
        "titre": "Devoirs des époux",
        "contenu": "Les époux se doivent mutuellement respect, fidélité, secours, assistance.",
        "categorie": "famille"
    },
    {
        "article_id": f"art_{uuid.uuid4().hex[:8]}",
        "numero": "213",
        "titre": "Communauté de vie",
        "contenu": "Les époux assurent ensemble la direction morale et matérielle de la famille. Ils pourvoient à l'éducation des enfants et préparent leur avenir.",
        "categorie": "famille"
    },
    {
        "article_id": f"art_{uuid.uuid4().hex[:8]}",
        "numero": "229",
        "titre": "Divorce pour altération définitive du lien conjugal",
        "contenu": "Le divorce peut être demandé par l'un des époux lorsque le lien conjugal est définitivement altéré. L'altération définitive du lien conjugal résulte de la cessation de la communauté de vie entre les époux, lorsqu'ils vivent séparés depuis au moins deux ans lors de l'assignation en divorce.",
        "categorie": "famille"
    },
    {
        "article_id": f"art_{uuid.uuid4().hex[:8]}",
        "numero": "242",
        "titre": "Divorce pour faute",
        "contenu": "Le divorce peut être demandé par l'un des époux lorsque des faits constitutifs d'une violation grave ou renouvelée des devoirs et obligations du mariage sont imputables à son conjoint et rendent intolérable le maintien de la vie commune.",
        "categorie": "famille"
    },
    {
        "article_id": f"art_{uuid.uuid4().hex[:8]}",
        "numero": "270",
        "titre": "Prestation compensatoire",
        "contenu": "Le divorce met fin au devoir de secours entre époux. L'un des époux peut être tenu de verser à l'autre une prestation destinée à compenser, autant qu'il est possible, la disparité que la rupture du mariage crée dans les conditions de vie respectives.",
        "categorie": "famille"
    },
    {
        "article_id": f"art_{uuid.uuid4().hex[:8]}",
        "numero": "371-2",
        "titre": "Obligation alimentaire envers les parents",
        "contenu": "L'enfant a une obligation d'aliments à l'égard de ses père et mère ou autres ascendants qui sont dans le besoin.",
        "categorie": "famille"
    }
]

ARTICLES_PENAL = [
    {
        "article_id": f"art_{uuid.uuid4().hex[:8]}",
        "numero": "121-1",
        "titre": "Principe de légalité",
        "contenu": "Nul n'est responsable pénalement que de son propre fait.",
        "categorie": "penal"
    },
    {
        "article_id": f"art_{uuid.uuid4().hex[:8]}",
        "numero": "121-3",
        "titre": "Absence d'intention",
        "contenu": "Il n'y a point de crime ou de délit sans intention de le commettre. Toutefois, lorsque la loi le prévoit, il y a délit en cas de mise en danger délibérée de la personne d'autrui.",
        "categorie": "penal"
    },
    {
        "article_id": f"art_{uuid.uuid4().hex[:8]}",
        "numero": "122-1",
        "titre": "Trouble psychique ou neuropsychique",
        "contenu": "N'est pas pénalement responsable la personne qui était atteinte, au moment des faits, d'un trouble psychique ou neuropsychique ayant aboli son discernement ou le contrôle de ses actes.",
        "categorie": "penal"
    },
    {
        "article_id": f"art_{uuid.uuid4().hex[:8]}",
        "numero": "122-5",
        "titre": "Légitime défense",
        "contenu": "N'est pas pénalement responsable la personne qui, devant une atteinte injustifiée envers elle-même ou autrui, accomplit, dans le même temps, un acte commandé par la nécessité de la légitime défense d'elle-même ou d'autrui, sauf s'il y a disproportion entre les moyens de défense employés et la gravité de l'atteinte.",
        "categorie": "penal"
    },
    {
        "article_id": f"art_{uuid.uuid4().hex[:8]}",
        "numero": "132-24",
        "titre": "Période de sûreté",
        "contenu": "La juridiction peut fixer une période de sûreté pendant laquelle le condamné ne peut bénéficier d'aucune des mesures énumérées à l'article 132-23.",
        "categorie": "penal"
    },
    {
        "article_id": f"art_{uuid.uuid4().hex[:8]}",
        "numero": "222-1",
        "titre": "Meurtre",
        "contenu": "Le fait de donner volontairement la mort à autrui constitue un meurtre. Il est puni de trente ans de réclusion criminelle.",
        "categorie": "penal"
    },
    {
        "article_id": f"art_{uuid.uuid4().hex[:8]}",
        "numero": "222-13",
        "titre": "Viol",
        "contenu": "Le viol est tout acte de pénétration sexuelle, de quelque nature qu'il soit, ou tout acte bucco-génital commis sur la personne d'autrui ou sur la personne de l'auteur par violence, contrainte, menace ou surprise. Le viol est puni de quinze ans de réclusion criminelle.",
        "categorie": "penal"
    },
    {
        "article_id": f"art_{uuid.uuid4().hex[:8]}",
        "numero": "311-1",
        "titre": "Vol",
        "contenu": "Le vol est la soustraction frauduleuse de la chose d'autrui. Il est puni de trois ans d'emprisonnement et de 45 000 euros d'amende.",
        "categorie": "penal"
    }
]

async def init_db():
    existing = await db.code_civil_articles.count_documents({})
    
    if existing > 0:
        print(f"{existing} articles déjà présents dans la base")
        return
    
    all_articles = ARTICLES_FAMILLE + ARTICLES_PENAL
    
    if all_articles:
        await db.code_civil_articles.insert_many(all_articles)
        print(f"{len(all_articles)} articles insérés avec succès")
    
    await db.code_civil_articles.create_index("numero")
    await db.code_civil_articles.create_index("categorie")
    await db.users.create_index("email", unique=True)
    await db.users.create_index("user_id", unique=True)
    await db.user_sessions.create_index("session_token", unique=True)
    await db.legal_conclusions.create_index("conclusion_id", unique=True)
    await db.legal_conclusions.create_index("user_id")
    
    print("Initialisation de la base de données terminée")

if __name__ == "__main__":
    asyncio.run(init_db())