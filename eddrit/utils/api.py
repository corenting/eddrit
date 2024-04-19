import random
from base64 import standard_b64encode
from datetime import timedelta
from uuid import uuid4

import httpx
from cachier import cachier
from loguru import logger

from eddrit.exceptions import RateLimitedError

OFFICIAL_ANDROID_OAUTH_ID = "ohXpoqrZYub1kg"
OFFICIAL_ANDROID_APP_VERSIONS = [
    "Version 2024.16.0/Build 1551366",
    "Version 2024.15.0/Build 1536823",
    "Version 2024.14.0/Build 1520556",
    "Version 2024.13.0/Build 1505187",
    "Version 2024.12.0/Build 1494694",
    "Version 2024.11.0/Build 1480707",
    "Version 2024.10.1/Build 1478645",
    "Version 2024.10.0/Build 1470045",
    "Version 2024.08.0/Build 1439531",
    "Version 2024.07.0/Build 1429651",
    "Version 2024.06.0/Build 1418489",
    "Version 2024.05.0/Build 1403584",
    "Version 2024.04.0/Build 1391236",
    "Version 2024.03.0/Build 1379408",
    "Version 2024.02.0/Build 1368985",
    "Version 2023.50.1/Build 1345844",
    "Version 2023.50.0/Build 1332338",
    "Version 2023.49.1/Build 1322281",
    "Version 2023.49.0/Build 1321715",
    "Version 2023.48.0/Build 1319123",
    "Version 2023.47.0/Build 1303604",
    "Version 2023.45.0/Build 1281371",
    "Version 2023.44.0/Build 1268622",
    "Version 2023.43.0/Build 1257426",
    "Version 2023.42.0/Build 1245088",
    "Version 2023.41.1/Build 1239615",
    "Version 2023.41.0/Build 1233125",
    "Version 2023.40.0/Build 1221521",
    "Version 2023.39.1/Build 1221505",
    "Version 2023.39.0/Build 1211607",
    "Version 2023.38.0/Build 1198522",
    "Version 2023.37.0/Build 1182743",
    "Version 2023.36.0/Build 1168982",
    "Version 2023.35.0/Build 1157967",
    "Version 2023.34.0/Build 1144243",
    "Version 2023.33.1/Build 1129741",
    "Version 2023.32.1/Build 1114141",
    "Version 2023.32.0/Build 1109919",
    "Version 2023.31.0/Build 1091027",
    "Version 2023.30.0/Build 1078734",
    "Version 2023.29.0/Build 1059855",
    "Version 2023.28.0/Build 1046887",
    "Version 2023.27.0/Build 1031923",
    "Version 2023.26.0/Build 1019073",
    "Version 2023.25.1/Build 1018737",
    "Version 2023.25.0/Build 1014750",
    "Version 2023.24.0/Build 998541",
    "Version 2023.23.0/Build 983896",
    "Version 2023.22.0/Build 968223",
    "Version 2023.21.0/Build 956283",
    "Version 2023.20.1/Build 946732",
    "Version 2023.20.0/Build 943980",
    "Version 2023.19.0/Build 927681",
    "Version 2023.18.0/Build 911877",
    "Version 2023.17.1/Build 900542",
    "Version 2023.17.0/Build 896030",
    "Version 2023.16.1/Build 886269",
    "Version 2023.16.0/Build 883294",
    "Version 2023.15.0/Build 870628",
    "Version 2023.14.1/Build 864826",
    "Version 2023.14.0/Build 861593",
    "Version 2023.13.0/Build 852246",
    "Version 2023.12.0/Build 841150",
    "Version 2023.11.0/Build 830610",
    "Version 2023.10.0/Build 821148",
    "Version 2023.09.1/Build 816833",
    "Version 2023.09.0/Build 812015",
    "Version 2023.08.0/Build 798718",
    "Version 2023.07.1/Build 790267",
    "Version 2023.07.0/Build 788827",
    "Version 2023.06.0/Build 775017",
    "Version 2023.05.0/Build 755453",
    "Version 2023.04.0/Build 744681",
    "Version 2023.03.0/Build 729220",
    "Version 2023.02.0/Build 717912",
    "Version 2023.01.0/Build 709875",
    "Version 2022.9.0/Build 426592",
    "Version 2022.8.0/Build 423906",
    "Version 2022.7.0/Build 420849",
    "Version 2022.6.2/Build 420562",
    "Version 2022.6.1/Build 419585",
    "Version 2022.6.0/Build 418391",
    "Version 2022.5.0/Build 414731",
    "Version 2022.45.0/Build 677985",
    "Version 2022.44.0/Build 664348",
    "Version 2022.43.0/Build 648277",
    "Version 2022.42.0/Build 638508",
    "Version 2022.41.1/Build 634168",
    "Version 2022.41.0/Build 630468",
    "Version 2022.40.0/Build 624782",
    "Version 2022.4.0/Build 411368",
    "Version 2022.39.1/Build 619019",
    "Version 2022.39.0/Build 615385",
    "Version 2022.38.0/Build 607460",
    "Version 2022.37.0/Build 601691",
    "Version 2022.36.0/Build 593102",
    "Version 2022.35.1/Build 589034",
    "Version 2022.35.0/Build 588016",
    "Version 2022.34.0/Build 579352",
    "Version 2022.33.0/Build 572600",
    "Version 2022.32.0/Build 567875",
    "Version 2022.31.1/Build 562612",
    "Version 2022.31.0/Build 556666",
    "Version 2022.30.0/Build 548620",
    "Version 2022.3.0/Build 408637",
    "Version 2022.28.0/Build 533235",
    "Version 2022.27.1/Build 529687",
    "Version 2022.27.0/Build 527406",
    "Version 2022.26.0/Build 521193",
    "Version 2022.25.2/Build 519915",
    "Version 2022.25.1/Build 516394",
    "Version 2022.25.0/Build 515072",
    "Version 2022.24.1/Build 513462",
    "Version 2022.24.0/Build 510950",
    "Version 2022.23.1/Build 506606",
    "Version 2022.23.0/Build 502374",
    "Version 2022.22.0/Build 498700",
    "Version 2022.21.0/Build 492436",
    "Version 2022.20.0/Build 487703",
    "Version 2022.2.0/Build 405543",
    "Version 2022.19.1/Build 482464",
    "Version 2022.18.0/Build 473740",
    "Version 2022.17.0/Build 468480",
    "Version 2022.16.0/Build 462377",
    "Version 2022.15.0/Build 455453",
    "Version 2022.14.1/Build 452742",
    "Version 2022.13.1/Build 444621",
    "Version 2022.13.0/Build 442084",
    "Version 2022.12.0/Build 436848",
    "Version 2022.11.0/Build 433004",
    "Version 2022.10.0/Build 429896",
    "Version 2022.1.0/Build 402829",
    "Version 2021.47.0/Build 394342",
    "Version 2021.46.0/Build 392043",
    "Version 2021.45.0/Build 387663",
    "Version 2021.44.0/Build 385129",
    "Version 2021.43.0/Build 382019",
    "Version 2021.42.0/Build 378193",
    "Version 2021.41.0/Build 376052",
    "Version 2021.39.1/Build 372418",
    "Version 2021.39.0/Build 369068",
    "Version 2021.38.0/Build 365032",
    "Version 2021.37.0/Build 361905",
    "Version 2021.36.1/Build 360572",
    "Version 2021.36.0/Build 359254",
    "Version 2021.35.0/Build 355878",
    "Version 2021.34.0/Build 353911",
    "Version 2021.33.0/Build 351843",
    "Version 2021.32.0/Build 349507",
    "Version 2021.31.0/Build 346485",
    "Version 2021.30.0/Build 343820",
    "Version 2021.29.0/Build 342342",
    "Version 2021.28.0/Build 340747",
    "Version 2021.27.0/Build 338857",
    "Version 2021.26.0/Build 336739",
    "Version 2021.25.0/Build 335451",
    "Version 2021.24.0/Build 333951",
    "Version 2021.23.0/Build 331631",
    "Version 2021.22.0/Build 329696",
    "Version 2021.21.1/Build 328461",
    "Version 2021.21.0/Build 327703",
    "Version 2021.20.0/Build 326964",
]


