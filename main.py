from fastapi import FastAPI, Request, Query
from fastapi.responses import RedirectResponse, PlainTextResponse
from google.cloud import firestore
from datetime import datetime
import time
import os

app = FastAPI()

# Path to service account file (same folder as main.py)
cred_path = os.path.join(os.path.dirname(__file__), "serviceAccount.json")
db = firestore.Client.from_service_account_json(cred_path)


@app.get("/")
async def root():
    return PlainTextResponse("Postback API running")


# CLICK TRACKING ENDPOINT
@app.get("/track")
async def track(request: Request, offer: str = "unknown"):
    click_id = f"clk_{int(time.time() * 1000)}"
    ip = request.client.host

    db.collection("clicks").add({
        "click_id": click_id,
        "offer_id": offer,
        "ip": ip,
        "created_at": datetime.utcnow()
    })

    # TODO: replace this with real offer URL from your client
    redirect_url = f"https://network.com/offer?id={offer}&sub1={click_id}"
    return RedirectResponse(url=redirect_url)


# POSTBACK ENDPOINT
@app.get("/postback")
async def postback(
    request: Request,
    click_id: str = Query(None),
    payout: float = 0.0,
    tid: str | None = None,
    status: str = "approved"
):
    if not click_id:
        return PlainTextResponse("Missing click_id", status_code=400)

    ip = request.client.host

    db.collection("conversions").add({
        "click_id": click_id,
        "transaction_id": tid,
        "payout": payout,
        "status": status,
        "ip": ip,
        "created_at": datetime.utcnow()
    })

    return PlainTextResponse("OK")
