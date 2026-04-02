from fastapi import APIRouter
from schemas import CoverLetterRequest
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
Tu es un expert en rédaction professionnelle pour le marché tech africain.
Rédige une lettre de motivation percutante, personnalisée et professionnelle.

Candidat :
- Nom : {nom} {prenom}
- Compétences clés : {competences}
- Expériences : {experiences}
- Objectif : {objectif}

Offre ciblée :
- Poste : {titre_offre}
- Entreprise : {entreprise_offre}
- Description : {description_offre}
- Compétences requises : {competences_requises}

Contraintes :
- Ton professionnel mais dynamique
- Maximum 3 paragraphes
- Mettre en valeur l'adéquation profil/poste
- Adapté au contexte africain/togolais

Retourne UNIQUEMENT un JSON :
{{
  "objet": "Candidature au poste de ...",
  "corps": "...",
  "score_adequation": 0-100,
  "points_forts_mis_en_avant": [...]
}}
""")

@router.post("")
async def generate_cover_letter(request: CoverLetterRequest):
    p = request.profil
    o = request.offre
    chain = prompt | llm
    result = chain.invoke({
        "nom": p.nom,
        "prenom": p.prenom,
        "competences": ", ".join(p.competences),
        "experiences": str([e.dict() for e in p.experiences]),
        "objectif": p.objectif_professionnel or "",
        "titre_offre": o.titre,
        "entreprise_offre": o.entreprise,
        "description_offre": o.description,
        "competences_requises": ", ".join(o.competences_requises),
    })

    import json
    try:
        lettre = json.loads(result.content)
    except Exception:
        lettre = {"raw": result.content}

    return {"success": True, "lettre_motivation": lettre}
