"""
Password Security Toolkit
A beginner-friendly cryptography project demonstrating:
- Password strength analysis
- Hashing with MD5, SHA-1, SHA-256, SHA-512, bcrypt
- Salting concepts
"""

from flask import Flask, request, jsonify, render_template
import hashlib
import bcrypt
import os
import re

app = Flask(__name__)


# ──────────────────────────────────────────────
# Password Strength Analysis
# ──────────────────────────────────────────────

def analyze_password(password: str) -> dict:
    """Analyze password strength and return a detailed report."""
    score = 0
    feedback = []
    checks = {}

    # Length checks
    length = len(password)
    checks["length_8"] = length >= 8
    checks["length_12"] = length >= 12
    checks["length_16"] = length >= 16

    if length < 8:
        feedback.append("Too short — use at least 8 characters.")
    elif length < 12:
        score += 1
        feedback.append("Decent length, but 12+ characters is stronger.")
    elif length < 16:
        score += 2
    else:
        score += 3

    # Character variety checks
    checks["has_uppercase"] = bool(re.search(r"[A-Z]", password))
    checks["has_lowercase"] = bool(re.search(r"[a-z]", password))
    checks["has_digit"] = bool(re.search(r"\d", password))
    checks["has_special"] = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", password))

    if checks["has_uppercase"]:
        score += 1
    else:
        feedback.append("Add uppercase letters (A–Z).")

    if checks["has_lowercase"]:
        score += 1
    else:
        feedback.append("Add lowercase letters (a–z).")

    if checks["has_digit"]:
        score += 1
    else:
        feedback.append("Add numbers (0–9).")

    if checks["has_special"]:
        score += 2
        feedback.append("Great — special characters add a lot of strength!")
    else:
        feedback.append("Add special characters like !@#$%^&*.")

    # Common password check
    common_passwords = [
        "password", "123456", "password123", "admin", "letmein",
        "qwerty", "abc123", "111111", "iloveyou", "welcome"
    ]
    checks["not_common"] = password.lower() not in common_passwords
    if not checks["not_common"]:
        score = 0
        feedback = ["This is one of the most common passwords — never use it!"]

    # Determine strength label
    if score <= 2:
        strength = "Weak"
        color = "weak"
    elif score <= 4:
        strength = "Fair"
        color = "fair"
    elif score <= 6:
        strength = "Good"
        color = "good"
    else:
        strength = "Strong"
        color = "strong"

    return {
        "score": score,
        "max_score": 8,
        "strength": strength,
        "color": color,
        "checks": checks,
        "feedback": feedback if feedback else ["Excellent password!"],
    }


# ──────────────────────────────────────────────
# Hashing Functions
# ──────────────────────────────────────────────

def hash_password(password: str) -> dict:
    """Hash the password using multiple algorithms to compare them."""
    encoded = password.encode("utf-8")

    # Generate a random salt for demonstration
    salt = os.urandom(16).hex()
    salted = (password + salt).encode("utf-8")

    # bcrypt (includes its own salt internally)
    bcrypt_hash = bcrypt.hashpw(encoded, bcrypt.gensalt()).decode("utf-8")

    return {
        "md5": hashlib.md5(encoded).hexdigest(),
        "sha1": hashlib.sha1(encoded).hexdigest(),
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "sha512": hashlib.sha512(encoded).hexdigest(),
        "salt": salt,
        "sha256_salted": hashlib.sha256(salted).hexdigest(),
        "bcrypt": bcrypt_hash,
    }


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    password = data.get("password", "")
    if not password:
        return jsonify({"error": "No password provided"}), 400

    strength = analyze_password(password)
    hashes = hash_password(password)

    return jsonify({
        "strength": strength,
        "hashes": hashes,
    })


if __name__ == "__main__":
    app.run(debug=True)
