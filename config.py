import os
from dotenv import load_dotenv

load_dotenv()

# Parâmetros padrão propostos para testes com Docker local. 
# Quando subir no Render/Railway, você vai colocar essa variável lá na Dashboard deles.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://gpow_user:gpow_pass@localhost:5434/gpow_db")
