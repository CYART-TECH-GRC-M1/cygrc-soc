from app.database.database import Base, engine
from app.models import Alert, Case, UEBAAnomaly

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.alerts import router as alerts_router
from app.api.v1.cases import router as cases_router
from app.api.v1.ueba import router as ueba_router
from app.database.database import Base, SessionLocal, engine
from app.models import Alert, Case, UEBAAnomaly


from app.services.wazuh_service import import_new_wazuh_alerts
from app.services.case_service import create_case_from_alert

def initialize_database():
    Base.metadata.create_all(bind=engine)


async def wazuh_polling_loop():
    while True:
        db = SessionLocal()

        try:
            new_alerts = await asyncio.to_thread(
                import_new_wazuh_alerts,
                db,
            )

            if new_alerts:
                print(
                    f"[WAZUH] Imported {len(new_alerts)} new alert(s)"
                )

                for alert in new_alerts:
                    case = create_case_from_alert(db, alert)

                    if case:
                        print(
                            f"[CASE] Auto-created case #{case.id} "
                            f"from alert #{alert.id} "
                            f"({alert.severity})"
                        )

        except Exception as error:
            print(
                f"[WAZUH] Import error: {error}"
            )

        finally:
            db.close()

        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()

    polling_task = asyncio.create_task(
        wazuh_polling_loop()
    )

    yield

    polling_task.cancel()

    try:
        await polling_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="CyGRC SOC API",
    version="0.1.0",
    description="Cyber Defense Operations SOC backend",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    alerts_router,
    prefix="/api/v1",
)

app.include_router(
    cases_router,
    prefix="/api/v1",
)

app.include_router(
    ueba_router,
    prefix="/api/v1",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "cygrc-soc-api",
    }