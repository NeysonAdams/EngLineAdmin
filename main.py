import os

from server_init import app, build_sample_db, add_questions,add_words, test_build

if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])

    #if not os.path.exists(database_path):
    # test_build()
    #build_sample_db()
    #add_questions()
    #add_words()

    # Start app
    app.run( host = '0.0.0.0', port = 4444, debug=True)
