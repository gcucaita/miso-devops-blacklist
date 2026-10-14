from app import create_app

application = create_app()
app = application

if __name__ == "__main__":
    application.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )