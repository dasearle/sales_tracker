"""
Elastic Beanstalk entry point.
EB looks for 'application' callable by default.
"""
from app import create_app

application = create_app()

if __name__ == "__main__":
    application.run(debug=True)
