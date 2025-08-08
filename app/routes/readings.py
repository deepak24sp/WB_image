from flask import Blueprint, jsonify,request
from sqlalchemy import text
from app.extensions import db
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)

readings_bp = Blueprint('readings', __name__)


@readings_bp.route('/reading-ds', methods=['GET'])
@jwt_required()
def get_readings_ds():
    current_user = get_jwt_identity()
    current_user_id = int(get_jwt_identity())
    # current_user_id = current_user["user_id"]

    # Pagination params
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 12))
    offset = (page - 1) * per_page

    # Date range
    start_date = '20.05.2025'
    end_date = '17.06.2025'

    # ✅ Query: main data (LIMIT + OFFSET)
    main_query = text("""
        SELECT id, consumer_number, image_url, meter_has_decimal
        FROM reading_ds
        WHERE assigned_to_user_id = :user_id
          AND meter_has_decimal IS NULL
          AND TO_DATE(updated_at, 'DD.MM.YYYY') BETWEEN TO_DATE(:start_date, 'DD.MM.YYYY') AND TO_DATE(:end_date, 'DD.MM.YYYY')
        ORDER BY id ASC
        LIMIT :limit OFFSET :offset
    """)

    result = db.session.execute(main_query, {
        'user_id': current_user_id,
        'start_date': start_date,
        'end_date': end_date,
        'limit': per_page,
        'offset': offset
    }).mappings().all()
    data = [dict(row) for row in result]

    count_query = text("""
        SELECT COUNT(*) FROM reading_ds
        WHERE assigned_to_user_id = :user_id
          AND meter_has_decimal IS NULL
          AND TO_DATE(updated_at, 'DD.MM.YYYY') BETWEEN TO_DATE(:start_date, 'DD.MM.YYYY') AND TO_DATE(:end_date, 'DD.MM.YYYY')
    """)

    total = db.session.execute(count_query, {
        'user_id': current_user_id,
        'start_date': start_date,
        'end_date': end_date
    }).scalar()

    pages = (total + per_page - 1) // per_page  # total pages

    return jsonify({
        'data': data,
        'total': total,
        'pages': pages,
        'current_page': page
    })



@readings_bp.route("/reading-ds/<int:id>/decimal", methods=["PATCH"])
def update_decimal(id):
    data = request.get_json()

    is_decimal = data.get('meter_has_decimal')
    prev_reading = data.get('prev_reading')  # can be None

    if is_decimal is None:
        return jsonify({'error': 'Missing meter_has_decimal field'}), 400

    # Check if record exists
    check_query = text("SELECT id FROM reading_ds WHERE id = :id")
    exists = db.session.execute(check_query, {"id": id}).first()

    if not exists:
        return jsonify({'error': 'Reading not found'}), 404

    # Build update query dynamically
    if prev_reading is not None:
        update_query = text("""
            UPDATE reading_ds
            SET meter_has_decimal = :is_decimal,
                prev_reading = :prev_reading
            WHERE id = :id
        """)
        db.session.execute(update_query, {
            "is_decimal": is_decimal,
            "prev_reading": prev_reading,
            "id": id
        })
    else:
        update_query = text("""
            UPDATE reading_ds
            SET meter_has_decimal = :is_decimal
            WHERE id = :id
        """)
        db.session.execute(update_query, {
            "is_decimal": is_decimal,
            "id": id
        })

    db.session.commit()

    return jsonify({
        "message": "Updated successfully",
        "id": id,
        "meter_has_decimal": is_decimal,
        "prev_reading": prev_reading
    })


@readings_bp.route('/qclogin', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    USERS = [
    {"email": "suchet@sujanix.com",        "password": "Sujanix#123", "id": 8},
    {"email": "mounika@sujanix.com",       "password": "Sujanix#123", "id": 35},
    {"email": "abishek@sujanix.com",       "password": "Sujanix#123", "id": 37},
    {"email": "chirag@sujanix.com",        "password": "Sujanix#123", "id": 38},
    {"email": "sunil@sujanix.com",         "password": "Sujanix#123", "id": 39},
    {"email": "deepak@sujanix.com",        "password": "Sujanix#123", "id": 40},
    {"email": "ajith@sujanix.com",         "password": "Sujanix#123", "id": 41},
    {"email": "suhasini@sujanix.com",      "password": "Sujanix#123", "id": 42},
    {"email": "hariprashanth@sujanix.com", "password": "Sujanix#123", "id": 43},
    {"email": "poornima@sujanix.com",      "password": "Sujanix#123", "id": 44},
    {"email": "sunilv@sujanix.com",        "password": "Sujanix#123", "id": 45},
    {"email": "indra@sujanix.com",         "password": "Sujanix#123", "id": 46},
    {"email": "deepaksp@sujanix.com",      "password": "Sujanix#123", "id": 47},
    {"email": "noor@sujanix.com",          "password": "Sujanix#123", "id": 48},
    {"email": "madhura@sujanix.com",       "password": "Sujanix#123", "id": 49}
    ]



    # Find user by email & password
    user = next((u for u in USERS if u["email"] == email and u["password"] == password), None)

    if not user:
        return jsonify({"status": "error", "msg": "Invalid email or password"}), 401

    access_token=create_access_token(identity=str(user["id"]))

    return jsonify({
        "status": "success",
        "access_token": access_token
    }), 200

