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
        log.info(rows)
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
            ) < 5
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

# class Queries(MongoDBConnect):

#     def get_user_by_id(self, id: str) -> dict:
#         try:
#             filter = {'_id': ObjectId(id)}
#             projection = {
#                 'username': True,
#                 'bio': True,
#                 'email': True,
#                 'profile_picture_url': True,
#                 'location': True,
#                 'posts': True,
#                 'scans': True,
#                 'is_premium': True,
#                 'is_private': True,
#                 'phone': True
#             }
#             return self.find_one('users', filter, projection)
#         except Exception as e:
#             log.error(f'Error fetching user: {e}')
#             return {}
    
#     def get_user_by_username(self, username: str) -> dict:
#         try:
#             filter = {'username': username}
#             projection = {
#                 '_id': True,
#                 'username': True,
#                 'bio': True,
#                 'email': True,
#                 'profile_picture_url': True,
#                 'location': True,
#                 'is_premium': True,
#                 'is_private': True,
#                 'phone': True,
#                 'posts': True,
#                 'scans': True
#             }
#             user = self.find_one('users', filter, projection)
#             if user:
#                 user['id'] = user.pop('_id')  # Rename _id to id
#             return user
#         except Exception as e:
#             log.error(f'Error fetching user: {e}')
#             return {}
    
#     def update_user_by_id(self, id: str, updates: dict) -> bool:
#         try:
#             filter = {'_id': ObjectId(id)}
#             update = {'$set': updates}

#             result = self.update_one('users', filter, update)
#             return result.modified_count > 0
#         except Exception as e:
#             log.error(f'Error updating user: {e}')
#             return False

#     def search_users_by_username(self, partial_username: str):
#         try:
#             filter = {
#                 'username': {
#                     '$regex': f'^{partial_username}',
#                     '$options': 'i'
#                 }
#             }
#             projection = {
#                 '_id': False,
#                 'username': True,
#                 'profile_picture_url': True
#             }
#             users = list(self.db['users'].find(filter, projection))
#             return users
#         except Exception as e:
#             log.debug(f'Error fetching users: {e}')
#             return []

        
#     def get_user_password_by_username(self, username: str) -> dict:
#         try:
#             filter = {'username': username}
#             projection = {
#                 '_id': True,
#                 'hashed_password': True,
#             }
#             return self.find_one('users', filter, projection)
#         except Exception as e:
#             log.error(f'Error fetching user: {e}')
#             return {}
        
#     def get_user_by_email(self, email: str) -> dict:
#         try:
#             filter = {'email': email}
#             return self.find_one('users', filter)
#         except Exception as e:
#             log.error(f'Error fetching user: {e}')
#             return {}
    
#     def get_post_by_id(self, id: str) -> dict:
#         try:
#             filter = {'_id': ObjectId(id)}
#             return self.find_one('posts', filter)
#         except Exception as e:
#             log.error(f'Error fetching post: {e}')
#             return {}
    
#     def get_comment_by_id(self, id: str) -> dict:
#         try:
#             filter = {'_id': ObjectId(id)}
#             return self.find_one('comments', filter)
#         except Exception as e:
#             log.error(f'Error fetching post: {e}')
#             return {}
    
#     def get_notifications(self, user_id: str, last_timestamp: datetime | None, quantity: int) -> list[dict] | bool:
#         try:
#             scans_filter = {
#                 'user_id': ObjectId(user_id),
#                 'is_notification': True
#             }
#             filter = {
#                 'is_notification': True
#             }

#             if last_timestamp:
#                 timestamp_filter = {'timestamp': {"$lt": last_timestamp}}
#                 scans_filter.update(timestamp_filter)
#                 filter.update(timestamp_filter)

#             pipeline = [
#                 {"$match": {"user_id": ObjectId(user_id)}},
#                 {"$project": {
#                     "_id": 1
#                 }},
#                 {"$lookup": {
#                     "from": "comments",
#                     "localField": "_id",
#                     "foreignField": "post_id",
#                     "pipeline": [
#                         {"$match": filter},
#                         {"$project": {
#                             "_id": 1,
#                             "post_id": 1,
#                             "user_id": 1,
#                             "timestamp": 1
#                         }}
#                     ],
#                     "as": "comments"
#                 }},
                
