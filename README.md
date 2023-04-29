# Authentication and Authorization Service

## Description

Authentication and authorization service - another part of the online cinema project.
It allows users to register, log in, log out, and manage their accounts. It also allows administrators to manage users and roles.

## Technologies Used

### Databases:

PostgreSQL: Main relational database for primary data storage.
Redis: In-memory data store for caching and token storage.

### Web Framework:

Flask + gevent: Lightweight web framework (Flask) combined with a coroutine-based networking library (gevent) to enable asynchronous functionality and improve the performance of the application.

### Web Server/Reverse Proxy:

Nginx: High-performance web server and reverse proxy server used as the entry point for the web application and for managing client connections.

### Containerization:

Docker: Platform for packaging and deploying applications in isolated containers.

### ORM:

SQLAlchemy: SQL toolkit and Object-Relational Mapping library for database interactions.

## Main Entities
- User: Represents a user with fields such as id, username, email, password, active status, roles, two-factor authentication settings, and social accounts. This entity also includes methods for setting and verifying passwords.

- SocialAccount: Represents a social account associated with a user. It has fields like id, user_id, social_id, and social_provider_name.

- AuthHistory: Represents the authentication history of a user. This includes fields such as id, user_id, IP address, user agent, success status, device, authentication event type and time, and authentication event fingerprint.

- Role: Represents a user role with fields such as id, name, and description. The name field is an enumeration that includes 'user' and 'superuser' roles.

- UserRole: Represents the relationship between a user and a role, with fields like id, user_id, and role_id.

- Token: Represents a token associated with a user, with fields like id, token_owner_id, token_value, token_used status, created_at, and expires_at.

## Working with the Project

### Launch
1. Clone the repository.
```shell
git clone https://github.com/samoilovartem/flask_auth_api.git
```

2. Build and run the project.
```shell
docker compose up --build
```

3. Create a superuser.
```shell
docker exec -it auth_app python manage.py create-superuser --username <USERNAME> --password <PASSWORD>
```
