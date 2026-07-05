## Library App

Create a Django app that does the following:
1. Login and SignUp of a user. (Add JWT later)
2. A user can issue a book.
3. A user has to return an issued book.
4. Every user can have a max of 5 books issued at any given time.
5. There can be multiple copies of the same book in the library.
6. Increment/Decrement the count of the book when it is returned/issued.
7. Return date is 15 days from the date of issue.
8. If returned later, levy Rs. 5 for every extra day.