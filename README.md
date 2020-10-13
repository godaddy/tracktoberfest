# tracktoberfest

Retrieve Hacktoberfest contributions for a list of GitHub usernames.

Their "validity" is calculated based on the rules enumerated in the Digital
Ocean blog post: <https://hacktoberfest.digitalocean.com/hacktoberfest-update>

Example:

```console
> tracktoberfest tarkatronic
Retrieving contributions for tarkatronic...
tarkatronic
    Counted! - https://github.com/godaddy/tartufo/pull/111
    Counted! - https://github.com/godaddy/tartufo/pull/109
    Counted! - https://github.com/godaddy/tartufo/pull/103
```

## Installation

```console
> pip install tracktoberfest
```

## Usage

In order to use this library you will need to expose a environment variable named `GITHUB_TOKEN`
to do this you can create a `.env` file and export the variable

```bash
export GITHUB_TOKEN='foo'
```

before running the application in your terminal run:

```bash
source .env
```

After that you can run:

```bash
tracktoberfest tarkatronic
```
