from flask import Flask, render_template, request, redirect, url_for
import db
from extract import extract_items

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


@app.route("/approve/<int:item_id>", methods=["POST"])
def approve(item_id):
    db.approve_item(item_id)
    return redirect(request.referrer or url_for("home"))


@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit(item_id):
    if request.method == "POST":
        owner = request.form.get("owner", "").strip() or "unknown"
        deadline = request.form.get("deadline", "").strip() or "unknown"
        db.update_item(item_id, owner, deadline)
        return redirect(url_for("home"))
    item = db.get_item(item_id)
    if item is None:
        return "Item not found", 404
    return render_template("edit.html", item=item)


@app.route("/new", methods=["GET", "POST"])
def new_meeting():
    if request.method == "POST":
        title = request.form.get("title", "").strip() or "Untitled meeting"
        transcript = request.form.get("transcript", "").strip()
        if not transcript:
            return render_template("new.html", error="Please paste a transcript.")
        try:
            items = extract_items(transcript)
        except Exception as e:
            return render_template("new.html", error=f"Extraction failed: {type(e).__name__}")
        db.save_meeting(title, transcript, items)
        return redirect(url_for("home"))
    return render_template("new.html", error=None)


if __name__ == "__main__":
    app.run(debug=True)