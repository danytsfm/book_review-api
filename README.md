Description of project1.

Requirements: Flask
	      Flask-Session
	      psycopg2-binary
	      SQLAlchemy
	      passlib

The project1 is an introduction to SQL, Python (flask).
The project has 9 HTML files,  1 CSS file, 3 images, 2 classes which are: class Users, class Book. In the classes, you will find
methods to select and insert users and books respectively. 
It also includes a CSV file to upload the books to the database and an import.py file that contains a function to upload the CSV file detached from the project.
API access: '/api/readanview/<string:isbn>' it will return a JSON format result as follow:
{
  "author": "Raymond E. Feist", 
  "average": [
    4
  ], 
  "isbn": "0380795272  ", 
  "reviews_count": [
    5
  ], 
  "title": "Krondor: The Betrayal", 
  "year": "1998 "
}

	