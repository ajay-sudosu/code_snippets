import os

CLIENT_ID = "a46c4487-e934-45f0-b343-63b909e2d806" # Application (client) ID of app registration

CLIENT_SECRET = "97vR~4yX~jT3~JYxqsFDcrNa-521JWY.a2" # Placeholder - for use ONLY during testing.
# In a production app, we recommend you use a more secure method of storing your secret,
# like Azure Key Vault. Or, use an environment variable as described in Flask's documentation:
# https://flask.palletsprojects.com/en/1.1.x/config/#configuring-from-environment-variables
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# if not CLIENT_SECRET:
#     raise ValueError("Need to define CLIENT_SECRET environment variable")

AUTHORITY = "https://login.microsoftonline.com/common"  # For multi-tenant app
# AUTHORITY = "https://login.microsoftonline.com/Enter_the_Tenant_Name_Here"

REDIRECT_PATH = "/"  # Used for forming an absolute URL to your redirect URI.
                              # The absolute URL must match the redirect URI you set
                              # in the app's registration in the Azure portal.

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
ENDPOINT = 'https://graph.microsoft.com/v1.0/me'  # This resource requires no admin consent

# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["User.ReadBasic.All"]


SESSION_TYPE = "sqlalchemy"  # Specifies the token cache should be stored in server-side session

SQLALCHEMY_TRACK_MODIFICATIONS = False

MAX_CONTENT_LENGTH = 1024 * 1024 * 100
SESSION_SQLALCHEMY_TABLE = "sessions"
