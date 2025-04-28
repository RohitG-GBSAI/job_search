from app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    # configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///database.db")

