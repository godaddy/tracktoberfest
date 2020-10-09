import datetime
import os
from typing import Any, Dict, Iterable, List, Tuple, Union

import click
import colorama
import httpx
import iso8601
from colorama import Fore, Style


JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HACKTOBERFEST_YEAR = 2020


START_TIME = datetime.datetime(
    HACKTOBERFEST_YEAR, 10, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
)


def run_query(query: str, variables: Dict[str, Any] = None) -> JSONType:
    req = httpx.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers={"Authorization": f"bearer {GITHUB_TOKEN}"},
    )
    if req.status_code == 200:
        return req.json()
    raise Exception(
        f"Query failed with return code {req.status_code}.\n"
        f"Query: {query}\n"
        f"Variables: {variables}\n"
        f"Request headers: {req.request.headers}"
    )


def get_user_contributions(username: str) -> JSONType:
    print(f"Retrieving contributions for {username}...")
    results = run_query(
        """query ($username: String!) {
  user(login: $username) {
    name
    pullRequests(first: 30, orderBy: {field: CREATED_AT, direction: DESC}) {
      edges {
        node {
          permalink
          title
          createdAt
          merged
          reviewDecision
          labels(first: 20) {
            edges {
              node {
                name
              }
            }
          }
          baseRepository {
            repositoryTopics(first: 50) {
              edges {
                node {
                  topic {
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
""",
        {"username": username},
    )
    results = [
        {
            "username": username,
            "name": results["data"]["user"]["name"],
            "permalink": result["node"]["permalink"],
            "title": result["node"]["title"],
            "createdAt": result["node"]["createdAt"],
            "merged": result["node"]["merged"],
            "approved": result["node"]["reviewDecision"] == "APPROVED",
            "labels": [
                label["node"]["name"] for label in result["node"]["labels"]["edges"]
            ],
            "repositoryTopics": [
                topic["node"]["topic"]["name"]
                for topic in result["node"]["baseRepository"]["repositoryTopics"][
                    "edges"
                ]
            ],
        }
        for result in results["data"]["user"].get("pullRequests", {}).get("edges", {})
    ]
    return list(map(flag_valid_contributions, filter(filter_by_date, results)))


def flag_valid_contributions(contribution: JSONType) -> JSONType:
    contribution["valid"] = (
        "hacktoberfest-accepted" in contribution["labels"]
        or contribution["merged"]
        or contribution["approved"]
    )
    return contribution


def filter_by_date(contribution: JSONType) -> bool:
    contrib_time = iso8601.parse_date(contribution["createdAt"])
    return contrib_time >= START_TIME


def get_all_contributions(users: Iterable[str]):
    contributions = {user: get_user_contributions(user) for user in users}
    return contributions


def print_user_contributions(username: str, contributions: JSONType) -> None:
    print(f"{Fore.CYAN}{username}{Style.RESET_ALL}")
    if not contributions:
        print("\tNo pull requests found!")
        return

    for contribution in contributions:
        if contribution["valid"]:
            print(
                f"\t{Fore.GREEN}    Counted!{Style.RESET_ALL} - {contribution['permalink']}"
            )
        else:
            print(
                f"\t{Fore.RED}Not counted.{Style.RESET_ALL} - {contribution['permalink']}"
            )


@click.command(name="tracktoberfest")
@click.argument("username", required=True, nargs=-1)
@click.pass_context
def main(ctx: click.Context, username: Tuple[str]):
    """Retrieve Hacktoberfest contributions for a list of GitHub usernames.

    Their "validity" is calculated based on the rules enumerated in the Digital
    Ocean blog post: https://hacktoberfest.digitalocean.com/hacktoberfest-update
    """
    if not GITHUB_TOKEN:
        click.echo("No GITHUB_TOKEN environment variable found!")
        ctx.exit(1)
    all_contributions = get_all_contributions(username)
    colorama.init()
    for username, contributions in all_contributions.items():
        print_user_contributions(username, contributions)
