import datetime
import logging 
import uuid
from fastapi import FastAPI , HTTPException
import inngest
import inngest.fast_api
from pydantic import BaseModel


reports ={}

class ReportRequest(BaseModel):
    topic : str

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

@inngest_client.create_function(
    fn_id = "make-report",
    trigger= inngest.TriggerEvent(event="report/requested"),
)
async def make_report(ctx:inngest.Context):
    
    await ctx.step.sleep(
        "do-the-slow-work",
        datetime.timedelta(seconds=8),
    )
    
    def build_report():
        report_id =ctx.event.data["id"]
        topic = ctx.event.data["topic"]

        result = f"Roprt about {topic}"

        reports[report_id]["status"]= "done"
        reports[report_id]["result"] = result
        
        return result
    result = await ctx.step.run("build-report",build_report)
    return {"result":result}


#create fastapi app
app = FastAPI()

#stage 0 
@app.get("/health")
def health():
    return {"status":"ok"}


@app.post("/reports" , status_code=202)
async def create_report(request: ReportRequest):
    report_id = str(uuid.uuid4())
    reports[report_id] = {"id":report_id , "topic": request.topic, "status":"pending",}

    await inngest_client.send(
        inngest.Event(name="report/requested", data={"id":report_id , "topic":request.topic,})
    )
    
    return reports[report_id]

@app.get("/reports/{report_id}")
def get_report(report_id: str):
    if report_id not in reports:
        raise HTTPException (status_code=404, detail="Report not found ")

    return reports[report_id]

#connect inngest to FastAPI
inngest.fast_api.serve(
    app,inngest_client,[say_hello , make_report],
)
