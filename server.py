import os
import threading
import pymysql
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='/static')

# MySQL Configuration
db_host = 'localhost'
db_user = 'root'
db_password = ''
db_name = 'booking'
conn = pymysql.connect(host=db_host, user=db_user, password=db_password, db=db_name, cursorclass=pymysql.cursors.DictCursor)

# Establish MySQL connection
def get_db():
    return pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

# Route for admin panel
@app.route('/admin')
def index():
    # Query to get total registrations
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) AS total_registrations FROM registration')
    result = cursor.fetchone()
    total_registrations = result['total_registrations']

    # Query to get all registrations
    cursor.execute('SELECT * FROM registration')
    registrations = cursor.fetchall()
    cursor.close()

    return render_template('admin.html', total_registrations=total_registrations, registrations=registrations)

# Route for handling registrations
@app.route('/confirmed', methods=['GET', 'POST'])
def confirmed():
    # Query to get total confirmed registrations
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) AS total_confirmed FROM confirmed')
    result = cursor.fetchone()
    total_confirmed = result['total_confirmed']

    # Query to get all confirmed registrations
    cursor.execute('SELECT * FROM confirmed')
    confirmed_registrations = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        created_at = request.form['created_at']  # Assuming 'created_at' is passed as a hidden field in the form
        # Fetch the registration details from the 'registration' table based on created_at
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM registration WHERE created_at = %s', (created_at,))
        registration = cursor.fetchone()

        if registration:
            # Insert the registration into the 'confirmed' table
            cursor.execute('INSERT INTO confirmed (name, mobile, location, date, created_at) VALUES (%s, %s, %s, %s, %s)',
                           (registration['name'], registration['mobile'], registration['location'], registration['date'], registration['created_at']))

            # Delete the registration from the 'registration' table based on created_at
            cursor.execute('DELETE FROM registration WHERE created_at = %s', (created_at,))

            # Commit the transaction
            conn.commit()

        # Close the cursor
        cursor.close()

        # Redirect back to the admin page
        return redirect('/admin')

    return render_template('confirmed.html', total_confirmed=total_confirmed, confirmed_registrations=confirmed_registrations)

# Route for deleting registrations
@app.route('/delete', methods=['POST'])
def delete():
    if request.method == 'POST':
        image_location = 'static/'
        image_location += request.form['image_location']
        print("Image Location to Delete:", image_location)
        if os.path.exists(image_location):
            os.remove(image_location)
            parts = image_location.rsplit('/', 1)
            image_location = parts[0] + '\\' + parts[1]
            print("location to delete from database", image_location)
            db = get_db()
            cursor = db.cursor()
            cursor.execute('DELETE FROM image WHERE location = %s', (image_location,))
            db.commit()
            print("Image Location to Delete:", image_location)
            cursor.close()
            db.close()
    return redirect(url_for('upload'))

# Define the directory where you want to save the plot file
save_directory = 'C:/xampp/htdocs/static'

def generate_description(booking_counts, confirmed_counts):
    # Calculate the growth rate of bookings and confirmed entries
    booking_growth_rate = 0
    confirmed_growth_rate = 0

    if booking_counts[0] != 0:
        booking_growth_rate = (booking_counts[-1] - booking_counts[0]) / booking_counts[0] * 100

    if confirmed_counts[0] != 0:
        confirmed_growth_rate = (confirmed_counts[-1] - confirmed_counts[0]) / confirmed_counts[0] * 100

# Calculate the growth or decline rate compared to last month
    if booking_counts[-2] != 0:
        booking_growth_last_month = (booking_counts[-1] - booking_counts[-2]) / booking_counts[-2] * 100
    else:
        booking_growth_last_month = 0
# Calculate the growth or decline rate compared to last month
    if confirmed_counts[-2] != 0:
        confirmed_growth_last_month = (confirmed_counts[-1] - confirmed_counts[-2]) / confirmed_counts[-2] * 100
    else:
        confirmed_growth_last_month = 0


    # Define threshold values for growth rates
    high_growth_threshold = 10  # arbitrary threshold for high growth rate
    moderate_growth_threshold = 5  # arbitrary threshold for moderate growth rate

    # Generate description based on growth rates
    if booking_growth_rate > high_growth_threshold and confirmed_growth_rate > high_growth_threshold:
        description = "The bookings and confirmed entries have experienced significant growth, indicating a strong demand."
    elif booking_growth_rate > moderate_growth_threshold and confirmed_growth_rate > moderate_growth_threshold:
        description = "Both bookings and confirmed entries show moderate growth, suggesting steady progress."
    else:
        description = "The growth rate of bookings and confirmed entries is relatively stable."

    # Generate description based on growth or decline compared to last month
    if booking_growth_last_month > 0 and confirmed_growth_last_month > 0:
        trend_description = "Both bookings and confirmations have increased compared to last month."
    elif booking_growth_last_month < 0 and confirmed_growth_last_month < 0:
        trend_description = "Both bookings and confirmations have decreased compared to last month."
    else:
        trend_description = "There has been a mixed trend in bookings and confirmations compared to last month."

    # Additional motivating line
    motivation = "Keep up the good work! Consistency is key to achieving your goals."

    # Concatenate all descriptions
    description = f"{description} {trend_description} {motivation}"

    return description

# Route for statistics
# Route for statistics
@app.route('/statistics', methods=['GET', 'POST'])
def statistics():
    # Define a function to generate and save the plot
    def generate_plot():
        cursor = conn.cursor()
        cursor.execute('SELECT MONTH(date) AS month, COUNT(*) AS count FROM registration GROUP BY month')
        booking_results = cursor.fetchall()

        cursor.execute('SELECT MONTH(created_at) AS month, COUNT(*) AS count FROM confirmed GROUP BY month')
        confirmed_results = cursor.fetchall()

        months = np.arange(1, 13)
        booking_counts = [0] * 12
        confirmed_counts = [0] * 12

        for row in booking_results:
            month = row['month']
            count = row['count']
            booking_counts[month - 1] = count

        for row in confirmed_results:
            month = row['month']
            count = row['count']
            confirmed_counts[month - 1] = count

        # Plotting
        plt.figure(figsize=(8, 4))  # Adjust width and height of the plot
        labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        colors = ['orange', 'green', 'blue', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan', 'magenta', 'yellow']
        plt.pie(booking_counts, labels=labels, colors=colors, autopct='%1.1f%%')
        plt.title('Monthly Bookings Distribution')
        plt.tight_layout()

        # Construct the file path using the specified directory
        graph_file = os.path.join(save_directory, 'monthly_bookings_pie.png')

        # Save the plot to the specified directory
        plt.savefig(graph_file)
        plt.close()

        return graph_file, booking_counts, confirmed_counts  # Return booking_counts and confirmed_counts

    # Call the function to generate and save the plot
    graph_file, booking_counts, confirmed_counts = generate_plot()

    # Generate the description
    description = generate_description(booking_counts, confirmed_counts)

    # Pass the description to the template
    return render_template('statistics.html', graph_file=graph_file, description=description)

# Route for uploading images
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        category = request.form['category']
        url = request.form['url']
        if 'location' in request.files:
            file = request.files['location']
            if category and url and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join('static/uploads', filename)
                if os.path.exists(file_path):
                    return render_template('already_uploaded.html')
                else:
                    file.save(file_path)
                    db = get_db()
                    cursor = db.cursor()
                    cursor.execute('INSERT INTO image (category, location, url) VALUES (%s, %s, %s)', (category, file_path, url))
                    db.commit()
                    cursor.close()
                    db.close()
                    return redirect(url_for('display_images'))
            else:
                return "Please fill in all required fields."
    image_locations = get_image_locations()
    return render_template('upload.html', image_locations=image_locations)

def get_image_locations():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT category, location, url FROM image')
    image_locations = cursor.fetchall()
    # Format the image paths properly
    formatted_locations = [(category, location.replace('\\', '/').replace('static/', '')) for category, location in image_locations]
    cursor.close()
    db.close()
    return formatted_locations

# Route for displaying uploaded images
@app.route('/index')  # Change this route to '/index'
def display_images():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT category, location, url FROM image')
    image_locations = cursor.fetchall()
    print("Image Locations:", image_locations)
    cursor.close()
    db.close()
    return render_template('index.html', image_locations=image_locations)

# Route for deleting images
@app.route('/delete_image', methods=['POST'])
def delete_image():
    if request.method == 'POST':
        image_location = 'static/'
        image_location += request.form['image_location']
        print("Image Location to Delete:", image_location)
        if os.path.exists(image_location):
            os.remove(image_location)
            parts = image_location.rsplit('/', 1)
            image_location = parts[0] + '\\' + parts[1]
            print("location to delete from database", image_location)
            db = get_db()
            cursor = db.cursor()
            cursor.execute('DELETE FROM image WHERE location = %s', (image_location,))
            db.commit()
            print("Image Location to Delete:", image_location)
            cursor.close()
            db.close()
    return redirect(url_for('upload'))

@app.route('/cancelled', methods=['GET', 'POST'])
def cancelled():
    # Query to get total cancelled registrations
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) AS total_cancelled FROM cancelled')
    result = cursor.fetchone()
    total_cancelled = result['total_cancelled']

    # Query to get all cancelled registrations
    cursor.execute('SELECT * FROM cancelled')
    cancelled_registrations = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        created_at = request.form['created_at']  # Assuming 'created_at' is passed as a hidden field in the form
        # Fetch the registration details from the 'registration' table based on created_at
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM registration WHERE created_at = %s', (created_at,))
        registration = cursor.fetchone()

        if registration:
            # Insert the registration into the 'cancelled' table
            cursor.execute('INSERT INTO cancelled (name, mobile, location, date, created_at) VALUES (%s, %s, %s, %s, %s)',
                           (registration['name'], registration['mobile'], registration['location'], registration['date'], registration['created_at']))

            # Delete the registration from the 'registration' table based on created_at
            cursor.execute('DELETE FROM registration WHERE created_at = %s', (created_at,))

            # Commit the transaction
            conn.commit()

        # Close the cursor
        cursor.close()

        # Redirect back to the admin page
        return redirect('/admin')

    return render_template('cancelled.html', total_cancelled=total_cancelled, cancelled_registrations=cancelled_registrations)

if __name__ == '__main__':
    app.run(debug=True)
