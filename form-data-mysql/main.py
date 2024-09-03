from fastapi import FastAPI, HTTPException, Depends, status, Form, Request
from sqlalchemy import insert, delete
from pydantic import BaseModel
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import logging

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


app.mount("/static", StaticFiles(directory="HTML"), name="static")
templates = Jinja2Templates(directory="HTML")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    print("Rendering contact form...")
    return templates.TemplateResponse("contact-form.html", {"request": request})

@app.post("/submit", status_code=status.HTTP_201_CREATED)
async def submit_form(
    fullname: str = Form(...),
    email: str = Form(...),
    gender: str = Form(...),
    newsletter: bool = Form(False),
    comment: str = Form(""),
    db: Session = Depends(get_db)
):
    existing_user = db.query(models.ContactForm).filter(models.ContactForm.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        db_form = models.ContactForm(
            fullname=fullname,
            email=email,
            gender=gender,
            newsletter=newsletter,
            comment=comment
        )
        db.add(db_form)
        db.commit()
        return {"message": "Form submitted successfully!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while submitting the form")

@app.get("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def read_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.ContactForm).filter(models.ContactForm.id == post_id).first()
    
    if post is None:
        raise HTTPException(status_code=404, detail='Post was not found')
    print(f"ID: {post.id}")
    print(f"Full Name: {post.fullname}")
    print(f"Email: {post.email}")
    print(f"Gender: {post.gender}")
    print(f"Newsletter: {post.newsletter}")
    print(f"Comment: {post.comment}")    
    return post

@app.delete("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    try:
        db_post = db.query(models.ContactForm).filter(models.ContactForm.id == post_id).first()
        if db_post is None:
            raise HTTPException(status_code=404, detail='Post was not found')

        # Move the record to the deleted_contact_forms table
        db.execute(
            insert(models.DeletedContactForm).values(
                id=db_post.id,
                fullname=db_post.fullname,
                email=db_post.email,
                gender=db_post.gender,
                newsletter=db_post.newsletter,
                comment=db_post.comment,
                # deleted_at=datetime.now(IST)  # Use IST time
            )
        )
        db.commit()

        # Delete the record from the contact_forms table
        db.delete(db_post)
        db.commit()
        return {"message": "Post deleted successfully"}
    except Exception as e:
        logging.error(f"Error deleting post with id {post_id}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while deleting the post")

@app.put("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def update_post(
    post_id: int,
    fullname: str = Form(...),
    email: str = Form(...),
    gender: str = Form(...),
    newsletter: bool = Form(False),
    comment: str = Form(""),
    db: Session = Depends(get_db)
):
    db_post = db.query(models.ContactForm).filter(models.ContactForm.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail='Post was not found')

    db_post.fullname = fullname
    db_post.email = email
    db_post.gender = gender
    db_post.newsletter = newsletter
    db_post.comment = comment

    db.commit()
    return {"message": "Post updated successfully"}

@app.patch("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def partial_update_post(
    post_id: int,
    fullname: str = Form(None),
    email: str = Form(None),
    gender: str = Form(None),
    newsletter: bool = Form(None),
    comment: str = Form(None),
    db: Session = Depends(get_db)
):
    db_post = db.query(models.ContactForm).filter(models.ContactForm.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail='Post was not found')

    if fullname is not None:
        db_post.fullname = fullname
    if email is not None:
        db_post.email = email
    if gender is not None:
        db_post.gender = gender
    if newsletter is not None:
        db_post.newsletter = newsletter
    if comment is not None:
        db_post.comment = comment

    db.commit()
    return {"message": "Post partially updated successfully"}

@app.post("/restore/{post_id}", status_code=status.HTTP_200_OK)
async def restore_post(post_id: int, db: Session = Depends(get_db)):
    try:
        # Fetch the record from deleted_contact_forms
        deleted_post = db.query(models.DeletedContactForm).filter(models.DeletedContactForm.id == post_id).first()
        if deleted_post is None:
            raise HTTPException(status_code=404, detail='Post was not found in deleted records')

        # Restore the record to contact_forms
        db_form = models.ContactForm(
            id=deleted_post.id,
            fullname=deleted_post.fullname,
            email=deleted_post.email,
            gender=deleted_post.gender,
            newsletter=deleted_post.newsletter,
            comment=deleted_post.comment
        )
        db.add(db_form)
        db.commit()

        # Optionally, delete the record from deleted_contact_forms
        db.execute(
            delete(models.DeletedContactForm).where(models.DeletedContactForm.id == post_id)
        )
        db.commit()

        return {"message": "Post restored successfully!"}
    except Exception as e:
        logging.error(f"Error restoring post with id {post_id}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while restoring the post")

