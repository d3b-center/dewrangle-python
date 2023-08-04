# D3b Dewrangle Python API

Python API for interacting with [Dewrangle](https://github.com/kids-first/dewrangle).

## Quick Dewrangle API Overview

The Dewrangle API uses [Relay](https://relay.dev/) GraphQL. The Python API uses the [gql](https://github.com/graphql-python/gql) library.

## Getting Started

Before running any of the API scripts, an authentication tocken must be created on Dewrangle and stored in the credentials.py file located in the root directory of this repo.

1. Login to [Dewrangle](https://dewrangle.com/)

1. Click on you profile and go to Settings

1. Click Generate new token and copy the token into credentials.py

### credentials.py file

```
api_key = "<<YOUR_KEY>>"
```