<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #c74848;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .title {
            font-size: 4em;
            margin-bottom: 40px;
        }
        .login-container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 300px;
        }
        .login-container h2 {
            margin-bottom: 20px;
        }
        .login-container input[type="email"],
        .login-container input[type="id"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        .login-container input[type="submit"] {
            width: 100%;
            padding: 10px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .login-container input[type="submit"]:hover {
            background-color: #45a049;
        }
        .gap{margin-top: 10px;}
        .club_login{
          color: #2196F3;
        }
        .club_signup {
          color: #2196F3; 
        }
        .club_login:hover{
            background-color: #0660bae2;
        }
        .club_signup:hover {
            background-color: #0660bae2;
        }
    </style>
</head>
<body>
    <div class="title">Eventify</div>
    <div class="login-container">
        <h2>Login</h2>
        <form action="\Login" method="POST">
            <input type="email" name="email" placeholder="G-suite Email" required>
            <input type="id" name="id" placeholder="Id" required>
            <input type="submit" value="Login">
        </form>
            <a class="club_login" href="club_login.html">
              Club Login
            </a>
            <p>   </p>
            <a class="club_signup" href="signup.html">
              Club Sign-up
            </a>
</body>
</html>
