from datetime import datetime
import logging
from sqlmodel import Session, select

from api.core.config import settings
from api.models import Recipe, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_users(session: Session):
    if not settings.SUPERUSER_GID:
        raise ValueError("Missing SUPERUSER_GID env variable.")

    existing = session.exec(
        select(User).where(User.google_user_id == settings.SUPERUSER_GID)
    ).first()

    if existing is not None:
        logger.warn("Superuser already exsits, skipping add.")
        return

    first_user = User.model_validate(
        {
            "username": "admin",
            "email": "admin@joelyoung.dev",
            "display_name": "admin",
            "admin": True,
            "google_user_id": settings.SUPERUSER_GID,
        }
    )
    session.add(first_user)
    session.commit()
    session.refresh(first_user)
    logger.info("Successfully created users")


def init_recipes(session: Session):
    user = session.exec(select(User)).first()

    import random

    recipes_source = [
        {
            "created_by_id": user.id,
            "created_on": datetime.now(),
            "name": "Classic Chocolate Chip Cookies",
            "description": "Soft and chewy chocolate chip cookies that are perfect for any occasion",
            "instructions": "1. Preheat oven to 375°F\n2. Cream butter and sugars\n3. Beat in eggs and vanilla\n4. Mix in dry ingredients\n5. Stir in chocolate chips\n6. Drop by rounded tablespoons onto baking sheets\n7. Bake 9-11 minutes until golden brown",
            "notes": "For softer cookies, reduce baking time by 1-2 minutes",
            "public": False,
            "prep_time": random.randint(5, 60),
        },
        {
            "created_by_id": user.id,
            "created_on": datetime.now(),
            "name": "Spaghetti Carbonara",
            "description": "Classic Italian pasta dish with eggs, cheese, pancetta and black pepper",
            "instructions": "1. Cook spaghetti in salted water\n2. Fry pancetta until crispy\n3. Mix eggs, cheese and pepper\n4. Combine hot pasta with egg mixture\n5. Add pancetta and extra cheese",
            "notes": "Work quickly when mixing eggs to avoid scrambling",
            "public": True,
            "prep_time": random.randint(5, 60),
        },
        {
            "created_by_id": user.id,
            "created_on": datetime.now(),
            "name": "Chicken Stir Fry",
            "description": "Quick and healthy chicken stir fry with vegetables",
            "instructions": "1. Cut chicken into strips\n2. Chop vegetables\n3. Heat wok with oil\n4. Stir fry chicken until cooked\n5. Add vegetables\n6. Add sauce and simmer",
            "notes": "Can substitute any vegetables you have on hand",
            "public": True,
            "prep_time": random.randint(5, 60),
        },
        {
            "created_by_id": user.id,
            "created_on": datetime.now(),
            "name": "Banana Bread",
            "description": "Moist and delicious banana bread using overripe bananas",
            "instructions": "1. Preheat oven to 350°F\n2. Mash bananas\n3. Mix wet ingredients\n4. Combine with dry ingredients\n5. Pour into loaf pan\n6. Bake 60-65 minutes",
            "notes": "Best with very ripe bananas with brown spots",
            "public": False,
            "prep_time": random.randint(5, 60),
        },
        {
            "created_by_id": user.id,
            "created_on": datetime.now(),
            "name": "Greek Salad",
            "description": "Fresh and crisp traditional Greek salad",
            "instructions": "1. Chop cucumbers and tomatoes\n2. Slice red onion\n3. Add kalamata olives\n4. Crumble feta cheese\n5. Dress with olive oil and oregano",
            "notes": "Use the freshest vegetables possible",
            "public": True,
            "prep_time": random.randint(5, 60),
        },
        {
            "created_by_id": user.id,
            "created_on": datetime.now(),
            "name": "Beef Tacos",
            "description": "Simple and delicious ground beef tacos",
            "instructions": "1. Brown ground beef\n2. Add taco seasoning\n3. Warm taco shells\n4. Prepare toppings\n5. Assemble tacos",
            "notes": "Can make taco seasoning from scratch for better flavor",
            "public": True,
            "prep_time": random.randint(5, 60),
        },
        {
            "created_by_id": user.id,
            "created_on": datetime.now(),
            "name": "Vegetable Soup",
            "description": "Hearty homemade vegetable soup",
            "instructions": "1. Chop all vegetables\n2. Sauté onions and garlic\n3. Add vegetables and broth\n4. Simmer until vegetables are tender\n5. Season to taste",
            "notes": "Great way to use up leftover vegetables",
            "public": True,
            "prep_time": random.randint(5, 60),
        },
        {
            "created_by_id": user.id,
            "created_on": datetime.now(),
            "name": "Blueberry Pancakes",
            "description": "Fluffy pancakes studded with fresh blueberries",
            "instructions": "1. Mix dry ingredients\n2. Combine wet ingredients\n3. Fold together gently\n4. Fold in blueberries\n5. Cook on griddle until golden",
            "notes": "Can use frozen blueberries if fresh aren't available",
            "public": False,
            "prep_time": random.randint(5, 60),
        },
        {
            "created_by_id": user.id,
            "created_on": datetime.now(),
            "name": "Guacamole",
            "description": "Fresh homemade guacamole with ripe avocados",
            "instructions": "1. Mash avocados\n2. Dice onion and tomato\n3. Chop cilantro\n4. Mix ingredients\n5. Season with lime and salt",
            "notes": "Add jalapeño for extra heat",
            "public": True,
            "prep_time": random.randint(5, 60),
        },
        {
            "created_by_id": user.id,
            "created_on": datetime.now(),
            "name": "Chicken Noodle Soup",
            "description": "Comforting homemade chicken noodle soup",
            "instructions": "1. Cook chicken in broth\n2. Chop vegetables\n3. Add vegetables to broth\n4. Cook egg noodles\n5. Season with herbs",
            "notes": "Can use rotisserie chicken for quicker preparation",
            "public": True,
            "prep_time": random.randint(5, 60),
        },
    ]

    recipes = [Recipe.model_validate(recipe_data) for recipe_data in recipes_source]
    session.add_all(recipes)
    session.commit()
    logger.info("Successfully created recipes")


def seed_database(session: Session):
    init_users(session)

    init_recipes(session)
