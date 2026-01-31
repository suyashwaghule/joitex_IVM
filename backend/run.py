import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Debug mode only in development
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug)
