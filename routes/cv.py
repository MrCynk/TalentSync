from fastapi import APIRouter
from schemas import CvRequest
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
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

prompt = ChatPromptTemplate.from_template("""
Tu es un expert RH spécialisé dans le marché tech africain.
Génère un CV professionnel structuré en JSON pour le profil suivant.

Profil :
- Nom : {nom} {prenom}
- Email : {email}
- Téléphone : {telephone}
- Localisation : {localisation}
- Compétences : {competences}
- Langages : {langages}
- Expériences : {experiences}
- Formations : {formations}
- Objectif : {objectif}

Retourne UNIQUEMENT un JSON valide avec cette structure :
{{
  "nom_complet": "...",
  "contact": {{"email": "...", "telephone": "...", "localisation": "..."}},
  "objectif_professionnel": "...",
  "competences": [...],
  "langages_programmation": [...],
  "experiences": [{{"poste": "...", "entreprise": "...", "duree": "...", "description": "..."}}],
  "formations": [{{"diplome": "...", "etablissement": "...", "annee": "..."}}],
  "score_profil": 0-100
}}
""")

@router.post("")
async def generate_cv(request: CvRequest):
    p = request.profil
    chain = prompt | llm
    result = chain.invoke({
        "nom": p.nom,
        "prenom": p.prenom,
        "email": p.email,
        "telephone": p.telephone or "N/A",
        "localisation": p.localisation,
        "competences": ", ".join(p.competences),
        "langages": ", ".join(p.langages),
        "experiences": str([e.dict() for e in p.experiences]),
        "formations": str([f.dict() for f in p.formations]),
        "objectif": p.objectif_professionnel or "Cherche une opportunité dans le domaine tech",
    })

    import json
    try:
        cv_data = json.loads(result.content)
    except Exception:
        cv_data = {"raw": result.content}

    return {"success": True, "cv": cv_data}
