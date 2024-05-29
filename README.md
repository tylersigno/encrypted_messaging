# SecureChat - End-to-End Encrypted Messaging Web Application

SecureChat is a web application designed to provide secure, real-time messaging between users. The application ensures the privacy and security of user communications through end-to-end encryption, robust authentication mechanisms, and user-friendly features for managing friends and messages.

## Features

- **User Authentication**: Secure registration and login processes using hashed passwords (SHA-256) and session management with Flask.
- **End-to-End Encryption**: All messages are encrypted using AES-GCM encryption to ensure privacy and security.
- **Real-Time Messaging**: Instantaneous message exchange using Socket.IO for real-time, bidirectional communication.
- **Friend Management**: Users can send, accept, and manage friend requests to build their contact list.
- **Secure Storage**: User data, including messages and friend lists, are securely stored and accessed.

## Technologies Used

### Languages
- **Python**: Server-side programming for handling business logic, authentication, and encryption.
- **JavaScript**: Client-side scripting for dynamic user interactions and asynchronous communication.
- **HTML/CSS**: Structuring and styling the web pages for a responsive and interactive user interface.

### Libraries and Frameworks
- **Flask**: Lightweight web framework for Python, used for building the server-side application and managing routes.
- **Socket.IO**: JavaScript library for enabling real-time, bidirectional communication between the client and server.
- **Jinja**: Templating engine for Python, used with Flask to render dynamic HTML content.
- **Axios**: Promise-based HTTP client for JavaScript, used for making asynchronous requests to the server.
- **jQuery**: JavaScript library for simplifying DOM manipulation and event handling.
- **CryptoJS**: Library for JavaScript cryptographic operations, used for client-side encryption and hashing.

### Security
- **AES-GCM Encryption**: Implemented to secure message content, ensuring only the intended recipient can decrypt and read the messages.
- **SHA-256 Hashing**: Used for securely hashing user passwords before storing them in the database.
- **CSRF Protection**: Ensured through Flask's built-in security features to protect against cross-site request forgery attacks.

### Development Tools
- **Git**: Version control system for managing project codebase and collaboration.
- **VS Code**: Code editor used for development with extensions to support Python and JavaScript.