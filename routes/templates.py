from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from forms.template_form import TemplateForm
from services.template_service import TemplateService
from models.message_template import MessageTemplate

templates_bp = Blueprint("templates", __name__, url_prefix="/templates")
template_service = TemplateService()


@templates_bp.route("/")
@login_required
def index():
    all_templates = template_service.get_all()
    return render_template("templates/templates.html", templates=all_templates)


@templates_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = TemplateForm()
    if form.validate_on_submit():
        existing = MessageTemplate.query.filter_by(template_name=form.template_name.data).first()
        if existing:
            flash(f"Template name '{form.template_name.data}' already exists.", "danger")
        else:
            template_service.create(
                name=form.template_name.data,
                content=form.template_content.data,
                category=form.category.data,
            )
            flash("Template created successfully.", "success")
            return redirect(url_for("templates.index"))
    return render_template("templates/template_form.html", form=form, action="Create")


@templates_bp.route("/<int:template_id>")
@login_required
def view(template_id):
    template = template_service.get_by_id(template_id)
    if not template:
        flash("Template not found.", "warning")
        return redirect(url_for("templates.index"))
    return render_template("templates/template_view.html", template=template)


@templates_bp.route("/<int:template_id>/edit", methods=["GET", "POST"])
@login_required
def edit(template_id):
    template = template_service.get_by_id(template_id)
    if not template:
        flash("Template not found.", "warning")
        return redirect(url_for("templates.index"))

    form = TemplateForm(obj=template)
    if form.validate_on_submit():
        existing = MessageTemplate.query.filter_by(
            template_name=form.template_name.data
        ).first()
        if existing and existing.id != template_id:
            flash("Another template with that name already exists.", "danger")
        else:
            template_service.update(
                template_id,
                name=form.template_name.data,
                content=form.template_content.data,
                category=form.category.data,
            )
            flash("Template updated.", "success")
            return redirect(url_for("templates.index"))

    return render_template(
        "templates/template_form.html", form=form, action="Edit", template=template
    )


@templates_bp.route("/<int:template_id>/delete", methods=["POST"])
@login_required
def delete(template_id):
    template_service.delete(template_id)
    flash("Template deleted.", "success")
    return redirect(url_for("templates.index"))


@templates_bp.route("/<int:template_id>/content")
@login_required
def get_content(template_id):
    """AJAX endpoint to load template content into campaign form."""
    template = template_service.get_by_id(template_id)
    if not template:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"content": template.template_content})
