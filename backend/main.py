
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import SessionLocal,engine
from models import Todo,Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/todos")
def read_todos(db = Depends(get_db)):
    todos = db.query(Todo).all()
    return todos


class TodoCreate(BaseModel):
    title: str

@app.post("/todos")
def create_todo(new_Todo: TodoCreate, db = Depends(get_db)):
    db_todo = Todo(title = new_Todo.title)
    db.add(db_todo)
    db.commit()
    return {"message": "Todo created"}

class TodoUpdate(BaseModel):
    title: str

@app.put("/todos/{todo_id}")
def update_todo(
    todo_id: int,
    request_data : TodoUpdate,
    db = Depends(get_db)
):

    todo_item = db.query(Todo).filter(Todo.id == todo_id).first()
    
    if not todo_item:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo_item.title = request_data.title
    db.add(todo_item)
    db.commit()
    
    return {"message": "Todo updated"}


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db = Depends(get_db)):
    todo_item = db.query(Todo).filter(Todo.id == todo_id).first()
    
    if not todo_item:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(todo_item)
    db.commit()
    
    return {"message": "Todo deleted"}