#                 {"$lookup": {
#                     "from": "reactions",
#                     "localField": "_id",
#                     "foreignField": "post_id",
#                     "pipeline": [
#                         {"$match": filter},
#                         {"$project": {
#                             "_id": 1,
#                             "post_id": 1,
#                             "user_id": 1,
#                             "reaction_type": 1,
#                             "timestamp": 1
#                         }}
#                     ],
#                     "as": "reactions"
#                 }},
                
#                 {"$project": {
#                     "notifications": {
#                         "$concatArrays": [
#                             {"$ifNull": ["$comments", []]},
#                             {"$ifNull": ["$reactions", []]}
#                         ]
#                     }
#                 }},
                
#                 {"$unwind": {"path": "$notifications", "preserveNullAndEmptyArrays": True}},
                
#                 {"$replaceRoot": {
#                     "newRoot": {
#                         "$ifNull": ["$notifications", {}]
#                     }
#                 }},
                
#                 {"$unionWith": {
#                     "coll": "scans",
#                     "pipeline": [
#                         {"$match": scans_filter},
#                         {"$project": {
#                             "city": 1,
#                             "latitude": 1,
#                             "longitude": 1,
#                             "timestamp": 1
#                         }}
#                     ]
#                 }},

#                 {"$addFields": {
#                     "user_id_object": {"$toObjectId": "$user_id"}
#                 }},
#                 {"$lookup": {
#                     "from": "users",
#                     "localField": "user_id_object",
#                     "foreignField": "_id",
#                     "as": "user_info"
#                 }},
#                 {"$unwind": {
#                     "path": "$user_info",
#                     "preserveNullAndEmptyArrays": True 
#                 }},
#                 {"$addFields": {
#                     "username": "$user_info.username"
#                 }},
#                 {"$project": {
#                     "user_info": 0,
#                     "user_id_object": 0
#                 }},

#                 {"$sort": {"timestamp": -1}},
#                 {"$addFields": {
#                     "timestamp": {
#                         "$dateToString": {
#                             "format": "%Y-%m-%d %H:%M:%S",
#                             "date": "$timestamp"
#                         }
#                     }
#                 }},
#                 {"$match": {
#                     "timestamp": {"$ne": None}
#                 }},
#                 {"$limit": quantity}
#             ]

#             return self.find_aggregate('posts', pipeline)

#         except Exception as e:
#             log.error(f'Error fetching notifications: {e}')
#             return False

#     def search_posts(self, search_term: str) -> list:
#         try:
#             query = {"description": {"$regex": search_term, "$options": "i"}}

#             pipeline = [
#                 {"$match": query},
#                 {"$sort": {"timestamp": -1}},
#                 {
#                     "$lookup": {
#                         "from": "reactions",
#                         "localField": "_id",
#                         "foreignField": "post_id",
#                         "as": "reactions",
#                     }
#                 },
#                 {
#                     "$lookup": {
#                         "from": "users",
#                         "localField": "user_id",
#                         "foreignField": "_id",
#                         "as": "user",
#                     }
#                 },
#                 {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},
#                 {
#                     "$project": {
#                         "id": {"$toString": "$_id"},
#                         "content": "$description",
#                         "images": "$images_urls",
#                         "user": {
#                             "id": {"$toString": "$user._id"},
#                             "username": "$user.username",
#                             "image": "$user.profile_picture_url",
#                         },
#                         "location": 1,
#                         "timestamp": {
#                             "$dateToString": {
#                                 "format": "%Y-%m-%dT%H:%M:%S.%LZ",
#                                 "date": "$timestamp",
#                                 "timezone": "UTC"
#                             }
#                         },
#                         "reactions": {
#                             "$map": {
#                                 "input": "$reactions",
#                                 "as": "reaction",
#                                 "in": {
#                                     "id": {"$toString": "$$reaction._id"},
#                                     "user_id": {"$toString": "$$reaction.user_id"},
#                                     "reaction_type": "$$reaction.reaction_type",
#                                 },
#                             }
#                         },
#                     }
#                 },
#             ]

