"""Amorçage idempotent et strictement synthétique de la recette publique."""

import asyncio
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import get_settings
from models.database import ActeMedical, ClinicSetting, RoleEnum, Utilisateur


BRANDING = {
    "nom_clinique": "Cabinet Dentaire Démonstration",
    "logo_url": None,
    "couleur_primaire": "#0EA5A4",
    "couleur_secondaire": "#0F172A",
    "contenu_landing": {
        "titre": "Votre sourire, notre priorité",
        "sous_titre": "Demandez un créneau en ligne pour une consultation dentaire.",
        "services_mis_en_avant": [],
        "adresse": "Adresse de démonstration — données de test",
        "ville": "Tunis",
        "telephone": "",
        "whatsapp": "",
        "email": "",
        "instagram": "",
        "facebook": "",
        "tiktok": "",
        "photo_hero_url": None,
        "description_longue": "Instance de recette avec données strictement synthétiques.",
        "horaires": "Lundi au samedi, sur rendez-vous",
    },
}

PRACTITIONERS = [
    {
        "email": "dr.aymen.demo@example.test",
        "nom": "Mansour",
        "prenom": "Aymen",
        "role": RoleEnum.MEDECIN.value,
        "specialite": "Chirurgie dentaire",
        "agenda_color": "#0EA5A4",
    },
    {
        "email": "dr.salma.demo@example.test",
        "nom": "Ben Ali",
        "prenom": "Salma",
        "role": RoleEnum.ORTHODONTISTE.value,
        "specialite": "Orthodontie",
        "agenda_color": "#6366F1",
    },
]

ACTES = [
    ("Consultation dentaire", "Consultation", 30, "Bilan et orientation personnalisée."),
    ("Détartrage", "Prévention", 45, "Nettoyage professionnel et prévention."),
    ("Blanchiment dentaire", "Esthétique", 60, "Évaluation et séance esthétique."),
    ("Consultation orthodontique", "Orthodontie", 45, "Évaluation orthodontique et plan de traitement."),
]


async def main() -> None:
    settings = get_settings()
    clinic_id = int(settings.instance_clinic_id or 1)
    engine = create_async_engine(settings.database_url, future=True)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with sessions() as db:
            branding = await db.scalar(
                select(ClinicSetting).where(
                    ClinicSetting.clinic_id == clinic_id,
                    ClinicSetting.key == "branding",
                )
            )
            if branding is None:
                db.add(
                    ClinicSetting(
                        clinic_id=clinic_id,
                        key="branding",
                        value=BRANDING,
                        description="Branding synthétique de la recette Railway",
                    )
                )

            for practitioner in PRACTITIONERS:
                existing = await db.scalar(
                    select(Utilisateur).where(Utilisateur.email == practitioner["email"])
                )
                if existing is None:
                    db.add(
                        Utilisateur(
                            clinic_id=clinic_id,
                            email=practitioner["email"],
                            hashed_password="!public-demo-profile-not-login-enabled!",
                            nom=practitioner["nom"],
                            prenom=practitioner["prenom"],
                            role=practitioner["role"],
                            specialite=practitioner["specialite"],
                            agenda_color=practitioner["agenda_color"],
                            is_active=True,
                        )
                    )

            for name, category, duration, description in ACTES:
                existing = await db.scalar(
                    select(ActeMedical).where(
                        ActeMedical.clinic_id == clinic_id,
                        ActeMedical.nom == name,
                    )
                )
                if existing is None:
                    db.add(
                        ActeMedical(
                            clinic_id=clinic_id,
                            nom=name,
                            categorie=category,
                            duree_minutes=duration,
                            prix_base=Decimal("0.000"),
                            description=description,
                            is_active=True,
                        )
                    )
            await db.commit()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
