from app import create_app
from services.cats.store import CatStore

app = create_app()
with app.app_context():
    cat = CatStore.get_cat_by_name('beans')
    print(f"Cat 'beans': {cat}")
