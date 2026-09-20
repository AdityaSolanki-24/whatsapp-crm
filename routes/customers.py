import os
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, current_app
)
from flask_login import login_required
from forms.customer_form import CustomerForm
from services.customer_service import CustomerService
from services.csv_import import CSVImportService
from utils.validators import allowed_csv_file
from utils.helpers import generate_unique_filename
from werkzeug.utils import secure_filename
from models.customer import Customer

customers_bp = Blueprint("customers", __name__, url_prefix="/customers")
customer_service = CustomerService()
csv_service = CSVImportService()


@customers_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "").strip()
    search_by = request.args.get("search_by", "name")
    pagination = customer_service.get_all(
        page=page, per_page=25, search=search or None, search_by=search_by
    )
    return render_template(
        "customers/customers.html",
        customers=pagination.items,
        pagination=pagination,
        search=search,
        search_by=search_by,
    )


@customers_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = CustomerForm()
    if form.validate_on_submit():
        result = customer_service.create({
            "customer_id": form.customer_id.data,
            "name": form.name.data,
            "email": form.email.data,
            "phone": form.phone.data,
            "orders": form.orders.data or 0,
            "status": form.status.data,
        })
        if result["success"]:
            flash(f"Customer '{form.name.data}' added successfully.", "success")
            return redirect(url_for("customers.index"))
        else:
            flash(result["error"], "danger")
    return render_template("customers/customer_form.html", form=form, action="Add")


@customers_bp.route("/<int:customer_id>")
@login_required
def view(customer_id):
    customer = customer_service.get_by_id(customer_id)
    if not customer:
        flash("Customer not found.", "warning")
        return redirect(url_for("customers.index"))
    return render_template("customers/customer_view.html", customer=customer)


@customers_bp.route("/<int:customer_id>/edit", methods=["GET", "POST"])
@login_required
def edit(customer_id):
    customer = customer_service.get_by_id(customer_id)
    if not customer:
        flash("Customer not found.", "warning")
        return redirect(url_for("customers.index"))

    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        result = customer_service.update(customer_id, {
            "customer_id": form.customer_id.data,
            "name": form.name.data,
            "email": form.email.data,
            "phone": form.phone.data,
            "orders": form.orders.data or 0,
            "status": form.status.data,
        })
        if result["success"]:
            flash("Customer updated successfully.", "success")
            return redirect(url_for("customers.view", customer_id=customer_id))
        else:
            flash(result["error"], "danger")

    return render_template("customers/customer_form.html", form=form, action="Edit", customer=customer)


@customers_bp.route("/<int:customer_id>/delete", methods=["POST"])
@login_required
def delete(customer_id):
    deleted = customer_service.delete(customer_id)
    if deleted:
        flash("Customer deleted.", "success")
    else:
        flash("Customer not found.", "warning")
    return redirect(url_for("customers.index"))


@customers_bp.route("/delete_selected", methods=["POST"])
@login_required
def delete_selected():
    # keep selection from current search context (optional but nicer)
    search = request.form.get("search", "")
    search_by = request.form.get("search_by", "name")
    all_customers = request.form.get("all_customers")

    if all_customers == "true":
        customer_ids = [str(c.id) for c in Customer.query.all()]
    else:
        customer_ids = request.form.getlist("customer_ids")

    result = customer_service.delete_many(customer_ids)

    if result.get("success"):
        deleted = result.get("deleted", 0)
        not_found = result.get("not_found", 0)
        if deleted > 0 and not_found == 0:
            flash(f"Deleted {deleted} customer(s).", "success")
        elif deleted > 0:
            flash(f"Deleted {deleted} customer(s). {not_found} not found.", "warning")
        else:
            flash("No customers were deleted.", "warning")
    else:
        flash(result.get("error", "Delete failed"), "danger")

    return redirect(
        url_for("customers.index", search=search, search_by=search_by)
        if search
        else url_for("customers.index", search_by=search_by)
    )



@customers_bp.route("/import", methods=["GET", "POST"])
@login_required
def import_csv():
    if request.method == "POST":
        if "csv_file" not in request.files:
            flash("No file selected.", "warning")
            return redirect(request.url)

        file = request.files["csv_file"]
        if not file or not file.filename:
            flash("No file selected.", "warning")
            return redirect(request.url)

        if not allowed_csv_file(file.filename):
            flash("Only CSV files are allowed.", "danger")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        upload_dir = os.path.join(current_app.root_path, "static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, f"import_{generate_unique_filename(filename)}")
        file.save(filepath)

        result = csv_service.import_csv(filepath)

        try:
            os.remove(filepath)
        except Exception:
            pass

        if result["success"]:
            msg = (
                f"Import complete: {result['created']} added, "
                f"{result['skipped_duplicate']} duplicates skipped, "
                f"{result['skipped_invalid']} invalid rows skipped "
                f"(from {result['total_rows']} total rows)."
            )
            flash(msg, "success" if result["created"] > 0 else "warning")
        else:
            flash(f"Import failed: {'; '.join(result['errors'][:3])}", "danger")

        return redirect(url_for("customers.index"))

    return render_template("customers/import_customers.html")
