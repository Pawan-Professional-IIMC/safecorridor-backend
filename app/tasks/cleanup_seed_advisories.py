import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import SessionLocal
from app import models

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def cleanup_seed_advisories():
    db = SessionLocal()
    try:
        deleted = (
            db.query(models.Advisory)
            .filter(models.Advisory.source_name == "SafeCorridor Seed Data")
            .delete(synchronize_session=False)
        )
        db.commit()
        logger.info("Deleted %s seed advisories.", deleted)
    except Exception as exc:
        db.rollback()
        logger.error("Failed to cleanup seed advisories: %s", exc)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    cleanup_seed_advisories()
