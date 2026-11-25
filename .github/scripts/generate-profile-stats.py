import html
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


USERNAME = "imtushaarr"
API = "https://api.github.com"


def github_json(url: str) -> dict | list:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "imtushaarr-profile-readme",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def format_count(value: int) -> str:
    return f"{value:,}"


def main() -> None:
    user = github_json(f"{API}/users/{USERNAME}")
    repositories = []
    page = 1
    while True:
        batch = github_json(
            f"{API}/users/{USERNAME}/repos?type=owner&per_page=100&page={page}"
        )
        repositories.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    original_repos = [repo for repo in repositories if not repo["fork"]]
    stars = sum(repo["stargazers_count"] for repo in original_repos)
    values = [
        ("PUBLIC REPOSITORIES", user["public_repos"]),
        ("FOLLOWERS", user["followers"]),
        ("STARS ON ORIGINAL REPOS", stars),
    ]

    cards = []
    for index, (label, value) in enumerate(values):
        x = 35 + index * 280
        cards.append(
            f"""
            <g transform="translate({x}, 88)">
              <rect width="250" height="132" rx="18" fill="#111827" stroke="#293548"/>
              <text x="22" y="39" class="label">{html.escape(label)}</text>
              <text x="22" y="92" class="value">{format_count(value)}</text>
              <rect x="22" y="111" width="0" height="3" rx="2" fill="#38bdf8">
                <animate attributeName="width" from="0" to="206" dur="1.1s" fill="freeze"/>
              </rect>
            </g>
            """
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="250" viewBox="0 0 900 250" role="img" aria-labelledby="title description">
      <title id="title">GitHub profile statistics for {USERNAME}</title>
      <desc id="description">Public repositories, followers, and stars across original repositories.</desc>
      <defs>
        <linearGradient id="background" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#0b1220"/>
          <stop offset="100%" stop-color="#172554"/>
        </linearGradient>
        <style>
          .heading {{ font: 600 18px system-ui, sans-serif; fill: #e2e8f0; letter-spacing: 1.5px; }}
          .label {{ font: 600 11px system-ui, sans-serif; fill: #94a3b8; letter-spacing: 1px; }}
          .value {{ font: 700 34px system-ui, sans-serif; fill: #f8fafc; }}
        </style>
      </defs>
      <rect width="900" height="250" rx="24" fill="url(#background)"/>
      <circle cx="850" cy="30" r="3" fill="#38bdf8">
        <animate attributeName="opacity" values="0.35;1;0.35" dur="2.4s" repeatCount="indefinite"/>
      </circle>
      <text x="35" y="48" class="heading">GITHUB PROFILE · {USERNAME.upper()}</text>
      {''.join(cards)}
    </svg>
    """

    output = Path("dist")
    output.mkdir(parents=True, exist_ok=True)
    (output / "profile-stats.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
