import datetime
import json
import urllib.error
import urllib.parse
import urllib.request

EDAM_TOPICS = [
    "Genomics",
    "Comparative genomics",
    "Sequence analysis",
    "Genetic variation",
    "Structural variation",
    "Alignment",
    "Gene structure",
    "Whole genome sequencing",
]

CURRENT_YEAR = datetime.date.today().year
OPENALEX_HEADERS = {"User-Agent": "fetch_biotools/1.0"}


def fetch_openalex(identifier_url: str):
    url = f"https://api.openalex.org/works/{identifier_url}"
    try:
        req = urllib.request.Request(url, headers=OPENALEX_HEADERS)
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status != 200:
                return None
            return json.loads(response.read().decode())
    except Exception:
        return None


def citation_score_for_publication(pub: dict) -> float:
    doi = pub.get("doi")
    pmcid = pub.get("pmcid")
    pmid = pub.get("pmid")

    if doi:
        identifier_url = f"https://doi.org/{doi}"
    elif pmcid:
        identifier_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}"
    elif pmid:
        identifier_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}"
    else:
        return 0.0

    try:
        data = fetch_openalex(identifier_url)
        if not data:
            return 0.0

        counts_by_year = data.get("counts_by_year", [])
        if not counts_by_year:
            return 0.0

        cutoff_year = CURRENT_YEAR - 9  # last 10 years inclusive
        recent = [e for e in counts_by_year if e.get("year", 0) >= cutoff_year]
        if not recent:
            return 0.0

        score = 0.0
        for entry in recent:
            year = entry.get("year", 0)
            cited = entry.get("cited_by_count", 0)
            years_ago = CURRENT_YEAR - year  # 0 for current year
            coefficient = max(1.0 - years_ago * 0.05, 0.0)
            score += cited * coefficient

        return score
    except Exception:
        return 0.0


def compute_tool_citation_score(tool: dict):
    publications = tool.get("publication")
    if not publications:
        return None

    total = sum(citation_score_for_publication(pub) for pub in publications)
    return round(total, 2)


def fetch_tools():
    result = []
    seen_ids = set()

    for index, topic in enumerate(EDAM_TOPICS):
        params = urllib.parse.urlencode({
            "cost": "Free of charge",
            "format": "json",
            "inputDataFormat": "FASTA",
            "maturity": "Mature",
            "per_page": 1000,
            "topic": topic,
        })
        url = f"https://bio.tools/api/tool/?{params}"
        print(f"Fetching ({index + 1}/{len(EDAM_TOPICS)}): {url}")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "fetch_biotools/1.0"})
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status != 200:
                    raise urllib.error.HTTPError(url, response.status, "HTTP error", {}, None)
                data = json.loads(response.read().decode())
        except urllib.error.URLError as e:
            print(f"  Request error for '{topic}': {e}")
            continue
        except (json.JSONDecodeError, ValueError) as e:
            print(f"  JSON parse error for '{topic}': {e}")
            continue

        tools = data.get("list", [])
        added = 0
        for tool in tools:
            biotools_id = tool.get("biotoolsID")
            if not biotools_id or biotools_id in seen_ids:
                continue

            score = compute_tool_citation_score(tool)
            if score is None:
                continue  # no publications — skip

            tool["citation_score"] = score
            seen_ids.add(biotools_id)
            result.append(tool)
            added += 1

        print(f"  Topic ({index + 1}/{len(EDAM_TOPICS)}) '{topic}': {len(tools)} tools fetched, {added} new added (total: {len(result)})")

    return result


if __name__ == "__main__":
    tools = fetch_tools()
    tools.sort(key=lambda t: t["citation_score"], reverse=True)

    print(f"\nDone. Total unique tools with publications: {len(tools)}")
    print(f"\n{'#':<5} {'Name':<40} {'biotoolsID':<30} {'Citation score':>14}")
    print("-" * 92)
    for rank, tool in enumerate(tools, start=1):
        print(f"{rank:<5} {tool.get('name', ''):<40} {tool.get('biotoolsID', ''):<30} {tool['citation_score']:>14.2f}")
