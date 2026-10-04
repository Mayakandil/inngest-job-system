import datetime
import logging 

from fastapi import FastAPI
import inngest
import inngest.fast_api


#create innggest client 
inngest_client = inngest.Inngest(
    app_id="report-api", logger = logging.getLogger("uvicorn"),
)

# create background function
@inngest_client.create_function(
        fn_id = "say-hello",
        trigger =inngest.TriggerEvent(event="test/hello"),
)

async def say_hello(ctx: inngest.Context):
    await ctx.step.sleep("wait-5-seconds",datetime.timedelta(seconds=5),)
    return "Hello from the background"

#create fastapi app
app = FastAPI()

#stage 0 
@app.get("/health")
def health():
    return {"status":"ok"}


#connect inngest to FastAPI
inngest.fast_api.serve(
    app,inngest_client,[say_hello],
)
