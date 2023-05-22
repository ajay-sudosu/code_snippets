from django.http import HttpResponse

unauthorized_html = '''
    <!DOCTYPE html>
<html>
<head>
<title>Unauthorized Access</title>
<link rel="stylesheet" type="text/css" href="style.css">
</head>
<style>
body {
background-color: #f2f2f2;
font-family: Arial, sans-serif;
}

.container {
margin: 50px auto;
padding: 20px;
background-color: #fff;
border: 1px solid #ddd;
border-radius: 5px;
box-shadow: 0 0 10px rgba(0,0,0,0.1);
width: 80%;
max-width: 600px;
text-align: center;
}

h1 {
color: #f00;
font-size: 36px;
margin-bottom: 20px;
}

p {
font-size: 18px;
margin-bottom: 10px;
}

</style>
<body>
<div class="container">
    <h1>Unauthorized Access</h1>
    <p>You do not have permission to access this page.</p>
</div>
</body>
</html>
    '''
class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in ['/department','/admin', '/roles', '/employee']:  # Add the URLs that you want to restrict access to here
            if not request.user.is_admin:
                print(request.user)
                return HttpResponse(unauthorized_html)  # replace 'restricted' with the URL of the page you want to redirect to

        response = self.get_response(request)

        return response
