from fastapi import APIRouter
from schemas import MatchRequest
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
import json

router = APIRouter()

llm = ChatGroq(
    temperature=0.3, 
    model_name="llama3-70b-8192", 
    groq_api_key=api_key
)

prompt = ChatPromptTemplate.from_template("""
Tu es un algorithme de matching RH intelligent.
Analyse la compatibilité entre ce profil et ces offres d'emploi.

Profil du candidat :
- Compétences : {competences}
- Langages : {langages}
- Expériences : {experiences}
- Objectif : {objectif}

Offres disponibles :
{offres}

Pour chaque offre, calcule un score de compatibilité (0-100) et explique pourquoi.
Trie par score décroissant.

Retourne UNIQUEMENT un JSON :
{{
  "offres_matchees": [
    {{
      "titre": "...",
      "entreprise": "...",
      "url": "...",
      "score_compatibilite": 85,
      "raisons": ["..."],
      "competences_manquantes": ["..."],
      "recommande_candidature_auto": true
    }}
  ],
  "profil_resume": "..."
}}

Note : recommande_candidature_auto = true si score >= 70
""")

@router.post("")
async def match_opportunities(request: MatchRequest):
    p = request.profil
    offres_str = json.dumps(
        [o.dict() for o in request.offres],
        ensure_ascii=False,
        indent=2
    )
    chain = prompt | llm
    result = chain.invoke({
        "competences": ", ".join(p.competences),
        "langages": ", ".join(p.langages),
        "experiences": str([e.dict() for e in p.experiences]),
        "objectif": p.objectif_professionnel or "",
        "offres": offres_str,
    })

    try:
        data = json.loads(result.content)
    except Exception:
        data = {"raw": result.content}

    return {"success": True, "matching": data}
