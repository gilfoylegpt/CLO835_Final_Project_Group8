from flask import Flask, render_template, request
from pymysql import connections
import os
import random
import argparse
import logging
import boto3
from botocore.exceptions import ClientError
import base64

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get configuration from ConfigMap
BACKGROUND_IMAGE_LOCATION = os.environ.get("BACKGROUND_IMAGE_LOCATION")
logger.info("=== Background Image Configuration ===")
logger.info(f"Background image location from ConfigMap: {BACKGROUND_IMAGE_LOCATION}")
if not BACKGROUND_IMAGE_LOCATION:
    logger.warning("No background image location found in ConfigMap")
else:
    logger.info(f"Background image will be loaded from S3 bucket: {BACKGROUND_IMAGE_LOCATION}")

# Initialize S3 client
s3_client = boto3.client('s3')

def get_background_image():
    try:
        if BACKGROUND_IMAGE_LOCATION:
            # Parse S3 URL
            bucket_name = BACKGROUND_IMAGE_LOCATION.split('/')[2]
            object_key = '/'.join(BACKGROUND_IMAGE_LOCATION.split('/')[3:])
            
            logger.info(f"Attempting to fetch image from S3 bucket: {bucket_name}")
            logger.info(f"Image object key: {object_key}")
            
            # Get the object from S3
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            image_data = response['Body'].read()
            logger.info(f"Successfully retrieved background image from S3: {BACKGROUND_IMAGE_LOCATION}")
            logger.info(f"Image size: {len(image_data)} bytes")
            return base64.b64encode(image_data).decode('utf-8')
        else:
            logger.warning("No background image location specified in ConfigMap")
            return None
    except ClientError as e:
        logger.error(f"Error accessing S3: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while fetching background image: {str(e)}")
        return None

# Get database credentials from Kubernetes secrets
DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER")
DBPWD = os.environ.get("DBPWD")
DATABASE = os.environ.get("DATABASE") or "employees"
COLOR_FROM_ENV = os.environ.get('APP_COLOR') or "lime"
DBPORT = int(os.environ.get("DBPORT"))

# Log database configuration (without sensitive information)
logger.info("=== Database Configuration ===")
logger.info(f"Database host: {DBHOST}")
logger.info(f"Database name: {DATABASE}")
logger.info(f"Database port: {DBPORT}")
if not DBUSER or not DBPWD:
    logger.error("Database credentials not found in Kubernetes secrets")
    raise ValueError("Database credentials are required")

# Create a connection to the MySQL database
try:
    db_conn = connections.Connection(
        host=DBHOST,
        port=DBPORT,
        user=DBUSER,
        password=DBPWD, 
        db=DATABASE
    )
    logger.info("Successfully connected to MySQL database")
except Exception as e:
    logger.error(f"Failed to connect to MySQL database: {str(e)}")
    raise

output = {}
table = 'employee';

# Define the supported color codes
color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}


# Create a string of supported colors
SUPPORTED_COLORS = ",".join(color_codes.keys())

# Generate a random color
COLOR = random.choice(["red", "green", "blue", "blue2", "darkblue", "pink", "lime"])


@app.route("/", methods=['GET', 'POST'])
def home():
    background_image = get_background_image()
    return render_template('addemp.html', color=color_codes[COLOR], background_image=background_image)

@app.route("/about", methods=['GET','POST'])
def about():
    return render_template('about.html', color=color_codes[COLOR])
    
@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

  
    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        
        cursor.execute(insert_sql,(emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('addempoutput.html', name=emp_name, color=color_codes[COLOR])

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", color=color_codes[COLOR])


@app.route("/fetchdata", methods=['GET','POST'])
def FetchData():
    emp_id = request.form['emp_id']

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql,(emp_id))
        result = cursor.fetchone()
        
        # Add No Employee found form
        output["emp_id"] = result[0]
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]
        
    except Exception as e:
        print(e)

    finally:
        cursor.close()

    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"],
                           lname=output["last_name"], interest=output["primary_skills"], location=output["location"], color=color_codes[COLOR])

if __name__ == '__main__':
    
    # Check for Command Line Parameters for color
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', required=False)
    args = parser.parse_args()

    if args.color:
        print("Color from command line argument =" + args.color)
        COLOR = args.color
        if COLOR_FROM_ENV:
            print("A color was set through environment variable -" + COLOR_FROM_ENV + ". However, color from command line argument takes precendence.")
    elif COLOR_FROM_ENV:
        print("No Command line argument. Color from environment variable =" + COLOR_FROM_ENV)
        COLOR = COLOR_FROM_ENV
    else:
        print("No command line argument or environment variable. Picking a Random Color =" + COLOR)

    # Check if input color is a supported one
    if COLOR not in color_codes:
        print("Color not supported. Received '" + COLOR + "' expected one of " + SUPPORTED_COLORS)
        exit(1)

    app.run(host='0.0.0.0',port=81,debug=True)