#             cursor = self.find_aggregate('posts', pipeline)

#             processed_results = []
#             for post in cursor:
#                 try:
#                     processed_results.append({
#                         'id': post.get('id', ''),
#                         'content': post.get('content', ''),
#                         'images': post.get('images', []),
#                         'user': {
#                             'id': post.get('user', {}).get('id', ''),
#                             'username': post.get('user', {}).get('username', ''),
#                             'image': post.get('user', {}).get('image', '')
#                         },
#                         'location': post.get('location', ''),
#                         'timestamp': post.get('timestamp', ''),
#                         'reactions': post.get('reactions', [])
#                     })
#                 except Exception as e:
#                     log.error(f"Error processing post: {e}")

#             return processed_results

#         except Exception as e:
#             log.error(f"Error searching posts: {e}")
#             return False

    
#     def user_change_password(self, _id: ObjectId, hashed_password: bytes) -> bool:
#         try:
#             hashed_password_binary = Binary(hashed_password)
#             update_result = self.update_one(
#                 'users',
#                 {'_id': _id},
#                 {'$set': {'hashed_password': hashed_password_binary}},
#             )

#             if update_result.modified_count == 0:
#                 log.info(f'User with id {_id} not updated')
#                 return False
            
#             return True

#         except Exception as e:
#             log.error(f'Error updating user: {e}')
#             return False
            
#     def create_user(self, username: str, email: str, hashed_password: bytes, phone: str):
#         try:
#             user_data = {
#                 'username': username,
#                 'email': email,
#                 'hashed_password': hashed_password,
#                 'phone': phone,
#                 'profile_picture_url': "",
#                 'bio': "",
#                 'scans': [],
#                 'posts': [],
#                 'location': "",
#                 'is_premium': False,
#                 'is_private': False,
#             }
#             result = self.insert_one('users', user_data)
#             return result.inserted_id
#         except Exception as e:
#             log.error(f'Error creating user: {e}')
#             return False

#     @MongoDBConnect.transaction
#     def insert_scan(self, user_id: str, ip: str, city: str, latitude: float, longitude: float, timestamp: datetime, session=None) -> str | bool:
#         try:
#             document = {
#                 'user_id': ObjectId(user_id), 
#                 'ip': ip, 
#                 'city': city, 
#                 'latitude': latitude, 
#                 'longitude': longitude, 
#                 'timestamp': timestamp,
#                 'is_notification': True
#             }
#             result = self.insert_one('scans', document)
            
#             inserted_id = result.inserted_id

#             update_result = self.update_one(
#                 'users',
#                 {'_id': ObjectId(user_id)},
#                 {'$push': {'scans': inserted_id}},
#                 session=session
#             )

#             if update_result.modified_count == 0:
#                 log.info(f"User with id {user_id} not updated")
#                 return False
            
#             return inserted_id
    
#         except Exception as e:
#             log.error(f"Error inserting comment with data {user_id = }, {ip = }, {city = }, {latitude = }, {longitude = } Error: {e}")
#             return False
    
#     @MongoDBConnect.transaction
#     def insert_comment(self, post_id: str, user_id: str, content: str, timestamp: datetime, session=None) -> str | bool:
#         try:
#             document = {
#                 'post_id': ObjectId(post_id), 
#                 'user_id': ObjectId(user_id), 
#                 'content': content, 
#                 'timestamp': timestamp, 
#                 'is_notification': True
#             }
#             result = self.insert_one('comments', document)
            
#             inserted_id = result.inserted_id

#             update_result = self.update_one(
#                 'posts',
#                 {'_id': ObjectId(post_id)},
#                 {'$push': {'comments': inserted_id}},
#                 session=session
#             )

#             if update_result.modified_count == 0:
#                 log.info(f"Post with id {post_id} not updated")
#                 return False
            
#             return str(inserted_id)
        
