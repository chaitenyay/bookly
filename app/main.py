from fastapi import FastAPI
from app.books.routes import book_router
from app.auth.routes import auth_router
from app.author.routes import author_router
from app.members.routes import member_router
from app.publisher.routes import publisher_router
from contextlib import asynccontextmanager
from app.db.main import init_db
from app.config import Config

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform any startup tasks here (e.g., connect to the database)
    print("Starting up...")
    await init_db()  # Initialize the database (create tables, etc.)    
    yield
    # Perform any shutdown tasks here (e.g., disconnect from the database)
    print("Shutting down...")

version = "v1"  # Define API version

app = FastAPI(
    title="Bookly API",
    description="A simple API for managing books.",
    version=version,
    lifespan=lifespan
) 


# @app.get("/")
# def home():
#     d = Config.DATABASE_URL
#     return f"Bookly - A Book Library Service. Database URL: {d}"

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["Books"])  # Include the book router to handle book-related endpoints
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["Auth"])  # Include the auth router to handle authentication-related endpoints
app.include_router(author_router, prefix=f"/api/{version}/authors", tags=["Authors"])  # Include the author router to handle author-related endpoints
app.include_router(member_router, prefix=f"/api/{version}/members", tags=["Members"])  # Include the member router to handle member-related endpoints
app.include_router(publisher_router, prefix=f"/api/{version}/publishers", tags=["Publishers"])  # Include the publisher router to handle publisher-related endpoints