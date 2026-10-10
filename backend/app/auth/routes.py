import json
from datetime import datetime
from io import BytesIO
import html

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.lineplots import LinePlot
from flask import jsonify, request, send_file
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.models.user import User
from app.models.assessment import Assessment
from app.extensions import bcrypt, db
from . import auth_bp


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}

    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")

    if not full_name or not email or not password:
        return jsonify(
            {
                "error": "All fields are required"
            }
        ), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify(
            {
                "error": "Email already registered"
            }
        ), 409

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(
        full_name=full_name,
        email=email,
        password_hash=hashed_password
    )
    db.session.add(user)
    db.session.commit()

    return jsonify(
        {
            "message": "User registered successfully"
        }
    ), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify(
            {
                "error": "Email or Password are required"
            }
        ), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.password_hash:
        return jsonify(
            {
                "error": "Invalid email or password"
            }
        ), 401

    if not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify(
            {
                "error": "Invalid email or password"
            }
        ), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify(
        {
            "message": "Login successful",
            "access_token": access_token
        }
    ), 200


@auth_bp.route("/google", methods=["POST"])
def google_login():
    data = request.get_json() or {}

    google_token = data.get("credential")

    if not google_token:
        return jsonify(
            {
                "error": "Google credential is required"
            }
        ), 400

    try:
        GOOGLE_CLIENT_ID = "101681046390-bg14ds2o6kmu0snob1prfisnprrgh000.apps.googleusercontent.com"

        idinfo = id_token.verify_oauth2_token(
            google_token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email")
        full_name = idinfo.get("name")

        if not email:
            return jsonify(
                {
                    "error": "Google account email not available"
                }
            ), 400

        user = User.query.filter_by(email=email).first()

        if not user:
            user = User(
                full_name=full_name or "Google User",
                email=email,
                password_hash=None,
                provider="google"
            )

            db.session.add(user)
            db.session.commit()

        access_token = create_access_token(
            identity=str(user.id)
        )

        return jsonify(
            {
                "message": "Google login successful",
                "access_token": access_token
            }
        ), 200

    except ValueError:
        return jsonify(
            {
                "error": "Invalid Google credential"
            }
        ), 401


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    identity = get_jwt_identity()

    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity"}), 401

    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify(
            {
                "error": "User not found"
            }
        ), 404

    return jsonify(
        {
            "full_name": user.full_name,
            "email": user.email
        }
    ), 200


@auth_bp.route("/export-data", methods=["GET"])
@jwt_required()
def export_data():
    """Download the authenticated user's account and assessment data as JSON."""
    identity = get_jwt_identity()

    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity"}), 401

    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    assessments = (
        Assessment.query
        .filter_by(user_id=user.id)
        .order_by(Assessment.created_at.asc(), Assessment.id.asc())
        .all()
    )

    exported_at = datetime.utcnow()

    def datetime_to_iso(value):
        return value.isoformat() + "Z" if value else None

    assessment_records = []
    for assessment in assessments:
        assessment_records.append({
            "id": assessment.id,
            "created_at": datetime_to_iso(assessment.created_at),
            "prediction_score": assessment.prediction_score,
            "sleep_hours": assessment.sleep_hours,
            "sleep_quality": assessment.sleep_quality,
            "stress_level": assessment.stress_level,
            "academic_pressure": assessment.academic_pressure,
            "mood": assessment.mood,
            "energy_level": assessment.energy_level,
            "social_interaction": assessment.social_interaction,
            "exercise_minutes": assessment.exercise_minutes,
            "screen_time": assessment.screen_time,
            "study_hours": assessment.study_hours,
            "journal_text": assessment.journal_text,
            "facial_emotion": assessment.facial_emotion,
            "facial_confidence": assessment.facial_confidence,
            "facial_used": assessment.facial_used,
        })

    export_payload = {
        "export_info": {
            "format": "JSON",
            "exported_at": datetime_to_iso(exported_at),
            "description": "Personal account and assessment data export."
        },
        "account": {
            "full_name": user.full_name,
            "email": user.email,
            "provider": user.provider,
            "role": user.role,
            "created_at": datetime_to_iso(user.created_at),
        },
        "assessments": assessment_records,
    }

    file_bytes = BytesIO(
        json.dumps(
            export_payload,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8")
    )
    file_bytes.seek(0)

    filename = f"my_wellbeing_data_{exported_at.strftime('%Y-%m-%d')}.json"

    response = send_file(
        file_bytes,
        mimetype="application/json",
        as_attachment=True,
        download_name=filename,
        max_age=0
    )
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
@auth_bp.route("/export-report", methods=["GET"])
@jwt_required()
def export_report():
    """Generate a personal wellbeing report as a PDF."""

    identity = get_jwt_identity()

    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity"}), 401

    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    assessments = (
        Assessment.query
        .filter_by(user_id=user.id)
        .order_by(Assessment.created_at.asc(), Assessment.id.asc())
        .all()
    )

    generated_at = datetime.utcnow()
    output = BytesIO()

    # Report colours
    navy = colors.HexColor("#183B56")
    teal = colors.HexColor("#2A9D8F")
    pale_blue = colors.HexColor("#EEF5F8")
    light_teal = colors.HexColor("#E8F5F2")
    muted = colors.HexColor("#5B6B75")
    border = colors.HexColor("#D9E3E8")

    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=19 * mm,
        bottomMargin=18 * mm,
        title="Personal Wellbeing Report",
        author="Student Wellbeing Early Warning System",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=28,
        textColor=navy,
        alignment=TA_LEFT,
        spaceAfter=5,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        textColor=muted,
        spaceAfter=4,
    )

    section_style = ParagraphStyle(
        "ReportSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=navy,
        spaceBefore=12,
        spaceAfter=7,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#263746"),
        spaceAfter=5,
    )

    small_style = ParagraphStyle(
        "ReportSmall",
        parent=body_style,
        fontSize=8,
        leading=11,
        textColor=muted,
    )

    cell_style = ParagraphStyle(
        "ReportCell",
        parent=body_style,
        fontSize=8,
        leading=10,
        spaceAfter=0,
    )

    header_style = ParagraphStyle(
        "ReportHeaderCell",
        parent=cell_style,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )

    def safe_text(value):
        return html.escape(
            str(value if value is not None else "—")
        ).replace("\n", "<br/>")

    def formatted_date(value):
        if not value:
            return "Not available"

        return value.strftime("%d %b %Y, %I:%M %p")

    story = []

    # --------------------------------------------------
    # Report header
    # --------------------------------------------------

    story.append(
        Paragraph("PERSONAL WELLBEING", subtitle_style)
    )

    story.append(
        Paragraph("Wellbeing Data Report", title_style)
    )

    story.append(
        Paragraph(
            "A personal summary of your self-reported check-ins "
            "and recorded indicators.",
            subtitle_style,
        )
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=2,
            color=teal,
            spaceBefore=5,
            spaceAfter=13,
        )
    )

    # --------------------------------------------------
    # Account overview
    # --------------------------------------------------

    story.append(
        Paragraph("Account Overview", section_style)
    )

    account_rows = [
        [
            Paragraph("<b>Name</b>", cell_style),
            Paragraph(safe_text(user.full_name), cell_style),
        ],
        [
            Paragraph("<b>Email</b>", cell_style),
            Paragraph(safe_text(user.email), cell_style),
        ],
        [
            Paragraph("<b>Account Created</b>", cell_style),
            Paragraph(formatted_date(user.created_at), cell_style),
        ],
        [
            Paragraph("<b>Report Generated</b>", cell_style),
            Paragraph(formatted_date(generated_at), cell_style),
        ],
        [
            Paragraph("<b>Total Assessments</b>", cell_style),
            Paragraph(str(len(assessments)), cell_style),
        ],
    ]

    account_table = Table(
        account_rows,
        colWidths=[43 * mm, 115 * mm],
    )

    account_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), pale_blue),
            ("BOX", (0, 0), (-1, -1), 0.6, border),
            ("INNERGRID", (0, 0), (-1, -1), 0.35, border),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ])
    )

    story.append(account_table)

    # --------------------------------------------------
    # Assessment details and history
    # --------------------------------------------------

    if assessments:

        latest = assessments[-1]

        latest_score = (
            float(latest.prediction_score) * 100
        )

        story.append(
            Paragraph("Latest Check-In", section_style)
        )

        latest_rows = [
            ["Assessment Date", formatted_date(latest.created_at)],
            ["Recorded Risk Indicator", f"{latest_score:.1f}%"],
            ["Sleep Duration", f"{latest.sleep_hours:g} hours"],
            ["Sleep Quality", f"{latest.sleep_quality}/5"],
            ["Stress Level", f"{latest.stress_level}/5"],
            ["Academic Pressure", f"{latest.academic_pressure}/5"],
            ["Mood", f"{latest.mood}/5"],
            ["Energy Level", f"{latest.energy_level}/5"],
            ["Social Interaction", f"{latest.social_interaction}/5"],
            ["Exercise", f"{latest.exercise_minutes:g} minutes"],
            ["Screen Time", f"{latest.screen_time:g} hours"],
            ["Study Time", f"{latest.study_hours:g} hours"],
            [
                "Facial Emotion Signal",
                latest.facial_emotion
                if latest.facial_used and latest.facial_emotion
                else "Not provided",
            ],
        ]

        latest_table_data = [
            [
                Paragraph(f"<b>{safe_text(label)}</b>", cell_style),
                Paragraph(safe_text(value), cell_style),
            ]
            for label, value in latest_rows
        ]

        latest_table = Table(
            latest_table_data,
            colWidths=[55 * mm, 103 * mm],
        )

        latest_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), light_teal),
                ("BOX", (0, 0), (-1, -1), 0.6, border),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, border),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ])
        )

        story.append(latest_table)

        # Journal reflection
        story.append(
            Paragraph("Latest Reflection", section_style)
        )

        reflection = (latest.journal_text or "").strip()

        story.append(
            Paragraph(
                safe_text(reflection)
                if reflection
                else "No reflection was recorded.",
                body_style,
            )
        )

        # History table
        story.append(
            Paragraph("Assessment History", section_style)
        )

        story.append(
            Paragraph(
                "Historical scores represent model-generated awareness "
                "indicators, not clinical measurements.",
                small_style,
            )
        )

        history_data = [[
            Paragraph("Date", header_style),
            Paragraph("Indicator", header_style),
            Paragraph("Sleep", header_style),
            Paragraph("Mood", header_style),
            Paragraph("Stress", header_style),
        ]]

        for item in reversed(assessments):

            history_data.append([
                Paragraph(
                    safe_text(
                        item.created_at.strftime("%d %b %Y")
                        if item.created_at else "—"
                    ),
                    cell_style,
                ),
                Paragraph(
                    f"{float(item.prediction_score) * 100:.1f}%",
                    cell_style,
                ),
                Paragraph(
                    f"{item.sleep_hours:g} h",
                    cell_style,
                ),
                Paragraph(
                    f"{item.mood}/5",
                    cell_style,
                ),
                Paragraph(
                    f"{item.stress_level}/5",
                    cell_style,
                ),
            ])

        history_table = Table(
            history_data,
            colWidths=[
                45 * mm,
                28 * mm,
                27 * mm,
                27 * mm,
                27 * mm,
            ],
            repeatRows=1,
        )

        history_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), navy),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, pale_blue],
                ),
                ("BOX", (0, 0), (-1, -1), 0.6, border),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, border),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ])
        )

        story.append(history_table)

        # Trend chart, only when enough records exist
        if len(assessments) >= 2:

            story.append(
                Paragraph("Indicator Trend", section_style)
            )

            drawing = Drawing(440, 170)

            plot = LinePlot()
            plot.x = 42
            plot.y = 28
            plot.width = 360
            plot.height = 105

            plot.xValueAxis.valueMin = 0
            plot.xValueAxis.valueMax = len(assessments) - 1
            plot.xValueAxis.valueSteps = list(
                range(len(assessments))
            )
            plot.xValueAxis.labelTextFormat = lambda value: str(
                int(value) + 1
            )
            plot.xValueAxis.strokeColor = border

            plot.yValueAxis.valueMin = 0
            plot.yValueAxis.valueMax = 100
            plot.yValueAxis.valueSteps = [
                0, 20, 40, 60, 80, 100
            ]
            plot.yValueAxis.labelTextFormat = "%d%%"
            plot.yValueAxis.strokeColor = border

            plot.lines[0].strokeColor = teal
            plot.lines[0].strokeWidth = 2

            plot.data = [[
                (
                    index,
                    float(item.prediction_score) * 100,
                )
                for index, item in enumerate(assessments)
            ]]

            drawing.add(plot)

            drawing.add(
                String(
                    42,
                    145,
                    "Stored awareness indicator (%)",
                    fontName="Helvetica-Bold",
                    fontSize=8,
                    fillColor=navy,
                )
            )

            drawing.add(
                String(
                    42,
                    10,
                    "Assessments in chronological order",
                    fontName="Helvetica",
                    fontSize=7,
                    fillColor=muted,
                )
            )

            story.append(drawing)

    else:

        story.append(
            Paragraph("Assessment History", section_style)
        )

        story.append(
            Paragraph(
                "No assessments have been recorded yet. "
                "Complete a check-in to populate your future reports.",
                body_style,
            )
        )

    # --------------------------------------------------
    # Privacy disclaimer
    # --------------------------------------------------

    story.append(Spacer(1, 12))

    story.append(
        HRFlowable(
            width="100%",
            thickness=0.7,
            color=border,
            spaceBefore=4,
            spaceAfter=8,
        )
    )

    story.append(
        Paragraph("Privacy and Important Information", section_style)
    )

    story.append(
        Paragraph(
            "This report contains personal wellbeing information. "
            "Store it securely and share it only with people you trust. "
            "The system supports early awareness and preventive wellbeing; "
            "it does not diagnose mental health conditions. Scores are "
            "model-generated indicators, not clinical measurements or a "
            "substitute for professional advice.",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "This PDF is generated on request and is not permanently "
            "stored by this endpoint.",
            small_style,
        )
    )

    # Header/footer on every page
    def draw_page(canvas, document):

        canvas.saveState()

        page_width, page_height = A4

        canvas.setFillColor(navy)
        canvas.rect(
            0,
            page_height - 7 * mm,
            page_width,
            7 * mm,
            stroke=0,
            fill=1,
        )

        canvas.setStrokeColor(border)
        canvas.setLineWidth(0.5)

        canvas.line(
            18 * mm,
            13 * mm,
            page_width - 18 * mm,
            13 * mm,
        )

        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(muted)

        canvas.drawString(
            18 * mm,
            8 * mm,
            "PERSONAL WELLBEING DATA REPORT",
        )

        canvas.drawRightString(
            page_width - 18 * mm,
            8 * mm,
            f"Page {document.page}",
        )

        canvas.restoreState()

    document.build(
        story,
        onFirstPage=draw_page,
        onLaterPages=draw_page,
    )

    output.seek(0)

    filename = (
        f"my_wellbeing_report_"
        f"{generated_at.strftime('%Y-%m-%d')}.pdf"
    )

    response = send_file(
        output,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
        max_age=0,
    )

    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"

    return response


@auth_bp.route("/delete-account", methods=["DELETE"])
@jwt_required()
def delete_account():
    """Permanently delete the authenticated user's account and assessments."""
    identity = get_jwt_identity()

    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity"}), 401

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404

    try:
        # The User.assessments relationship is configured with
        # cascade="all, delete-orphan", so deleting the user removes
        # their associated assessment records in the same transaction.
        db.session.delete(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({
            "error": "Unable to delete account right now. Please try again."
        }), 500

    return jsonify({
        "message": "Your account and associated assessment data have been deleted."
    }), 200
