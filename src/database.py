import psycopg2


def run_query(station, query_str, args):
    # Save a detection in the db
    conn = None
    try:
        conn = psycopg2.connect(
            f"postgresql://ronny:ronnydbpassword@localhost:{station.db_port}/ronny"
        )
        cur = conn.cursor()
        # print(f"Run {query_str}")
        # print(f"With args: {args}")
        cur.execute(query_str, args)
        conn.commit()
        # print(cur.fetchone()[0])
        cur.close()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