#         except Exception as e:
#             log.error(f"Error inserting comment with data {post_id = }, {user_id = }, {content = }, Error: {e}")
#             return False
    
#     @MongoDBConnect.transaction
#     def insert_reaction(self, post_id: str, user_id: str, reaction_type: str, timestamp: datetime, session=None) -> str | bool:
#         try:
#             filter = {
#                 'post_id': ObjectId(post_id), 
#                 'user_id': ObjectId(user_id), 
#             }
#             find_result = self.find_one('reactions', filter)

#             if find_result:
#                 if find_result.get('reaction_type') == reaction_type:
#                     return False
                
#                 inserted_id = str(find_result.get('_id'))
#                 update_values = {
#                     '$set': {
#                         'reaction_type': reaction_type, 
#                         'timestamp': timestamp, 
#                         'is_notification': True
#                     }
#                 }
#                 update_result = self.update_one('reactions', filter, update_values, session=session)

#                 if update_result.modified_count == 0:
#                     log.info(f"Reaction with id {inserted_id} not updated")
#                     return False
                
#                 return inserted_id

#             else:
#                 document = {
#                     'post_id': ObjectId(post_id), 
#                     'user_id': ObjectId(user_id), 
#                     'reaction_type': reaction_type, 
#                     'timestamp': timestamp, 
#                     'is_notification': True
#                 }
#                 result = self.insert_one('reactions', document, session=session)

#                 inserted_id = result.inserted_id

#                 update_result = self.update_one(
#                     'posts',
#                     {'_id': ObjectId(post_id)},
#                     {'$push': {'reactions': inserted_id}},
#                     session=session
#                 )

#                 if update_result.modified_count == 0:
#                     log.info(f"Reaction with id {inserted_id} not updated")
#                     return False
                
#                 return str(inserted_id)
        
#         except Exception as e:
#             log.error(f"Error inserting reaction with data {post_id = }, {user_id = }, {reaction_type = }, Error: {e}")
#             return False

#     def update_user_picture(self, user_id: str, new_picture_url: str) -> bool:
#         try:
#             update_result = self.update_one(
#                 'users',
#                 {'_id': ObjectId(user_id)},
#                 {'$set': {'profile_picture_url': new_picture_url}}
#             )

#             if update_result.modified_count == 0:
#                 log.info(f"Profile picture not updated for user {user_id}")
#                 return False

#             return True
        
#         except Exception as e:
#             log.error(f"Error updating profile picture for user {user_id}: {e}")
#             return False

#     def remove_notification(self, notification_type: str, user_id: str, notification_id: str) -> bool:
#         try:
#             if notification_type in {'comment', 'reaction'}:
#                 result = self.find_one(f'{notification_type}s', {"_id": ObjectId(notification_id)})
                
#                 if not result:
#                     return False

#                 post_result = self.find_one(f'posts', {"_id": result.get('post_id')})

#                 if not post_result or str(post_result.get('user_id')) != user_id:
#                     return False
                
#                 delete_result = self.update_one(
#                     f'{notification_type}s',
#                     {
#                         "_id": ObjectId(notification_id)
#                     },
#                     {'$set': {'is_notification': False}}
#                 )

#             else:
#                 delete_result = self.update_one(
#                     f'{notification_type}s',
#                     {
#                         "user_id": ObjectId(user_id),
#                         "_id": ObjectId(notification_id)
#                     },
#                     {'$set': {'is_notification': False}}
#                 )
            
#             if delete_result.modified_count == 0:
#                 log.info(f"Notification not removed for {user_id}, {notification_id = }")
#                 return False

#             return True
        
#         except Exception as e:
#             log.error(f"Error during removing notification: {notification_id = }, {user_id = }, Error = {e}")
#             return False
    
#     @MongoDBConnect.transaction
#     def delete_comment(self, comment_id: str, session=None) -> bool:
#         try:
#             delete_result = self.find_one_and_delete(
#                 'comments',
#                 {
#                     "_id": ObjectId(comment_id)
#                 },
#                 session=session
#             )
            
#             if not delete_result:
#                 log.info(f"Comment not deleted for {comment_id = }")
#                 return False

