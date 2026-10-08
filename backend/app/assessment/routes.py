import os
import subprocess
import tempfile

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import assessment_bp
from .services import (
    predict_depression,
    get_risk_level,
    generate_recommendations,
)
from .nlp_service import predict_nlp_risk
from .voice_service import extract_voice_features
from .facial_service import predict_facial_emotion

from app.extensions import db
from app.models.assessment import Assessment


# ------------------------------------------------------------
# FFmpeg configuration
# ------------------------------------------------------------

FFMPEG_PATH = (
    r"C:\Users\ADMIN\AppData\Local\Microsoft\WinGet"
    r"\Packages\Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-9.0.2-full_build-shared\bin\ffmpeg.exe"
)


@assessment_bp.route("/", methods=["POST"])
@jwt_required()
def submit_assessment():

    identity = get_jwt_identity()

    # --------------------------------------------------------
    # Read assessment data
    # --------------------------------------------------------

    if request.content_type and request.content_type.startswith(
        "multipart/form-data"
    ):
        data = request.form.to_dict()
    else:
        data = request.get_json(silent=True) or {}

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    required_fields = [
        "sleep_hours",
        "sleep_quality",
        "stress_level",
        "academic_pressure",
        "mood",
        "energy_level",
        "social_interaction",
        "exercise_minutes",
        "screen_time",
        "study_hours",
        "journal_text",
    ]

    # --------------------------------------------------------
    # Validate required fields
    # --------------------------------------------------------

    for field in required_fields:

        if data.get(field) is None:

            return jsonify({
                "error": f"{field} is required"
            }), 400

    # --------------------------------------------------------
    # Convert numerical form values
    # --------------------------------------------------------

    try:

        data["sleep_hours"] = float(
            data["sleep_hours"]
        )

        data["sleep_quality"] = int(
            data["sleep_quality"]
        )

        data["stress_level"] = int(
            data["stress_level"]
        )

        data["academic_pressure"] = int(
            data["academic_pressure"]
        )

        data["mood"] = int(
            data["mood"]
        )

        data["energy_level"] = int(
            data["energy_level"]
        )

        data["social_interaction"] = int(
            data["social_interaction"]
        )

        data["exercise_minutes"] = float(
            data["exercise_minutes"]
        )

        data["screen_time"] = float(
            data["screen_time"]
        )

        data["study_hours"] = float(
            data["study_hours"]
        )

    except (TypeError, ValueError):

        return jsonify({
            "error": "Invalid assessment values."
        }), 400

    # --------------------------------------------------------
    # Voice processing
    # --------------------------------------------------------

    voice_features = None
    voice_used = False

    voice_file = request.files.get(
        "voice_audio"
    )

    if voice_file and voice_file.filename:

        input_path = None
        output_path = None

        try:

            # ------------------------------------------------
            # Create temporary files
            # ------------------------------------------------

            with tempfile.NamedTemporaryFile(
                suffix=".webm",
                delete=False
            ) as input_temp:

                voice_file.save(
                    input_temp.name
                )

                input_path = input_temp.name

            with tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False
            ) as output_temp:

                output_path = output_temp.name

            # ------------------------------------------------
            # Convert WebM → WAV
            # ------------------------------------------------

            ffmpeg_command = [
                FFMPEG_PATH,
                "-y",
                "-i",
                input_path,
                "-ac",
                "1",
                "-ar",
                "16000",
                output_path,
            ]

            conversion = subprocess.run(
                ffmpeg_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            if conversion.returncode != 0:

                raise RuntimeError(
                    "Audio conversion failed."
                )

            # ------------------------------------------------
            # Read converted WAV
            # ------------------------------------------------

            with open(
                output_path,
                "rb"
            ) as audio_file:

                wav_bytes = (
                    audio_file.read()
                )

            # ------------------------------------------------
            # Extract acoustic features
            # ------------------------------------------------

            voice_features = (
                extract_voice_features(
                    wav_bytes
                )
            )

            voice_used = True

            print(
                "🎙️ Voice features extracted successfully."
            )

            print(
                "🎙️ Voice features:",
                voice_features
            )

        except Exception as exc:

            print(
                "🎙️ Voice processing error:",
                exc
            )

            voice_features = None
            voice_used = False

        finally:

            # ------------------------------------------------
            # Delete temporary audio files
            # ------------------------------------------------

            if (
                input_path
                and os.path.exists(input_path)
            ):

                os.remove(input_path)

            if (
                output_path
                and os.path.exists(output_path)
            ):

                os.remove(output_path)

    # --------------------------------------------------------
    # Facial emotion processing
    # --------------------------------------------------------

    facial_emotion = None
    facial_confidence = None
    facial_used = False

    facial_file = request.files.get(
        "facial_image"
    )

    if facial_file and facial_file.filename:

        try:

            facial_result = (
                predict_facial_emotion(
                    facial_file
                )
            )

            facial_emotion = (
                facial_result["emotion"]
            )

            facial_confidence = (
                facial_result["confidence"]
            )

            facial_used = True

            print(
                "📷 Facial emotion detected:",
                facial_emotion
            )

            print(
                "📷 Facial confidence:",
                facial_confidence
            )

        except Exception as exc:

            print(
                "📷 Facial processing error:",
                exc
            )

            facial_emotion = None
            facial_confidence = None
            facial_used = False

    # --------------------------------------------------------
    # Structured ML prediction
    # --------------------------------------------------------

    structured_prediction, structured_risk_score = (
        predict_depression(data)
    )

    # --------------------------------------------------------
    # NLP prediction
    # --------------------------------------------------------

    journal_text = data.get(
        "journal_text",
        ""
    )

    nlp_result = predict_nlp_risk(
        journal_text
    )

    # --------------------------------------------------------
    # Risk fusion
    #
    # Structured model = primary signal
    # NLP = supporting signal
    # Facial emotion = auxiliary affective signal
    #
    # IMPORTANT:
    # Facial emotion is NOT converted into a
    # depression/stress probability.
    # --------------------------------------------------------

    if nlp_result["valid"]:

        nlp_risk_score = (
            nlp_result["risk_score"]
        )

        final_risk_score = (
            (0.70 * structured_risk_score)
            + (0.30 * nlp_risk_score)
        )

        nlp_used = True

    else:

        nlp_risk_score = None

        final_risk_score = (
            structured_risk_score
        )

        nlp_used = False

    # --------------------------------------------------------
    # Final risk level
    # --------------------------------------------------------

    risk_level = get_risk_level(
        final_risk_score
    )

    # --------------------------------------------------------
    # Recommendations
    # --------------------------------------------------------

    recommendations = (
        generate_recommendations(
            data,
            final_risk_score
        )
    )

    # --------------------------------------------------------
    # Save assessment
    # --------------------------------------------------------

    assessment = Assessment(

        user_id=identity,

        sleep_hours=data.get(
            "sleep_hours"
        ),

        sleep_quality=data.get(
            "sleep_quality"
        ),

        stress_level=data.get(
            "stress_level"
        ),

        academic_pressure=data.get(
            "academic_pressure"
        ),

        mood=data.get(
            "mood"
        ),

        energy_level=data.get(
            "energy_level"
        ),

        social_interaction=data.get(
            "social_interaction"
        ),

        exercise_minutes=data.get(
            "exercise_minutes"
        ),

        screen_time=data.get(
            "screen_time"
        ),

        study_hours=data.get(
            "study_hours"
        ),

        journal_text=journal_text,

        prediction_score=final_risk_score,

        facial_emotion=facial_emotion,

        facial_confidence=facial_confidence,

        facial_used=facial_used,
    )

    db.session.add(
        assessment
    )

    db.session.commit()

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return jsonify({

        "message":
            "Assessment submitted successfully",

        # Final risk result
        "prediction":
            structured_prediction,

        "risk_score":
            round(
                final_risk_score * 100,
                2
            ),

        "risk_level":
            risk_level,

        # Structured signal
        "structured_risk_score":
            round(
                structured_risk_score * 100,
                2
            ),

        # NLP signal
        "nlp_risk_score":
            (
                round(
                    nlp_risk_score * 100,
                    2
                )
                if nlp_risk_score is not None
                else None
            ),

        "nlp_used":
            nlp_used,

        # Facial signal
        "facial_used":
            facial_used,

        "facial_emotion":
            facial_emotion,

        "facial_confidence":
            (
                round(
                    facial_confidence,
                    4
                )
                if facial_confidence is not None
                else None
            ),

        # Voice information
        "voice_used":
            voice_used,

        "voice_features":
            voice_features,

        # NLP validation
        "nlp_validation":
            nlp_result.get(
                "validation"
            ),

        # Recommendations
        "recommendations":
            recommendations

    }), 201


@assessment_bp.route(
    "/history",
    methods=["GET"]
)
@jwt_required()
def assessment_history():

    identity = get_jwt_identity()

    assessments = (
        Assessment.query
        .filter_by(
            user_id=identity
        )
        .order_by(
            Assessment.created_at.desc()
        )
        .all()
    )

    result = []

    for assessment in assessments:

        result.append({

            "id":
                assessment.id,

            "prediction_score":
                round(
                    assessment.prediction_score * 100,
                    2
                ),

            "sleep_hours":
                assessment.sleep_hours,

            "sleep_quality":
                assessment.sleep_quality,

            "stress_level":
                assessment.stress_level,

            "academic_pressure":
                assessment.academic_pressure,

            "mood":
                assessment.mood,

            "energy_level":
                assessment.energy_level,

            "social_interaction":
                assessment.social_interaction,

            "exercise_minutes":
                assessment.exercise_minutes,

            "screen_time":
                assessment.screen_time,

            "study_hours":
                assessment.study_hours,

            "journal_text":
                assessment.journal_text,

            # Facial information
            "facial_emotion":
                assessment.facial_emotion,

            "facial_confidence":
                assessment.facial_confidence,

            "facial_used":
                assessment.facial_used,

            "created_at":
                assessment.created_at.isoformat()
        })

    return jsonify({

        "count":
            len(result),

        "assessments":
            result

    }), 200