async def event_hook_raise_if_rate_limited_on_response(api_res: httpx.Response) -> None:
    """Event hook to raise a specific exception if Reddit returns a 429 (rate-limit reached)."""
    if api_res.status_code == 429:
        raise RateLimitedError()


async def event_hook_add_official_android_app_headers_to_request(
    request: httpx.Request,
) -> None:
    """
    Event hook to add the official Android app headers to the request
    """
    # Remove our user-agent
    request.headers.pop("User-Agent")

    # Add the Android official app headers
    android_headers = get_official_android_app_headers()
    for header_name, header_value in android_headers.items():
        request.headers[header_name] = header_value


@cachier(stale_after=timedelta(hours=23, minutes=50))
def get_official_android_app_headers() -> dict[str, str]:
    """
    Get headers matching the official Android app.
    """

    # Generate identity: unique ID + random user-agent
    unique_uuid = str(uuid4())
    android_app_version = random.choice(OFFICIAL_ANDROID_APP_VERSIONS)  # noqa: S311
    android_version = random.choice(range(9, 15))  # noqa: S311
    common_headers = {
        "Client-Vendor-Id": unique_uuid,
        "X-Reddit-Device-Id": unique_uuid,
        "User-Agent": f"Reddit/{android_app_version}/Android {android_version}",
    }
    logger.debug(f"Generated headers for official Android app login: {common_headers}")

    # Login
    client = httpx.Client()  # not async but not supported by cachier
    id_to_encode = f"{OFFICIAL_ANDROID_OAUTH_ID}:"
    res = client.post(
        url="https://accounts.reddit.com/api/access_token",
        headers={
            "Authorization": f"Basic {standard_b64encode(id_to_encode.encode()).decode()}",
            **common_headers,
        },
        json={"scopes": ["*", "email"]},
    )

    if res.is_success:
        return {
            **common_headers,
            "Authorization": f"Bearer {res.json()['access_token']}",
            "x-reddit-loid": res.headers["x-reddit-loid"],
            "x-reddit-session": res.headers["x-reddit-session"],
        }
    else:
        logger.debug(
            f"Got {res.status_code} response for official Android app login: {res.json()}"
        )
        raise RuntimeError(
            "Cannot generate credentials for Reddit by spoofing the official Android app"
        )
