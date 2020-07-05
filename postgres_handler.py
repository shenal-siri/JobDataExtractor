# Reference matrial: https://www.psycopg.org/docs/sql.html
import sys
# Psycopg2
import psycopg2
from psycopg2 import Error, sql
from postgres_config import pg_config

class PGHandler:
    """
    PGHandler class stores a collection of methods for transacting inserts / selects / deletes 
    to the tables in the job_helper Postgres database.
    It also stores a connection to the database once initialized, as well as pre-defined query strings.
    """
    connection = None
    
    # Query strings used to build queries safely
    
    text_insert_query = """
    INSERT INTO {table} ({fields}) 
    VALUES ({values})
    ON CONFLICT ({pkey}) 
    DO NOTHING; 
    """
    
    text_select_query = """
    SELECT {field} FROM {table}
 	WHERE {field_where} = ({value});
    """
    
    text_select_from_title_company = """
    SELECT {field} FROM {table} 
    WHERE title ILIKE {title}
    AND company ILIKE {company};
    """
    
    text_update_query = """
    UPDATE {table}
    SET {field} = ({value})
    WHERE {field_where} = ({value_where});
    """
    
    
    @classmethod
    def init_connection(cls):
        """
        Initialize a Postgres database connection
        Inputs:  Database connection arguments
        Outputs: PGHandler.connection attribute (or print error message)
        """
        try:
            # Read connection config from database.ini file and connect to database
            params = pg_config()
            cls.connection = psycopg2.connect(**params)
            
        except psycopg2.DatabaseError as error:
            print(f'Error {error}')
            sys.exit(1)
    
    
    @classmethod
    def insert_job(cls, job_data):
        """
        Execute a SQL transaction to insert a new job listing into the database
        Inputs:  Dictionary of key-value pairs corresponding to columns in the 'jobs' table
        Outputs: True if transaction commits to db successfully, else False
        """
        
        # Check if job already exists, cancel transaction if it does
        if cls.check_job_exists(job_data):
            print("Job id: {} already exists in database, insert transaction cancelled".format(job_data['id']))
            return False
        
        # Separate many-to-many fields from extracted job_data
        junc_data = {'industry': job_data.pop('industries'),
                     'function': job_data.pop('functions')}
        
        # Dictionaries to store the various insert / select queries
        query_insert = {}
        query_select = {}
        
        job_fields, job_values = zip(*job_data.items())
        
        # Create cursor
        if cls.connection is None:
            print("Connection to Postgres database has not been established! Call PGHandler.init_connection()")
        else:
            with cls.connection: # pylint: disable=not-context-manager
                with cls.connection.cursor() as cur:
                    
                    # Get job id and insert job into database
                    job_id = int(job_data['id'])
                    
                    # Build and execute query for insertion into job table
                    query_insert['job'] = sql.SQL(cls.text_insert_query).format(
                        table = sql.Identifier('job'),
                        fields = sql.SQL(",").join(map(sql.Identifier, job_fields)),
                        values = sql.SQL(",").join(sql.Placeholder() * len(job_fields)),
                        pkey = sql.Identifier('id')
                        )
                    
                    cur.execute(query_insert['job'], job_values)
                    
                    # Loop through each of the multi-value tables and fields
                    for table, values in junc_data.items():
                        
                        junc_ids = ['job_id', table+'_id']
                        
                        # Build queries for industry / function table insertion and selection
                        query_insert[table] = sql.SQL(cls.text_insert_query).format(
                        table = sql.Identifier(table),
                        fields = sql.Identifier('name'),
                        values = sql.Placeholder(),
                        pkey = sql.Identifier('name')
                        )
                        
                        query_select[table] = sql.SQL(cls.text_select_query).format(
                        table = sql.Identifier(table),
                        field = sql.Identifier('id'),
                        field_where = sql.Identifier('name'),
                        value = sql.Placeholder()
                        )
                        
                        # Build query for insertion to junction tables
                        query_insert['job_'+table] = sql.SQL(cls.text_insert_query).format(
                        table = sql.Identifier('job_'+table),
                        fields = sql.SQL(",").join(sql.Identifier(n) for n in junc_ids),
                        values = sql.SQL(",").join(sql.Placeholder() * len(junc_ids)),
                        pkey = sql.SQL(",").join(sql.Identifier(n) for n in junc_ids),
                        )
                        
                        # Loop through each industry / function item
                        for value in values:
                            
                            # Insert industry / function item into database
                            cur.execute(query_insert[table], (value,))
                        
                            # Get auto-assigned industry_id / function_id from database
                            cur.execute(query_select[table], (value,))
                            current_id = cur.fetchone()[0]
                            
                            # Insert new row to job_industry / job_function junction tables
                            cur.execute(query_insert['job_'+table], (job_id, current_id))
                            
        #print("Transaction Completed Successfully!")
        return True
    
    
    @classmethod
    def check_job_exists(cls, job_data, show_result=False):
        """
        Execute a SQL transaction to check if a job is already in the database.
        Inputs:  Dictionary of key-value pairs corresponding to columns in the 'jobs' table
                 Boolean to toggle verbose check result
        Outputs: Boolean indicating presence (True) / absence (False) of job in database
        """
        job_id = int(job_data['id'])
        
        if cls.connection is None:
            print("Connection to Postgres database has not been established! Call PGHandler.init_connection()")
        else:
            with cls.connection: # pylint: disable=not-context-manager
                with cls.connection.cursor() as cur:
                    
                    # Build and execute query for insertion into job table
                    query_select = sql.SQL(cls.text_select_query).format(
                        table = sql.Identifier('job'),
                        field = sql.Identifier('id'),
                        field_where = sql.Identifier('id'),
                        value = sql.Placeholder()
                        )
                    cur.execute(query_select, (job_id,))
                    
                    if cur.fetchone() is None:
                        if show_result: print("Job id: {} NOT IN database".format(job_id))
                        return False
                    else:
                        if show_result: print("Job id: {} FOUND IN database".format(job_id))
                        return True
                    
        #print("Transaction Completed Successfully!")
    
    
    
    @classmethod
    def update_rejected(cls, job_title, job_company):
        """
        Change the 'rejected' flag for a job in the db from False to True
        Inputs:  Strings of job title and company
        Outputs: Boolean True if Transaction committed successfully, False if job not found / commit failed
        """
        
        if cls.connection is None:
            print("Connection to Postgres database has not been established! Call PGHandler.init_connection()")
        else:
            with cls.connection: # pylint: disable=not-context-manager
                with cls.connection.cursor() as cur:
        
                    # Build and execute query to check if job exists in table
                    query_select = sql.SQL(cls.text_select_from_title_company).format(
                        field = sql.Identifier('id'),
                        table = sql.Identifier('job'),
                        title = sql.Placeholder(), 
                        company = sql.Placeholder()
                        )
                    cur.execute(query_select, (job_title, job_company))
                    
                    job_id = cur.fetchone()
                    
                    if job_id is None:
                        print("Job not found in database")
                        return False
                    else:
                        # Build and execute query to update job listing
                        query_update = sql.SQL(cls.text_update_query).format(
                            table = sql.Identifier('job'),
                            field = sql.Identifier('rejected'),
                            value = sql.Placeholder(),
                            field_where = sql.Identifier('id'), 
                            value_where = sql.Placeholder()
                            )
                        cur.execute(query_update, (True, job_id))
                            
                        #print("Transaction Completed Successfully!")
                        return True
        
        
    @classmethod
    def delete_job(cls):
        """
        Execute a SQL transaction to remove a job listing from the database
        """
        pass
        

    
    