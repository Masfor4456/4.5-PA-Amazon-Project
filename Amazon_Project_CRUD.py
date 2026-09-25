"""
Name: Mason Ford
Date: 09/25/2026
Assignment: Amazon Project CRUD Assessment
Purpose: Use Python and the Neo4j Python library to perform CRUD operations
         on an Amazon review JSON dataset stored in a Neo4j database.
"""

import json
import os
from neo4j import GraphDatabase


# ------------------------------------------------------------
# Neo4j connection information
# ------------------------------------------------------------
URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password1")
DATABASE = "Amazon-Project"

# The JSON file should be in the same folder as this Python file.
JSON_FILE = "dataset_en_dev.json"


class AmazonProject:
    """Handles the Neo4j connection and all database operations."""

    def __init__(self):
        # Create the Neo4j driver used by the application.
        self.driver = GraphDatabase.driver(URI, auth=AUTH)

    def close(self):
        # Close the database connection when the program ends.
        self.driver.close()

    # --------------------------------------------------------
    # CREATE - Import the JSON dataset
    # --------------------------------------------------------
    def import_json_data(self, filename):
        """
        Read the JSON Lines file and create Category, Product,
        Review, and Reviewer nodes plus their relationships.
        """

        if not os.path.exists(filename):
            print(f"\nFile not found: {filename}")
            print("Make sure the JSON file is in the same folder as this program.")
            return

        count = 0

        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                # Skip blank lines.
                if not line:
                    continue

                record = json.loads(line)

                with self.driver.session(database=DATABASE) as session:
                    session.execute_write(self._create_imported_record, record)

                count += 1

                if count % 500 == 0:
                    print(f"Imported {count} records...")

        print(f"\nImport complete. {count} JSON records processed.")

    @staticmethod
    def _create_imported_record(tx, record):
        """
        Create one complete graph record from a JSON object.

        The dataset uses:
        product_category -> Category.name
        product_id       -> Product.name
        reviewer_id      -> Reviewer.name
        review_id        -> Review.review_id
        review_title     -> Review.title
        review_body      -> Review.content
        stars            -> Review.stars
        """

        query = """
        MERGE (c:Category {name: $category})
        MERGE (p:Product {name: $product})
        MERGE (u:Reviewer {name: $reviewer})
        MERGE (r:Review {review_id: $review_id})
        SET r.title = $title,
            r.content = $content,
            r.stars = $stars

        MERGE (p)-[:BELONGS_TO]->(c)
        MERGE (u)-[:WROTE]->(r)
        MERGE (p)-[:HAS_REVIEW]->(r)
        """

        tx.run(
            query,
            category=record.get("product_category", ""),
            product=record.get("product_id", ""),
            reviewer=record.get("reviewer_id", ""),
            review_id=record.get("review_id", ""),
            title=record.get("review_title", ""),
            content=record.get("review_body", ""),
            stars=int(record.get("stars", 0))
        )

    # --------------------------------------------------------
    # CREATE - User-created nodes
    # --------------------------------------------------------
    def create_node(self):
        print("\nCreate Node")
        print("1. Category")
        print("2. Product")
        print("3. Review")
        print("4. Reviewer")

        choice = input("Select a node type: ").strip()

        with self.driver.session(database=DATABASE) as session:
            if choice == "1":
                name = self.get_required_input("Enter category name: ")

                session.execute_write(
                    lambda tx: tx.run(
                        "MERGE (n:Category {name: $name})",
                        name=name
                    )
                )
                print("Category created.")

            elif choice == "2":
                name = self.get_required_input("Enter product name: ")

                session.execute_write(
                    lambda tx: tx.run(
                        "MERGE (n:Product {name: $name})",
                        name=name
                    )
                )
                print("Product created.")

            elif choice == "3":
                review_id = self.get_required_input("Enter review ID: ")
                title = self.get_required_input("Enter review title: ")
                content = self.get_required_input("Enter review content: ")
                stars = self.get_stars()

                session.execute_write(
                    lambda tx: tx.run(
                        """
                        MERGE (n:Review {review_id: $review_id})
                        SET n.title = $title,
                            n.content = $content,
                            n.stars = $stars
                        """,
                        review_id=review_id,
                        title=title,
                        content=content,
                        stars=stars
                    )
                )
                print("Review created.")

            elif choice == "4":
                name = self.get_required_input("Enter reviewer name: ")

                session.execute_write(
                    lambda tx: tx.run(
                        "MERGE (n:Reviewer {name: $name})",
                        name=name
                    )
                )
                print("Reviewer created.")

            else:
                print("Invalid selection.")

    # --------------------------------------------------------
    # READ
    # --------------------------------------------------------
    def read_node(self):
        print("\nRead Node")
        print("1. Category")
        print("2. Product")
        print("3. Review")
        print("4. Reviewer")
        print("5. Display node counts")

        choice = input("Select an option: ").strip()

        if choice == "5":
            with self.driver.session(database=DATABASE) as session:
                result = session.run(
                    """
                    MATCH (n)
                    RETURN labels(n) AS labels, count(n) AS count
                    ORDER BY labels
                    """
                )

                print("\nNode counts:")
                for record in result:
                    print(f"{record['labels']}: {record['count']}")
            return

        label_map = {
            "1": "Category",
            "2": "Product",
            "3": "Review",
            "4": "Reviewer"
        }

        if choice not in label_map:
            print("Invalid selection.")
            return

        label = label_map[choice]

        if label == "Review":
            identifier = self.get_required_input("Enter review ID: ")

            query = """
            MATCH (n:Review {review_id: $identifier})
            RETURN n
            """
        else:
            identifier = self.get_required_input(
                f"Enter {label.lower()} name: "
            )

            query = f"""
            MATCH (n:{label} {{name: $identifier}})
            RETURN n
            """

        with self.driver.session(database=DATABASE) as session:
            result = session.run(query, identifier=identifier)
            record = result.single()

            if record:
                print("\nNode found:")
                print(dict(record["n"]))
            else:
                print("No matching node was found.")

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------
    def update_node(self):
        """
        Update a node property. This supplies the UPDATE part
        of CRUD functionality required by the assignment.
        """

        print("\nUpdate Node")
        print("1. Category name")
        print("2. Product name")
        print("3. Reviewer name")
        print("4. Review")

        choice = input("Select an option: ").strip()

        with self.driver.session(database=DATABASE) as session:

            if choice == "1":
                old_name = self.get_required_input("Current category name: ")
                new_name = self.get_required_input("New category name: ")

                result = session.run(
                    """
                    MATCH (n:Category {name: $old_name})
                    SET n.name = $new_name
                    RETURN count(n) AS updated
                    """,
                    old_name=old_name,
                    new_name=new_name
                ).single()

                print(f"Categories updated: {result['updated']}")

            elif choice == "2":
                old_name = self.get_required_input("Current product name: ")
                new_name = self.get_required_input("New product name: ")

                result = session.run(
                    """
                    MATCH (n:Product {name: $old_name})
                    SET n.name = $new_name
                    RETURN count(n) AS updated
                    """,
                    old_name=old_name,
                    new_name=new_name
                ).single()

                print(f"Products updated: {result['updated']}")

            elif choice == "3":
                old_name = self.get_required_input("Current reviewer name: ")
                new_name = self.get_required_input("New reviewer name: ")

                result = session.run(
                    """
                    MATCH (n:Reviewer {name: $old_name})
                    SET n.name = $new_name
                    RETURN count(n) AS updated
                    """,
                    old_name=old_name,
                    new_name=new_name
                ).single()

                print(f"Reviewers updated: {result['updated']}")

            elif choice == "4":
                review_id = self.get_required_input("Review ID: ")

                print("1. Update title")
                print("2. Update content")
                print("3. Update stars")
                field_choice = input("Select a property: ").strip()

                if field_choice == "1":
                    value = self.get_required_input("New title: ")

                    result = session.run(
                        """
                        MATCH (n:Review {review_id: $review_id})
                        SET n.title = $value
                        RETURN count(n) AS updated
                        """,
                        review_id=review_id,
                        value=value
                    ).single()

                elif field_choice == "2":
                    value = self.get_required_input("New content: ")

                    result = session.run(
                        """
                        MATCH (n:Review {review_id: $review_id})
                        SET n.content = $value
                        RETURN count(n) AS updated
                        """,
                        review_id=review_id,
                        value=value
                    ).single()

                elif field_choice == "3":
                    value = self.get_stars()

                    result = session.run(
                        """
                        MATCH (n:Review {review_id: $review_id})
                        SET n.stars = $value
                        RETURN count(n) AS updated
                        """,
                        review_id=review_id,
                        value=value
                    ).single()

                else:
                    print("Invalid selection.")
                    return

                print(f"Reviews updated: {result['updated']}")

            else:
                print("Invalid selection.")

    # --------------------------------------------------------
    # CREATE - User-created relationships
    # --------------------------------------------------------
    def create_relationship(self):
        print("\nCreate Relationship")
        print("1. Product -> Category")
        print("2. Product -> Review")

        choice = input("Select a relationship type: ").strip()

        with self.driver.session(database=DATABASE) as session:

            if choice == "1":
                product = self.get_required_input("Product name: ")
                category = self.get_required_input("Category name: ")

                result = session.run(
                    """
                    MATCH (p:Product {name: $product})
                    MATCH (c:Category {name: $category})
                    MERGE (p)-[r:BELONGS_TO]->(c)
                    RETURN count(r) AS created
                    """,
                    product=product,
                    category=category
                ).single()

                if result["created"] > 0:
                    print("Product -> Category relationship created.")
                else:
                    print("The relationship could not be created.")
                    print("Make sure both nodes already exist.")

            elif choice == "2":
                product = self.get_required_input("Product name: ")
                review_id = self.get_required_input("Review ID: ")

                result = session.run(
                    """
                    MATCH (p:Product {name: $product})
                    MATCH (r:Review {review_id: $review_id})
                    MERGE (p)-[rel:HAS_REVIEW]->(r)
                    RETURN count(rel) AS created
                    """,
                    product=product,
                    review_id=review_id
                ).single()

                if result["created"] > 0:
                    print("Product -> Review relationship created.")
                else:
                    print("The relationship could not be created.")
                    print("Make sure both nodes already exist.")

            else:
                print("Invalid selection.")

    # --------------------------------------------------------
    # READ - Product count for a category
    # --------------------------------------------------------
    def count_products_by_category(self):
        category = self.get_required_input("Enter category name: ")

        with self.driver.session(database=DATABASE) as session:
            result = session.run(
                """
                MATCH (c:Category {name: $category})
                OPTIONAL MATCH (p:Product)-[:BELONGS_TO]->(c)
                RETURN count(p) AS product_count
                """,
                category=category
            ).single()

            print(
                f"\nProduct count for category '{category}': "
                f"{result['product_count']}"
            )

    # --------------------------------------------------------
    # READ - Review count for a reviewer
    # --------------------------------------------------------
    def count_reviews_by_reviewer(self):
        reviewer = self.get_required_input("Enter reviewer name (reviewer_id): ")

        with self.driver.session(database=DATABASE) as session:
            result = session.run(
                """
                MATCH (u:Reviewer {name: $reviewer})
                OPTIONAL MATCH (u)-[:WROTE]->(r:Review)
                RETURN count(r) AS review_count
                """,
                reviewer=reviewer
            ).single()

            print(
                f"\nReview count for reviewer '{reviewer}': "
                f"{result['review_count']}"
            )

    # --------------------------------------------------------
    # DELETE - Category by name
    # --------------------------------------------------------
    def delete_category(self):
        category = self.get_required_input("Enter category name to delete: ")

        with self.driver.session(database=DATABASE) as session:
            result = session.run(
                """
                MATCH (c:Category {name: $category})
                DETACH DELETE c
                RETURN count(c) AS deleted
                """,
                category=category
            ).single()

            print(f"Category deleted: {result['deleted']}")

    # --------------------------------------------------------
    # DELETE - All relationships
    # --------------------------------------------------------
    def delete_all_relationships(self):
        confirm = input(
            "Delete ALL relationships in the graph? Type YES to continue: "
        ).strip()

        if confirm != "YES":
            print("Operation cancelled.")
            return

        with self.driver.session(database=DATABASE) as session:
            result = session.run(
                """
                MATCH ()-[r]-()
                DELETE r
                RETURN count(r) AS deleted
                """
            ).single()

            print(f"Relationships deleted: {result['deleted']}")

    # --------------------------------------------------------
    # DELETE - All nodes
    # --------------------------------------------------------
    def delete_all_nodes(self):
        confirm = input(
            "Delete ALL nodes and relationships in the graph? "
            "Type DELETE to continue: "
        ).strip()

        if confirm != "DELETE":
            print("Operation cancelled.")
            return

        with self.driver.session(database=DATABASE) as session:
            result = session.run(
                """
                MATCH (n)
                DETACH DELETE n
                RETURN count(n) AS deleted
                """
            ).single()

            print(f"Nodes deleted: {result['deleted']}")

    # --------------------------------------------------------
    # Input validation helpers
    # --------------------------------------------------------
    @staticmethod
    def get_required_input(prompt):
        while True:
            value = input(prompt).strip()

            if value:
                return value

            print("Input cannot be blank. Please try again.")

    @staticmethod
    def get_stars():
        while True:
            value = input("Enter stars (1-5): ").strip()

            try:
                stars = int(value)

                if 1 <= stars <= 5:
                    return stars

                print("Stars must be between 1 and 5.")

            except ValueError:
                print("Please enter a whole number from 1 to 5.")

    # --------------------------------------------------------
    # Main menu
    # --------------------------------------------------------
    def run(self):
        print("\n==========================================")
        print("      Amazon Project - Neo4j CRUD")
        print("==========================================")

        while True:
            print("\nMain Menu")
            print("1. Import JSON data")
            print("2. Create a node")
            print("3. Read a node")
            print("4. Update a node")
            print("5. Create a relationship")
            print("6. Count products by category")
            print("7. Count reviews by reviewer")
            print("8. Delete a category")
            print("9. Delete all relationships")
            print("10. Delete all nodes")
            print("0. Exit")

            choice = input("\nSelect an option: ").strip()

            try:
                if choice == "1":
                    self.import_json_data(JSON_FILE)

                elif choice == "2":
                    self.create_node()

                elif choice == "3":
                    self.read_node()

                elif choice == "4":
                    self.update_node()

                elif choice == "5":
                    self.create_relationship()

                elif choice == "6":
                    self.count_products_by_category()

                elif choice == "7":
                    self.count_reviews_by_reviewer()

                elif choice == "8":
                    self.delete_category()

                elif choice == "9":
                    self.delete_all_relationships()

                elif choice == "10":
                    self.delete_all_nodes()

                elif choice == "0":
                    print("\nProgram ended.")
                    break

                else:
                    print("Invalid selection. Please choose a menu option.")

            except Exception as error:
                print("\nAn error occurred:")
                print(error)
                print("Check that Neo4j is running and the database settings are correct.")


# ------------------------------------------------------------
# Program entry point
# ------------------------------------------------------------
if __name__ == "__main__":
    app = AmazonProject()

    try:
        app.run()
    finally:
        app.close()
