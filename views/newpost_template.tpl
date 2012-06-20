<!doctype HTML>
<html>
<head>
<title>Create a new post</title>
</head>
<body>
<form action="/blog/newpost" method="POST">
{{errors}}
<h2>Title</h2>
<input type="text" name="subject" size="120" value="{{subject}}"><br>
<h2>Blog Entry<h2>
<textarea name="content" cols="120" rows="20">{{content}}</textarea><br>
<input type="submit" value="Submit">
<p>
</body>
</html>

