# ✨ This endpoint was generated using Kiro (https://kiro.studio)
# Kiro Spec: "Create a POST endpoint at /api/contact that receives name, email, and message as JSON and returns a success response."
class ContactForm(BaseModel):
    name: str
    email: str
    message: str

@app.post("/api/contact")
async def submit_contact(form: ContactForm):
    # In a real-world scenario, you might send an email or save to database here
    return {"message": f"Thanks {form.name}, your message has been received!"}
