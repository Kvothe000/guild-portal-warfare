from database import SessionLocal, engine
import models
import crud_campaign
import schemas_campaign

def seed_campaign():
    db = SessionLocal()
    try:
        # Check if stages exist
        existing = db.query(models.CampaignStage).count()
        if existing > 0:
            print("Campaign already seeded.")
            return

        print("Seeding Campaign...")
        for i in range(1, 13):
            # Only use arguments defined in CampaignStageCreate and its base classes
            stage = schemas_campaign.CampaignStageCreate(
                stage_number=i,
                name=f"Fase {i}",
                difficulty_modifier=i,
                afk_xp_per_hour=10 + (i * 5),
                afk_gold_per_hour=20 + (i * 10)
            )
            crud_campaign.create_campaign_stage(db, stage)
        print("Campaign seeded successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_campaign()
