# Static variables
GOOGLE_ACCOUNTS_BASE_URL = 'https://accounts.google.com'
REDIRECT_URI = 'http://www.silverlantern.net/oauth2callback'

FAIL = 1
OK = 0
YIELD = 2

TEST_OAUTH_CALLBACK = '/oauth2callback/?code=4/eQo7VL5ZqudITMqpjXn03aXRAdEs.Uso5fqMgKTwQuJJVnL49Cc_EqBqKeQI'

TEST_EMAIL_TEMPLATE = """X-Gmail-Received: ee7989d8ac8d7a5667a5e521b5d93b6aa07c9b25
Received: by 10.54.120.8 with HTTP; Sat, 4 Mar 2006 08:54:34 -0800 (PST)
Message-ID: <ead59d740603040854g58d51258xae1e2c7963ea908f@mail.gmail.com>
Date: Sat, 4 Mar 2006 08:54:34 -0800
From: "Peter Banka" <peter.banka@gmail.com>
To: botke3432@comcast.net
Subject: Re: Sunday/Unity
In-Reply-To: <030320061708.14299.44087802000EBC99000037DB2200750744CDCCCBCC0A059B010D@comcast.net>
MIME-Version: 1.0
Content-Type: text/plain; charset=ISO-8859-1
Content-Transfer-Encoding: quoted-printable
Content-Disposition: inline
References: <030320061708.14299.44087802000EBC99000037DB2200750744CDCCCBCC0A059B010D@comcast.net>
Delivered-To: peter.banka@gmail.com

%s

On 2/27/06, Thomas Seeling <thomas.seeling@gmx.net> wrote:
> -----BEGIN PGP SIGNED MESSAGE-----
> Hash: SHA1
>
> Hallo,
>
>
> I'm looking for software distribution systems that are
> available multi-platform, i.e. support at least windows and
"""

TEST_GOOGLE_REPLY = {
    'code': '4/eQo7VL5ZqudITMqpjXn03aXRAdEs.Uso5fqMgKTwQuJJVnL49Cc_EqBqKeQI',
    'id_token':  'eyJhbGciOiJSUzI1NiIsImtpZCI6Ijk5ZmIwMTUyNzY5MDU5MWI2YjhkOGRhOGM3NDNmOWE1NzUyMmY1ZTAifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwidG9rZW5faGFzaCI6IndQNEFBc2ktMXBMWVd4U3NJNzNnZkEiLCJhdF9oYXNoIjoid1A0QUFzaS0xcExZV3hTc0k3M2dmQSIsImF1ZCI6IjU1NDI5Mzk2MTYyMy5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsImlkIjoiMTAwMzI3NDIyODE3ODY2Njk5NzYxIiwic3ViIjoiMTAwMzI3NDIyODE3ODY2Njk5NzYxIiwiY2lkIjoiNTU0MjkzOTYxNjIzLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwiYXpwIjoiNTU0MjkzOTYxNjIzLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwiaWF0IjoxMzYwNTE1MjMyLCJleHAiOjEzNjA1MTkxMzJ9.oYHa5Wv0wIa9Ai-te5uGLFEYASFmoPWeF0NU299UJc0dVddrOywFUp2dOEYx9gnBZIh7hrI7tOoEH93yxk3_rYJuALWQZ_DOFIwyxhcAnys29xGdZW_DaM5ZNXixvhJIS5Day1DoH0NdgBl2C6ACUGU63UC6c2LVGNTfbM6-Bpc',
    'access_token': 'ya29.AHES6ZSbVJG3D8Q1Qo7RFxXSAnAjESLWwHnPTSwRqhbbg84',
    'token_type': 'Bearer',
    'expires_in': '3599',
}
