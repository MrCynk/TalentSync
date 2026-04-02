from pydantic import BaseModel
from typing import Optional, List


class Experience(BaseModel):
    poste: str
    entreprise: str
    duree: str
    description: Optional[str] = None


class Formation(BaseModel):
    diplome: str
    etablissement: str
    annee: str


class ProfilUtilisateur(BaseModel):
    nom: str
    prenom: str
    email: str
    telephone: Optional[str] = None
    localisation: Optional[str] = "Lomé, Togo"
    competences: List[str]
    langages: Optional[List[str]] = []
    experiences: Optional[List[Experience]] = []
    formations: Optional[List[Formation]] = []
    objectif_professionnel: Optional[str] = None


class OffreEmploi(BaseModel):
    titre: str
    entreprise: str
    description: str
    competences_requises: Optional[List[str]] = []
    url: Optional[str] = None


class CvRequest(BaseModel):
    profil: ProfilUtilisateur


class CoverLetterRequest(BaseModel):
    profil: ProfilUtilisateur
    offre: OffreEmploi


class MatchRequest(BaseModel):
    profil: ProfilUtilisateur
    offres: List[OffreEmploi]


class ApplyRequest(BaseModel):
    profil: ProfilUtilisateur
    offre: OffreEmploi
    webhook_url: Optional[str] = None  # URL Laravel pour callback async


class ApplicationStatusRequest(BaseModel):
    application_id: str
