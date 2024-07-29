from demo.db import close_db, init_db, get_db
import os
from flask import Flask, render_template, request
import re

def init_app(app):
    with app.app_context():
        app.teardown_appcontext(close_db)
        init_db()

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, template_folder='demo/templates')
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join('demo/instance', 'demo.sql'),
        # CORS_HEADERS = 'Content-Type',
        )
    print(os.path.join(app.instance_path))

    # ensure the instance folder exists
    try:
        path_instance = 'demo/instance'
        os.makedirs(path_instance)
    except OSError:
        pass


    init_app(app)

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/demo')
    def demo():
        db = get_db()
        texts = db.execute(
            'SELECT * FROM texts'
        ).fetchall()
        return render_template('base.html', texts=texts)


    @app.route('/contact')
    def contact():
        return render_template('contacts.html')

    def get_text(id):
        post = get_db().execute(
            'SELECT * FROM texts WHERE id = ?',
            (id,)
        ).fetchone()

        return post

    def check_url(info): 
        processed = []
        if '$' in info:
            items = info.split('$')

            for i, x in enumerate(items):
                if i == 1:
                    x = '<a href="'+items[i]+'">'
                    processed.append(x)
                elif i == 3:
                    x = " </a> " + items[i]
                    processed.append(x)
                else:
                    processed.append(x)
            return ' '.join(processed).strip()
        else:
            return info

    def check_string(text, span):
        PUNCT = re.compile(r'((\.)(\w|\s|\n))')
        span = PUNCT.sub(r' \1 ', span)
        text = PUNCT.sub(r' \1 ', text)
        span = span.strip()
        s = span.split(' ')
        t = text.split(' ')

        for i in range(0, len(t)):
            index1 = i
            index2 = i+len(s)
            if index2 < len(t):
                g = ' '.join([t[x] for x in range(index1, index2)])
            else:
                g = ' '.join([t[x] for x in range(index1, len(t))])

            if g == span:
                list_index=[x for x in range(index1, index2)]
                return list_index, t

    def add_mark(tokens, list_index):
        processed = []
        for i, t in enumerate(tokens):
            if i in list_index:
                p = "<u><mark>" + t + "</mark></u>"
                processed.append(p)
            else:
                p = '{:s}'.format(t)
                processed.append(p)
        return processed

    def get_all(text):
        text_processed = ''
        if ';' in text['span']:
            print(text['span'])
            list_s = text['span'].split(';')
            for span in list_s:
                if span == list_s[0]:
                    print(span)
                    list_index, tokens = check_string(text['text2check'], span)
                    processed = add_mark(tokens, list_index)
                    text_processed = ' '.join(processed).strip()
                    print(text_processed)
                else:
                    print(span)
                    list_index, tokens = check_string(text_processed, span)

                    processed = add_mark(tokens, list_index)
                    text_processed = ' '.join(processed).strip()
        else:
            list_index, tokens = check_string(text['text2check'], text['span'])
            processed = add_mark(tokens, list_index)
            text_processed = ' '.join(processed).strip()
        return text_processed

    @app.route('/<int:id>/get_check', methods=['POST', 'GET'])
    def get_check(id):
        text = get_text(id)
        info = check_url(text['info'])
        if text['span'] == '':
            return render_template('check.html', text=text, info=info)
        else:
            text_processed = get_all(text)
            return render_template('check.html', text=text, text_processed=text_processed,
                               info=info
                               )

    @app.route('/<int:id>/get_alternative', methods=['POST', 'GET'])
    def get_alternative(id):
        text = get_text(id)
        info = check_url(text['info'])
        value = request.form['x']
        if text['span'] == '':
            return render_template('check.html', text=text)
        else:
            text_processed = get_all(text)

        db = get_db()
        if value.endswith('1'):
            c = text['count1']+1
            db.execute(
                'UPDATE texts SET count1 = ?'
                ' WHERE id = ?',
                (c, id)
            )
            db.commit()
        elif value.endswith('2'):
                c = text['count2'] + 1
                db.execute(
                    'UPDATE texts SET count2 = ?'
                    ' WHERE id = ?',
                    (c, id)
                )
                db.commit()
        elif value.endswith('3'):
                c = text['count3'] + 1
                db.execute(
                    'UPDATE texts SET count3 = ?'
                    ' WHERE id = ?',
                    (c, id)
                )
                db.commit()
        else:
            c = text['count4']+1
            db.execute(
                'UPDATE texts SET count4 = ?'
                ' WHERE id = ?',
                (c, id)
            )
            db.commit()
        db.close()
        return render_template('check.html', text=text, x=text[value], text_processed=text_processed, info=info)

    @app.route('/<int:id>/get_rewrite', methods=('GET', 'POST'))
    def get_rewrite(id):
        text = get_text(id)
        sep = ' | '
        existing_texts = text['manual_rewrite']

        if request.method == 'POST':
            x = request.form['manual_rewrite']
            db = get_db()

            new_texts = existing_texts+sep+x
            db.execute(
                    'UPDATE texts SET manual_rewrite = ?'
                    ' WHERE id = ?',
                    (new_texts, id)
                )
            db.commit()
            db.close()
            return render_template('index.html', x=x, text=text)

        return render_template('rewrite.html', text=text)



    app.add_url_rule('/', endpoint='home')

    return app


app = create_app()
app.run(host="10.110.0.2",port=5000,debug=True)
