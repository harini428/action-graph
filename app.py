from flask import Flask, render_template, request, redirect, url_for
import db

app = Flask(__name__)

@app.route("/")
def home():
    only_review = request.args.get("filter") == "review"
    all_items = db.get_all_items()

    stats = {
        "total": len(all_items),
        "review": sum(1 for i in all_items if i["needs_review"]),
        "done": sum(1 for i in all_items if i["status"] == "done"),
    }

    items = [i for i in all_items if i["needs_review"]] if only_review else all_items
    return render_template("index.html", items=items, only_review=only_review, stats=stats)

@app.route("/done/<int:item_id>", methods=["POST"])
def done(item_id):
    db.mark_done(item_id)
    return redirect(request.referrer or url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)