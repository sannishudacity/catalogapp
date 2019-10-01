#!/usr/bin/python3

import psycopg2
#from config import config


def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE users(
            id serial PRIMARY KEY,
            name VARCHAR (255) NOT NULL,
            email VARCHAR (355) NOT NULL
        )
        """,
        """
        CREATE TABLE category (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                user_id INTEGER REFERENCES users (id)
                )
        """,
        """
        CREATE TABLE item(
                name VARCHAR(80) NOT NULL,
                id SERIAL PRIMARY KEY,
                description VARCHAR(255),
                category_id INTEGER REFERENCES category (id),
                user_id INTEGER REFERENCES users (id)
        )
        """)
    insertrecs = (
        """
        INSERT INTO users (name, email) VALUES ('Spiderman','itsspiderman@gmail.com')
        """,
        """
        INSERT INTO category (name, user_id) VALUES ('Soccer Category', 1)
        """,
        """
        INSERT INTO item (name, description, category_id, user_id) VALUES ('Soccer Ball', 'Soccer Ball Description', 1, 1)
        """,
        """
        INSERT INTO item (name, description, category_id, user_id) VALUES ('Soccer T-Shirt', 'Soccer T-Shirt Description', 1, 1)
        """,
        """
        INSERT INTO item (name, description, category_id, user_id) VALUES ('Soccer Shorts', 'Soccer Shorts Description', 1, 1)
        """,
        """
        INSERT INTO category (name, user_id) VALUES ('Baseball Category', 1)
        """,
        """
        INSERT INTO item (name, description, category_id, user_id) VALUES ('Baseball Bat', 'Baseball Bat Description', 2, 1)
        """,
        """
        INSERT INTO item (name, description, category_id, user_id) VALUES ('Baseball Ball', 'Baseball Ball Description', 2, 1)
        """,
        """
        INSERT INTO category (name, user_id) VALUES ('Swim Category', 1)
        """,
        """
        INSERT INTO item (name, description, category_id, user_id) VALUES ('Swim Trunks', 'Swim Trunks Description', 3, 1)
        """,
        """
        INSERT INTO item (name, description, category_id, user_id) VALUES ('Swim Goggles', 'Swim Goggles Description', 3, 1)
        """)

    conn = None
    try:
        # read the connection parameters
        #params = config()
        # connect to the PostgreSQL server
        #conn = psycopg2.connect(**params)

        conn = psycopg2.connect(user = "postgres",
                               password = "mypassword",
                               host = "localhost",
                               port = "5432",
                               dbname = "catalogdb")

        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        # insert records one by one
        for insertrec in insertrecs:
            cur.execute(insertrec)
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()
