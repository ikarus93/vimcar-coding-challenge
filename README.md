# BACKEND CODING CHALLENGE FOR VIMCAR


## Basic Structure
**Entry File**: ./app.py
**Unit/Integration Tests**: ./tests.py
**Helper Functions / Middleware Decorators / Other config files**: /misc/
**Database related configuration files**: /db/

I tried solving the given problemset by only using core flask modules, as I hold the opinion that too 
many external libraries would've simplified the core tasks too much - which is showing my programming and program
design capabilities.

I implemented a simple REST API Setup, having all authentication related endpoints underlying **/auth/**.
My applications endpoints function as follows:

**/auth/signup** - The user can sign up to the service, providing his **email** and a **password** in the request body.
Given that all parameters are provided, and the email address is valid, as well as not existing in the application database yet,
I create a user entry inside USERS table in **users.db**, hashing the password obviously.
(I chose an sqllite3 implementation for the data model because of its simplicity), then a response with a status code of 200
gets send back to client.
If a database entry was successful, a link holding the unique primary key from the user entry will be created, and 
send via the **flask-mail** module to the user. This link is used to verify the users email, hence the unique id inside the query string.

The following design pattern will most likely be noticed, I use a try/except pattern to catch errors that might occur,
as well as to raise custom Exceptions when necessary, they hold a status code, that gets mapped to the respective error message,
via a dictionary in **/misc/exceptionsMap.py**.

**/auth/login** - The user can login to the service, provided he supplies his **email** and **password** in the request body.
If the email exists inside the db, and the password is valid (check password against password hash inside db),
a session with the key "user_id" mapping to the users email (as it must be unique) will be created, allowing
the user to access protected resources.

**/auth/logout** - destroys any session (not suitable for production, as any session will be destroyed. If deployed, should only destroy the session
with the matching user_id, however for the sake of simplicity I keep this implementation).

**/verify?id=** - verifies the users email address by mapping the id from the query string to the matching row from the database,
setting its VERIFIED field to 1 (its 0 when created, meaning the email is not verified yet), meaning the email is verified.

**/mock/protected** - a protected route, using a decorator to filter requests where no session exists yet.






