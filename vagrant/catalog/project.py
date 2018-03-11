from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, CategoryItem

engine = create_engine('sqlite:///itemcatalogapp.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/category/')
def showCategory():
    category = session.query(Category).all()
    return render_template('show_category.html',category=category)

@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('showCategory'))
    else:
        return render_template('category_new.html')

@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    edit_category = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            edit_category.name = request.form['name']
        session.add(edit_category)
        session.commit()
        return redirect(url_for('showCategory'))
    else:
        return render_template('edit_category.html',category = edit_category)


@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory():
    return "Category Deleted"



@app.route('/category/<int:category_id>/')
def categoryItem(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(CategoryItem).filter_by(category_id = category.id)
    return render_template('category_item.html', category=category, items=items)

@app.route('/category/<int:category_id>/new/', methods=['GET','POST'])
def newCategoryItem(category_id):
    if request.method == 'POST':
        newCategoryItem = CategoryItem(name=request.form['name'],\
                        description=request.form['description'],\
                        category_id=category_id)
        session.add(newCategoryItem)
        session.commit()
        return redirect(url_for('categoryItem',category_id=category_id))
    else:
        category = session.query(Category).filter_by(id = category_id).one()
        return render_template('category_item_new.html',\
                category_id=category_id, category=category)



@app.route('/category/<int:category_id>/<int:category_item_id>/edit/',\
            methods=['GET','POST'])
def editCategoryItem(category_id,category_item_id):
    category = session.query(Category).filter_by(id = category_id).one()
    edit_category_item = session.query(CategoryItem).filter_by(id = \
                category_item_id).one()

    if request.method == 'POST':
        print "hello"
        if request.form['name']:
            edit_category_item.name = request.form['name']
        if request.form['description']:
            edit_category_item.description = request.form['description']
        session.add(edit_category_item)
        session.commit()
        return redirect(url_for('categoryItem',category_id=category_id))
    else:
        return render_template('edit_category_item.html',\
                category_id=category_id, category_item_id=category_item_id,\
                category_item=edit_category_item)


@app.route('/category/<int:category_id>/<int:category_item_id>/delete/', \
            methods=['GET','POST'])
def deleteCategoryItem(category_id,category_item_id):
    category = session.query(Category).filter_by(id = category_id).one()
    delete_category_item = session.query(CategoryItem).filter_by(id = \
            category_item_id).one()
    if request.method == 'POST':
        session.delete(delete_category_item)
        session.commit()
        return redirect(url_for('categoryItem', category_id=category_id))
    else:
        return render_template('delete_category_item.html',\
                category_id=category_id,\
                category_item=delete_category_item)


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
