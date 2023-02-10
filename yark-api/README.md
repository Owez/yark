# Yark API

YouTube archiving made simple (REST API)

## End-user

Want to deploy your own federated Yark instance to connect to? You can do it using Yark API + Docker ✨

TODO: add docker and then make this guide

## Development

To get this API setup, please first install Python 3.11 and make sure you've got Poetry installed. With these installed, you can download the dependencies for the API:

```shell
$ poetry install
```

Once you've got all of the dependencies installed, create a new `.env` file and put in some environment variables:

```env
YARK_DATABASE_URI=sqlite:///example.db
YARK_SECRET=supersecure
```

You now have everything installed and you're not ready to develop! Switch your IDE to use the newly-created virtual environment. To run the API in debug mode, just run the following:

```shell
$ poetry run poe dev
```
