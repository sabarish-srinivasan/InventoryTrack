import os

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request

from flask_sqlalchemy import SQLAlchemy

directory = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(directory, "inventory_database.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
database = SQLAlchemy(app)


class InventoryItem(database.Model):
    item_name = database.Column(database.String(), nullable=False, primary_key=True)
    del_comments = database.Column(database.String(), nullable=True)
    del_flag = database.Column(database.Boolean(), default=False)

    def __repr__(self):
        return "<Item: {}>".format(self.item_name)


@app.route('/', methods=["GET", "POST"])
def main():
    items = None
    if request.form:
        try:
            inventory_item = InventoryItem(item_name=request.form.get("item_name"))
            database.session.add(inventory_item)
            database.session.commit()
        except Exception as i:
            print("Failed to add item")
            print(i)
    items = InventoryItem.query.filter_by(del_flag=False)
    return render_template("setup.html", items=items)


@app.route("/update", methods=["POST"])
def update():
    try:
        new_item = request.form.get("new_item")
        old_item = request.form.get("old_item")
        inventory_item = InventoryItem.query.filter_by(item_name=old_item).first()
        inventory_item.item_name = new_item
        database.session.commit()
    except Exception as i:
        print("Couldn't update item")
        print(i)
    return redirect("/")


@app.route("/delete", methods=["POST"])
def delete():
    item_name = request.form.get("item_name")
    inventory_item = InventoryItem.query.filter_by(item_name=item_name).first()
    inventory_item.del_flag = True
    comment = request.form.get("comment")
    inventory_item.del_comment = comment
    items = InventoryItem.query.filter_by(del_flag=False)
    database.session.commit()
    return render_template("setup.html", items=items)


@app.route("/undelete", methods=["POST"])
def undelete():
    item_to_undelete = InventoryItem.query.filter_by(del_flag=True).first()
    item_to_undelete.del_flag = False
    database.session.commit()
    items = InventoryItem.query.filter_by(del_flag=False)
    return render_template("setup.html", items=items)


if __name__ == "__main__":
    app.run(debug=True)
