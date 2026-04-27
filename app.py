from app import create_app


# Application entry point for local development.
app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
