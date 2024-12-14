from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL database configuration
DB_CONFIG = {
    'host': 'team5hackathon.mysql.pythonanywhere-services.com',
    'user': 'team5hackathon',
    'password': 'pranathi',
    'database': 'team5hackathon$mediafusiondb'
}

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    return pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        cursorclass=pymysql.cursors.DictCursor
    )

def post_to_facebook(content):
    """Function to post content to Facebook using Facebook Graph API."""
    # Replace with actual API call
    # Example endpoint: 'https://graph.facebook.com/{page-id}/feed'
    api_url = 'https://graph.facebook.com/v12.0/me/feed'
    access_token = 'your_facebook_access_token'
    response = requests.post(api_url, data={'message': content, 'access_token': access_token})
    return response.json()

def post_to_instagram(content):
    """Function to post content to Instagram using Instagram Graph API."""
    # Replace with actual API call
    api_url = 'https://graph.facebook.com/v12.0/{instagram-user-id}/media'
    access_token = 'your_instagram_access_token'
    response = requests.post(api_url, data={'caption': content, 'access_token': access_token})
    return response.json()

def post_to_whatsapp(content):
    """Function to post content to WhatsApp using WhatsApp Business API."""
    # Replace with actual API call
    api_url = 'https://api.whatsapp.com/send'
    headers = {'Authorization': 'Bearer your_whatsapp_access_token'}
    response = requests.post(api_url, json={'message': content}, headers=headers)
    return response.json()

@app.route('/')
def home():
    """Renders the home page."""
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Query the database for the user
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
                user = cursor.fetchone()

        if user:
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Insert user details into the database
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        'INSERT INTO users (username, password, email) VALUES (%s, %s, %s)',
                        (username, password, email)
                    )
                    conn.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except pymysql.IntegrityError:
            flash('Username or email already exists.', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/post', methods=['GET', 'POST'])
def post():
    """Handles posting to multiple platforms."""
    if request.method == 'POST':
        content = request.form['content']
        platforms = request.form.getlist('platforms')

        results = {}
        for platform in platforms:
            if platform == 'facebook':
                results['facebook'] = post_to_facebook(content)
            elif platform == 'instagram':
                results['instagram'] = post_to_instagram(content)
            elif platform == 'whatsapp':
                results['whatsapp'] = post_to_whatsapp(content)

        flash('Post sent successfully to the selected platforms!', 'success')
        return render_template('post_result.html', results=results)

    return render_template('post.html')

if __name__ == '__main__':
    app.run(debug=True)
