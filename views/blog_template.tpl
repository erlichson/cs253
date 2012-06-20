<!DOCTYPE html>
<html>
<head>
<title>My Blog</title>
</head>
<body>

<h1>My Blog</h1>

%for post in myposts:
{{post['post_date']}}
<h2>{{post['title']}}</h2>
<hr>
{{post['content']}}
<p>
<p>
%end
</body>
</html>