#             update_result = self.update_one(
#                 'posts',
#                 {'_id': delete_result.get('post_id')},
#                 {'$pull': {'comments': delete_result.get('_id')}},
#                 session=session
#             )

#             if update_result.modified_count == 0:
#                 log.info(f"Comment not removed from post {delete_result.get('post_id')}, {comment_id = }")
#                 return False
            
#             return True
        
#         except Exception as e:
#             log.error(f"Error during deleting comment: {comment_id = }, Error = {e}")
#             return False
    
#     @MongoDBConnect.transaction
#     def delete_reaction(self, user_id: str, post_id: str, session=None) -> bool:
#         try:
#             delete_result = self.find_one_and_delete(
#                 'reactions',
#                 {
#                     'user_id': ObjectId(user_id),
#                     'post_id': ObjectId(post_id)
#                 },
#                 session=session
#             )
            
#             if not delete_result:
#                 log.info(f"Reaction not deleted for {user_id = }, {post_id = }")
#                 return False

#             update_result = self.update_one(
#                 'posts',
#                 {'_id': ObjectId(post_id)},
#                 {'$pull': {'reactions': delete_result.get('_id')}},
#                 session=session
#             )

#             if update_result.modified_count == 0:
#                 log.info(f"Reaction not removed from post for {user_id = }, {post_id = }")
#                 return False
            
#             return True
        
#         except Exception as e:
#             log.error(f"Error during deleting reaction for {user_id = }, {post_id = }, Error = {e}")
#             return False
        
#     def fetch_posts(self, query: dict, limit: int = 10) -> list:
#         """
#         Fetch posts from the database with optional filters and pagination using aggregation pipeline.
#         This version includes related reactions and user details using $lookup.
#         :param query: Dictionary containing query filters
#         :param limit: Maximum number of documents to return
#         :return: List of posts
#         """
#         try:
#             # Build the aggregation pipeline
#             pipeline = [
#                 # Match posts based on the query
#                 {"$match": query},

#                 # Sort by timestamp in descending order
#                 {"$sort": {"timestamp": -1}},

#                 # Limit the number of posts
#                 {"$limit": limit},

#                 # Lookup reactions for each post
#                 {
#                     "$lookup": {
#                         "from": "reactions",             # Collection to join
#                         "localField": "_id",             # Field from the 'posts' collection
#                         "foreignField": "post_id",       # Field from the 'reactions' collection
#                         "as": "reactions",               # Output array field
#                     }
#                 },

#                 # Lookup user details for the post author
#                 {
#                     "$lookup": {
#                         "from": "users",                 # Collection to join
#                         "localField": "user_id",         # Field from the 'posts' collection
#                         "foreignField": "_id",           # Field from the 'users' collection
#                         "as": "user",                    # Output array field
#                     }
#                 },

#                 # Unwind the user array to convert it to a single object
#                 {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},

#                 # Project fields to format the output structure
#                 {
#                     "$project": {
#                         "id": {"$toString": "$_id"},     # Convert ObjectId to string
#                         "content": "$description",      # Rename field
#                         "images": "$images_urls",       # Rename field
#                         "user": {
#                             "id": {"$toString": "$user._id"},
#                             "username": "$user.username",
#                             "image": "$user.profile_picture_url",
#                         },
#                         "location": 1,
#                         "timestamp": 1,
#                         "reactions": {
#                             "$map": {
#                                 "input": "$reactions",
#                                 "as": "reaction",
#                                 "in": {
#                                     "id": {"$toString": "$$reaction._id"},
#                                     "user_id": {"$toString": "$$reaction.user_id"},
#                                     "reaction_type": "$$reaction.reaction_type",
#                                 },
#                             }
#                         },
#                     }
#                 },
#             ]

#             # Execute the aggregation pipeline
#             cursor = self.find_aggregate('posts', pipeline)

#             return list(cursor)

