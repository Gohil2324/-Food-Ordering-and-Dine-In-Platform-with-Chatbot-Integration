from flask import Blueprint, request, jsonify
import re  # For input validation

payment_bp = Blueprint("payment", __name__)


def validate_card_details(card_number, expiry, cvv):
    """ Validate card details before processing payment """
    if not re.match(r"^\d{16}$", card_number):
        return "Card number must be exactly 16 digits."

    if not re.match(r"^\d{4}$", expiry):
        return "Expiry date must be 4 digits in MMYY format."

    if not re.match(r"^\d{3}$", cvv):
        return "CVV must be exactly 3 digits."

    return None  # No errors


def validate_paypal_email(email):
    """ Validate PayPal email format """
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return "Invalid PayPal email format."

    return None  # No errors


def process_payment(order_id, amount, payment_method, payment_details):
    """ Simulate Payment Processing """
    if payment_method == "card":
        error = validate_card_details(
            payment_details.get("card_number"),
            payment_details.get("expiry"),
            payment_details.get("cvv")
        )
        if error:
            return {"status": "failed", "message": error}

        return {"status": "success", "order_id": order_id, "amount": amount, "method": "card"}

    elif payment_method == "paypal":
        error = validate_paypal_email(payment_details.get("paypal_email"))
        if error:
            return {"status": "failed", "message": error}

        return {"status": "success", "order_id": order_id, "amount": amount, "method": "paypal"}

    return {"status": "failed", "message": "Unsupported payment method"}


@payment_bp.route('/pay', methods=['POST'])
def pay():
    data = request.json
    order_id = data.get('order_id')
    amount = data.get('amount')
    payment_method = data.get('payment_method')
    payment_details = data.get('payment_details', {})

    if not order_id or not amount or not payment_method:
        return jsonify({"error": "Invalid payment data"}), 400

    result = process_payment(order_id, amount, payment_method, payment_details)
    return jsonify(result)
