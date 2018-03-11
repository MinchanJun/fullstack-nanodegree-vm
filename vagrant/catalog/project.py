from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, CategoryItem

engine = create_engine('sqlite:///itemcatalogapp.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/category/<int:category_id>/')
def categoryItem(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(CategoryItem).filter_by(category_id = category.id)
    return render_template('category_item.html', category=category, items=items)

@app.route('/category/<int:category_id>/new/')
def newCategoryItem(category_id):
    return "Category Item Add complete"

@app.route('/category/<int:category_id>/<int:category_item_id>/edit/')
def editCategoryItem(category_id,category_item_id):
    return "Category Item Edit Complete"

@app.route('/category/<int:category_id>/<int:category_item_id>/delete')
def deleteCategoryItem(category_id,category_item_id):
    return "Category Item Delete Complete"

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
