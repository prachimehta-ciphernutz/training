from fastapi import FastAPI, BackgroundTasks
import time

app = FastAPI()

# bg task function

def send_email(email: str):
    time.sleep(5)
    print(f"Email sent to {email}")

# route
@app.post("/send-email/")
async def send_email_api(email:str, background_tasks: BackgroundTasks):
    # add bg task
    background_tasks.add_task(send_email, email)
    return {"message": f"Email request received for {email}"}