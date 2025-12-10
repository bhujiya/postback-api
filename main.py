import os
import json
import time
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from google.cloud import firestore
from google.oauth2 import service_account

# Load Firestore credentials from Render environment variable
credentials_info = json.loads(os.environ["FIREBASE_CREDENTIALS"])
credentials = service_account.Credentials.from_service_account_info(credentials_info)

db = firestore.Client(
    credentials=credentials,
    project=credentials_info["project_id"]
)

app = FastAPI()

@app.get("/track")
async def track(request: Request, offer: str = "unknown"):
    click_id = f"clk_{int(time.time() * 1000)}"
    ip = request.client.host

    db.collection("clicks").add({
        "click_id": click_id,
        "offer_id": offer,
        "ip": ip,
        "created_at": firestore.SERVER_TIMESTAMP
    })

    redirect_url = f"https://network.com/offer?id={offer}&sub1={click_id}"
    return RedirectResponse(url=redirect_url)


@app.get("/postback")
async def postback(
    request: Request,
    click_id: str = None,
    payout: float = 0.0,
    tid: str = None,
    status: str = "approved"
):
    if not click_id:
        return "Missing click_id"

    ip = request.client.host

    db.collection("conversions").add({
        "click_id": click_id,
        "transaction_id": tid,
        "payout": payout,
        "status": status,
        "ip": ip,
        "created_at": firestore.SERVER_TIMESTAMP
    })

    return "OK"
