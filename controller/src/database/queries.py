import logging

from . import PostgresConnect


log = logging.getLogger('QUERIES')


class Queries(PostgresConnect):

    def get_user_by_id(self, user_id: int) -> dict:
        """
        Retrieve a user by their ID.
        """
        query = """
            SELECT
                id, 
                email, 
                password, 
                username, 
                profile_picture_url,
                phone,
                bio,
                is_premium,
                is_private, 
                date_joined
            FROM users
            WHERE id = %s
        """
        rows = self.execute_query(query, (user_id,))
        if rows:
            return dict(rows[0])
        return {}

    def get_user_by_username(self, username: str) -> dict:
        """
        Retrieve a user by their username.
        """
        query = """
            SELECT
                id, 
                email, 
                username, 
                profile_picture_url,
                phone,
                bio,
                is_premium,
                is_private, 
                date_joined
            FROM users
            WHERE username = %s
        """
        rows = self.execute_query(query, (username,))
        if rows:
            return dict(rows[0])
        return {}

    def update_user_by_id(self, user_id: int, updates: dict) -> bool:
        """
        Update a user's information by their ID.
        """
        if not updates:
            return False

        set_clauses = []
        params = []
        for col, val in updates.items():
            set_clauses.append(f"{col} = %s")
            params.append(val)

        set_sql = ", ".join(set_clauses)
        params.append(user_id)

        query = f"UPDATE users SET {set_sql} WHERE id = %s"
        result = self.execute_query(query, tuple(params))
        return bool(result)

    def get_user_password_by_username(self, username: str) -> dict:
        """
        Retrieve a user's password by their username.
        """
        query = """
            SELECT 
                id, 
                password
            FROM users
            WHERE username = %s
        """
        rows = self.execute_query(query, (username,))
        if rows:
            return dict(rows[0])
        return {}

    def get_user_by_email(self, email: str) -> dict:
        """
        Retrieve a user by their email address.
        """
        query = """
            SELECT
                id, 
                email, 
                password, 
                username, 
                profile_picture_url
            FROM users
            WHERE email = %s
        """
        rows = self.execute_query(query, (email,))
        if rows:
            return dict(rows[0])
        return {}

    def user_change_password(self, user_id: int, new_password: str) -> bool:
        """
        Change a user's password.
        """
        query = """
            UPDATE users
            SET password = %s
            WHERE id = %s
        """
        result = self.execute_query(query, (new_password, user_id))
        return bool(result)

    def create_user(self, username: str, email: str, hashed_password: str, phone: str) -> int | None:
        """
        Create a new user account.
        """
        query = """
            INSERT INTO users (username, email, password, phone, profile_picture_url)
            VALUES (%s, %s, %s, %s, '')
            RETURNING id
        """
        rows = self.execute_query(query, (username, email, hashed_password, phone))
        if rows:
            return rows[0]['id']

    def update_user_picture(self, user_id: int, new_picture_url: str) -> bool:
        """
        Update a user's profile picture.
        """
        try:
            query = """
                UPDATE users
                SET profile_picture_url = %s
                WHERE id = %s
            """
            result = self.execute_query(query, (new_picture_url, user_id))
            
            if not result:
                log.info(f"Profile picture not updated for user {user_id}")
                return False

            return True
        
        except Exception as e:
            log.error(f"Error updating profile picture for user {user_id}: {e}")
            return False

    def get_routes_by_user_id(self, user_id: int) -> list:
        """
        Retrieve all routes associated with a specific user.
        """
        query = """
            SELECT
                id,
                user_id,
                declared_distance,
                real_distance,
                is_avoid_green,
                is_prefer_green,
                is_include_weather,
                ST_AsGeoJSON(start_point) AS point,
                ST_AsGeoJSON(route) AS route,
                timestamp
            FROM routes
            WHERE user_id = %s
        """
        rows = self.execute_query(query, (user_id,))
        return rows if rows else []

    def insert_route(self, route_dict: dict) -> dict[str, int | str] | None:
        """
        Create a new route using ST_GeomFromText to insert geometry.
        """
        query = """
            INSERT INTO routes (
                user_id,
                declared_distance,
                real_distance,
                is_avoid_green,
                is_prefer_green,
                is_include_weather,
                start_point,
                route
            )
            SELECT
                %s, %s, %s, %s, %s, %s,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                ST_GeomFromText(%s, 4326)
            WHERE (
                SELECT COUNT(*) FROM routes WHERE user_id = %s
            ) < 10
            RETURNING id, timestamp;
        """
        rows = self.execute_query(
            query,
            (
                route_dict['user_id'],
                route_dict['declared_distance'],
                route_dict['real_distance'],
                route_dict['is_avoid_green'],
                route_dict['is_prefer_green'],
                route_dict['is_include_weather'],
                route_dict['longitude'],
                route_dict['latitude'],
                'LINESTRING(' + ', '.join(f'{coords[0]} {coords[1]}' for coords in route_dict['route']) + ')',
                route_dict['user_id'],
            )
        )
        if rows:
            return rows[0]
        
    def delete_route(self, route_id: int, user_id: str) -> bool:
        """
        Route deletion
        """
        query = """
            DELETE FROM routes
            WHERE id IN (
                SELECT id FROM routes
                WHERE id = %s AND user_id = %s
                LIMIT 1
            )
            RETURNING id;
        """
        result = self.execute_query(query, (route_id, user_id))
        return bool(result)
