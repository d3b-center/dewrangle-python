# D3b Dewrangle Python API

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Python API for interacting with [Dewrangle](https://github.com/kids-first/dewrangle).

## Quick Dewrangle API Overview

The Dewrangle API uses [Relay](https://relay.dev/) GraphQL. The Python API uses the [gql](https://github.com/graphql-python/gql) library.

## Getting Started

Before running any of the API scripts, an authentication tocken must be created on Dewrangle and stored in the credential.py file located in the root directory of this repo.

1. Login to [Dewrangle](https://dewrangle.com/)

1. Click on you profile and go to Settings

1. Click Generate new token and copy the token into `~/.dewrangle/credentials`

1. Install the dewrangle-python package

### credentials file

The `~/.dewrangle/credentials` is a basic INI file with one section `[default]`

```
[default]
	api_key = "<<YOUR_KEY>>"
```

## Installing the dewrangle-python package

To install the package, simply run:
```
pip install dewrangle-python
```

## Get the Code

To get the code and run the predeveloped scripts locally, clone this repo and either install the package via `pip` or build it locally.

Clone this repo:
```
git clone https://github.com/d3b-center/dewrangle-python.git
```

Install the package locally:
```
cd dewrangle-python
pip install -e .
```