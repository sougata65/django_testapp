This application starts a webserver that allows you to check user information (their id, realname and timezone) and also the periods of their activity periods on a certain stage.
The data is generated from existing lists of first and last names, timezones and randomly selected timestamps and follows the format provided in the 'Test JSON.json' file.

To use the application go to the server on port 8000.
All the users available in the database can be viewed on the index page ( urls : '/' and 'index/' )
To view any user record just click on the user id from the list on the left.
The record should be displayed in the right side of the page.
Also to browse individual records, go to /users/{userid} where userid has to match the id of an existing user. This will display the same information but on a different page.

Any url other than are not desired and will take you to a "Not found" page.

