from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """User object"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    # Define relationship to favorite products
    favorite_products = db.relationship('Product', secondary='favorite_products',
        backref=db.backref('users', lazy='dynamic'))

    # Define relationship to favorite reviews
    favorite_reviews = db.relationship('Review', secondary='favorite_reviews',
        backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        """Display when printing a User object"""

        return "<User: {} email: {}>".format(self.user_id, self.email)


# Crosslink between products and categories
product_categories = db.Table('product_categories',
    db.Column('asin', db.Text, db.ForeignKey('products.asin')),
    db.Column('cat_name', db.Text, db.ForeignKey('categories.cat_name'))
)


class Product(db.Model):
    """Product object"""

    __tablename__ = "products"

    asin = db.Column(db.Text, primary_key=True)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    author = db.Column(db.Text)
    image = db.Column(db.Text, nullable=False)   # link to image
    scores = db.Column(db.JSON)    # dictionary with 1-5 star ratings
    n_scores = db.Column(db.Integer)

    categories = db.relationship('Category',
                                 secondary=product_categories,
                                 backref=db.backref('products',
                                                    lazy='dynamic'))

    def __repr__(self):
        """Display when printing a Product object"""

        return "<Product: {} name: {}>".format(self.asin, self.title)

    def calculate_score_distribution(self):
        """Calculates the distribution of 1,2,3,4,5 star reviews"""

        distribution = {1:0, 2:0, 3:0, 4:0, 5:0}

        for review in self.reviews:
            distribution[review.score] += 1

        return distribution



class Review(db.Model):
    """Review object"""

    __tablename__ = "reviews"

    review_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    reviewer_id = db.Column(db.Text, nullable=False)
    reviewer_name = db.Column(db.Text)
    review = db.Column(db.Text, nullable=False)
    asin = db.Column(db.Text, db.ForeignKey('products.asin'))
    helpful_total = db.Column(db.Integer)
    helpful_fraction = db.Column(db.Float)
    score = db.Column(db.Integer, nullable=False)
    summary = db.Column(db.Text)
    time = db.Column(db.DateTime)

    # Define relationship to product
    product = db.relationship('Product',
                              backref=db.backref('reviews',
                                                 order_by=review_id))

    def __repr__(self):
        """Display when printing a Review object"""

        return "<Review: {} asin: {} summary: {}>".format(self.review_id,
                                                          self.asin,
                                                          self.summary)


class Category(db.Model):
    """Product categories"""

    __tablename__ = "categories"

    cat_name = db.Column(db.Text, primary_key=True)

    def __repr__(self):
        """Display when printing a Category object"""

        return "<Category: {}>".format(self.cat_name)


# Crosslink between users and favorited products
favorite_products = db.Table('favorite_products',
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id')),
    db.Column('asin', db.Text, db.ForeignKey('products.asin'))
)

# Crosslink between users and favorited reviews
favorite_reviews = db.Table('favorite_reviews',
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id')),
    db.Column('review_id', db.Integer, db.ForeignKey('reviews.review_id'))
)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to Flask app."""

    # Configure to use PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///reviewgenius'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # Work with database directly if run interactively

    from server import app
    connect_to_db(app)
    print "Connected to DB."
