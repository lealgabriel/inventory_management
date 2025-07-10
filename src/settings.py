from decouple import config

APPLICATION_NAME = config("APPLICATION_NAME", default="Inventory Management")

DATABASE_URL = config("DATABASE_URL", default="postgresql+asyncpg://admin:admin@localhost:5432/inventory_management")