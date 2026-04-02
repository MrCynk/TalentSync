from fastapi import APIRouter, BackgroundTasks
from schemas import ApplyRequest
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import httpx
import uuid
import json
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

router = APIRouter()
llm = ChatGroq(
    temperature=0.3, 
    model_name="llama3-70b-8192", 
    groq_api_key=api_key
)

# Stockage en mémoire (à remplacer par Redis ou DB en production)
applications_store: dict = {}

cv_prompt = ChatPromptTemplate.from_template("""
Génère un CV JSON compact pour : {nom} {prenom}
Compétences: {competences} | Expériences: {experiences} | Formations: {formations}
Retourne UNIQUEMENT le JSON du CV.
""")

lettre_prompt = ChatPromptTemplate.from_template("""
Rédige une lettre de motivation JSON pour {nom} {prenom} postulant à {titre} chez {entreprise}.
Profil: {competences} | Offre: {description}
Retourne UNIQUEMENT: {{"objet": "...", "corps": "...", "score_adequation": 0-100}}
""")


async def run_application_agent(application_id: str, request: ApplyRequest):
    """Agent de candidature automatique — s'exécute en arrière-plan."""
    p = request.profil
    o = request.offre
    applications_store[application_id]["statut"] = "en_cours"

    try:
        # Étape 1 : Générer le CV
        applications_store[application_id]["etape"] = "generation_cv"
        cv_chain = cv_prompt | llm
        cv_result = cv_chain.invoke({
            "nom": p.nom, "prenom": p.prenom,
            "competences": ", ".join(p.competences),
            "experiences": str([e.dict() for e in p.experiences]),
            "formations": str([f.dict() for f in p.formations]),
        })

        # Étape 2 : Générer la lettre de motivation
        applications_store[application_id]["etape"] = "generation_lettre"
        lettre_chain = lettre_prompt | llm
        lettre_result = lettre_chain.invoke({
            "nom": p.nom, "prenom": p.prenom,
            "titre": o.titre, "entreprise": o.entreprise,
            "competences": ", ".join(p.competences),
            "description": o.description,
        })

        # Étape 3 : Simuler la soumission (à remplacer par scraping/API réelle)
        applications_store[application_id]["etape"] = "soumission"
        cv_data = json.loads(cv_result.content) if cv_result.content.strip().startswith("{") else {"raw": cv_result.content}
        lettre_data = json.loads(lettre_result.content) if lettre_result.content.strip().startswith("{") else {"raw": lettre_result.content}

        # Mise à jour finale
        applications_store[application_id].update({
            "statut": "soumise",
            "etape": "terminee",
            "cv_genere": cv_data,
            "lettre_generee": lettre_data,
            "soumise_le": datetime.utcnow().isoformat(),
        })

        # Callback Laravel si webhook fourni
        if request.webhook_url:
            async with httpx.AsyncClient() as client:
                await client.post(request.webhook_url, json={
                    "application_id": application_id,
                    "statut": "soumise",
                    "offre": o.dict(),
                    "cv": cv_data,
                    "lettre": lettre_data,
                }, timeout=10)

    except Exception as e:
        applications_store[application_id].update({
            "statut": "erreur",
            "erreur": str(e),
        })
        if request.webhook_url:
            async with httpx.AsyncClient() as client:
                await client.post(request.webhook_url, json={
                    "application_id": application_id,
                    "statut": "erreur",
                    "erreur": str(e),
                }, timeout=10)


@router.post("")
async def auto_apply(request: ApplyRequest, background_tasks: BackgroundTasks):
    application_id = str(uuid.uuid4())
    applications_store[application_id] = {
        "application_id": application_id,
        "statut": "en_attente",
        "etape": "initialisation",
        "offre": request.offre.dict(),
        "candidat": f"{request.profil.prenom} {request.profil.nom}",
        "cree_le": datetime.utcnow().isoformat(),
    }

    background_tasks.add_task(run_application_agent, application_id, request)

    return {
        "success": True,
        "application_id": application_id,
        "message": "Candidature lancée en arrière-plan.",
        "statut_url": f"/application-status/{application_id}",
    }


def get_store():
    return applications_store