#         except Exception as e:
#             log.error(f"Error fetching posts with $lookup: {e}")
#             return []


        
#     def get_reactions(self, post_id: str) -> list:
#         """
#         Fetch reactions for a specific post.
#         :param post_id: The unique ID of the post
#         :return: List of reactions for the post
#         """
#         try:
#             reactions = list(self.find('reactions', {'post_id': ObjectId(post_id)}))
#             for reaction in reactions:
#                 reaction['_id'] = str(reaction['_id'])
#                 reaction['user_id'] = str(reaction['user_id'])
#                 reaction['post_id'] = str(reaction['post_id'])
#             return reactions
#         except Exception as e:
#             log.error(f"Error fetching reactions for post {post_id}: {e}")
#             return []

#     def fetch_comments(self, query: dict, limit: int = 10) -> list:
#         """
#         Fetch comments for a specific post with user details included.
#         :param query: Dictionary containing query filters
#         :param limit: Maximum number of documents to return
#         :return: List of comments
#         """
#         try:
#             # Build the aggregation pipeline
#             pipeline = [
#                 # Match comments based on the query
#                 {"$match": query},

#                 # Sort by timestamp in descending order
#                 {"$sort": {"timestamp": -1}},

#                 # Limit the number of comments
#                 {"$limit": limit},

#                 # Lookup user details for each comment's user
#                 {
#                     "$lookup": {
#                         "from": "users",                # Collection to join
#                         "localField": "user_id",        # Field from the 'comments' collection
#                         "foreignField": "_id",          # Field from the 'users' collection
#                         "as": "user",                   # Output array field
#                     }
#                 },

#                 # Unwind the user array to convert it to a single object
#                 {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},

#                 # Project fields to format the output structure
#                 {
#                     "$project": {
#                         "id": {"$toString": "$_id"},     # Convert ObjectId to string
#                         "content": 1,
#                         "timestamp": 1,
#                         "user": {
#                             "id": {"$toString": "$user._id"},
#                             "username": "$user.username",
#                             "image": "$user.profile_picture_url",
#                         },
#                     }
#                 },
#             ]

#             # Execute the aggregation pipeline
#             cursor = self.find_aggregate('comments', pipeline)

#             return list(cursor)

#         except Exception as e:
#             log.error(f"Error fetching comments: {e}")
#             return []
    
#     def create_post(self, post_data: dict) -> str:
#         """
#         Create a new post in the database.
#         :param post_data: Dictionary containing post details
#         :return: ID of the newly created post
#         """
#         try:
#             result = self.insert_one('posts', post_data)
#             post_id = str(result.inserted_id)
#             update_result = self.update_one(
#                 'users',  
#                 {'_id': post_data.get("user_id")},  
#                 {'$push': {'posts': ObjectId(post_id)}}  
#             )
#             if update_result.modified_count == 0:
#                 log.warning(f"User document was not updated for user_id: {post_data.get("user_id")}")
#             return str(post_id)
#         except Exception as e:
#             log.error(f"Error creating a new post: {e}")
#             return None
        
#     def delete_post(self, post_id: str, user_id: str) -> bool:
#         try:
#             # Delete the post
#             delete_result = self.delete_one('posts', {'_id': ObjectId(post_id)})
#             if delete_result.deleted_count == 0:
#                 log.info(f"No post found with id {post_id} to delete")
#                 return False

#             # Remove the post reference from the user's posts array
#             update_result = self.update_one(
#                 'users',
#                 {'_id': ObjectId(user_id)},
#                 {'$pull': {'posts': ObjectId(post_id)}}
#             )

#             # Delete all reactions associated with the post
#             reactions_delete_result = self.delete_many('reactions', {'post_id': ObjectId(post_id)})
#             log.info(f"Deleted {reactions_delete_result.deleted_count} reactions for post {post_id}")

#             # Delete all comments associated with the post
#             comments_delete_result = self.delete_many('comments', {'post_id': ObjectId(post_id)})
#             log.info(f"Deleted {comments_delete_result.deleted_count} comments for post {post_id}")

#             # Return true if the post and related data were successfully deleted
#             return update_result.modified_count > 0

#         except Exception as e:
#             log.error(f"Error deleting post: {e}")
#             return False
