# Amazon Project - Neo4j CRUD

## Student
Mason Ford

## Course
SDC435L

## Project Description

This project uses Python and Neo4j to create and manage an Amazon product
review database. The program imports review data from a JSON file and
creates nodes and relationships in a Neo4j database.

## Technologies Used

- Python
- Neo4j
- Cypher
- JSON

## Database

Database Name: `Amazon-Project`

The program connects to a local Neo4j database using:

- URI: `neo4j://localhost:7687`
- Database: `Amazon-Project`

## Data

The project uses the `dataset_en_dev.json` file containing 5,000 Amazon
review records.

The imported data is used to create:

- Category nodes
- Product nodes
- Review nodes
- Reviewer nodes

The relationships include:

- Product -> Category
- Reviewer -> Review
- Product -> Review

## Program Features

The Python program provides a menu-driven interface with:

1. Import JSON data
2. Create a node
3. Read a node
4. Update a node
5. Create a relationship
6. Count products by category
7. Count reviews by reviewer
8. Delete a category
9. Delete all relationships
10. Delete all nodes

The program also includes input validation and comments explaining the
different sections of the code.

## How to Run

1. Start the Neo4j DBMS.
2. Make sure the `Amazon-Project` database is available.
3. Place `dataset_en_dev.json` in the appropriate project directory.
4. Make sure the Neo4j Python driver is installed.
5. Run the Python program.

The program will display a menu allowing the user to select the desired
operation.

## Author

Mason Ford
