# pocket-to-sqlite

[![PyPI](https://img.shields.io/pypi/v/pocket-to-sqlite.svg)](https://pypi.org/project/pocket-to-sqlite/)
[![CircleCI](https://circleci.com/gh/dogsheep/pocket-to-sqlite.svg?style=svg)](https://circleci.com/gh/dogsheep/pocket-to-sqlite)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/dogsheep/pocket-to-sqlite/blob/master/LICENSE)

Create a SQLite database containing data from your Pocket account

## How to install

    $ pip install pocket-to-sqlite

## Usage

You will need to first obtain a valid OAuth token for your Pocket account. You can do this by running the `auth` command and following the prompts:

    $ pocket-to-sqlite auth
    Visit this page and sign in with your Pocket account:

    https://getpocket.com/auth/author...

    Once you have signed in there, hit <enter> to continue
    Authentication tokens written to auth.json
