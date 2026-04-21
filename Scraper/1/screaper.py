from dataclasses import dataclass
import csv
import json
import os
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

@dataclass
class Board:
    id: int
    name: str


boards = [
    Board(1002, "BOARD OF HIGHER SECONDARY EXAMINATION( KERALA HSE)"),
    Board(1014, "Board of Intermediate Education, A. P."),
    Board(1011, "BOARD OF TECHNICAL HIGHER SECONDARY EDUCATION (THSE)"),
    Board(1003, "BOARD OF VOCATIONAL HIGHER SECONDARY EXAMINATIONS (KERALA VHSE)"),
    Board(1006, "CENTRAL BOARD OF SECONDARY EDUCATION (CBSE)"),
    Board(1005, "COUNCIL FOR THE INDIAN SCHOOL CERTIFICATE EXAMINATIONS,NEW DELHI"),
    Board(1020, "COUNCIL OF HIGHER SECONDARY EDUCATION,ODISHA"),
    Board(1007, "DEPARTMENT OF PRE-UNIVERSITY EDUCATION(KARNATAKA)"),
    Board(1022, "General Certificate of Secondary Education (GCSE), UK"),
    Board(1028, "Goa Board of Higher Secondary"),
    Board(1016, "GUJARAT HIGHER SECONDARY BOARD,GANDHINAGAR"),
    Board(1034, "Jammu and Kashmir board of secondary education (JKBOSE)"),
    Board(1029, "Jharhand state open school,jsos"),
    Board(1013, "Kerala State Open School"),
    Board(1026, "MADHYA PRADESH BOARD OF SECONDARY EDUCATION"),
    Board(1017, "Maharashtra State Board Of Secondary And Higher Secondary Education, Pune"),
    Board(1032, "Mizoram Board of School Education (MBSE)"),
    Board(1021, "NAGALAND BOARD OF SCHOOL EDUCATION,KOHIMA"),
    Board(1004, "NATIONAL INSTITUTE OF OPEN SCHOOLING (NIOS)"),
    Board(1033, "Pre-Degree Mahatma Gandhi University"),
    Board(1030, "Punjab School Education Board "),
    Board(1027, "Rural institute of open schooling"),
    Board(1008, "STATE BOARD OF SCHOOL EXAMINATIONS,TAMIL NADU"),
    Board(1015, "State Examinations Commission"),
    Board(1019, "Telangana state board of Intermediate education "),
    Board(1018, "West Bengal Council of Higher Secondary Education"),
]


BASE_URL = "https://services.cmscollege.ac.in/UGAdmission/Admission"
STREAMS_URL = f"{BASE_URL}/BindHscStream"
PROGRAMMES_URL = f"{BASE_URL}/BindHscProgramme"


BASE_HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "content-type": "application/json; charset=utf-8",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://services.cmscollege.ac.in/UGAdmission/Admission/Application_New_UG",
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
    ),
}


@dataclass
class Stream:
    hsc_pgm_id: int
    board_id: int
    stream: str


def build_headers() -> dict[str, str]:
    headers = dict(BASE_HEADERS)

    # Cloudflare-protected endpoint often requires fresh cookies.
    cf_clearance = os.getenv("CF_CLEARANCE", "").strip()
    aspnet_session = os.getenv("ASPNET_SESSIONID", "").strip()
    cookie_header = os.getenv("COOKIE_HEADER", "").strip()

    if cookie_header:
        headers["cookie"] = cookie_header
    else:
        cookies: list[str] = []
        if cf_clearance:
            cookies.append(f"cf_clearance={cf_clearance}")
        if aspnet_session:
            cookies.append(f"ASP.NET_SessionId={aspnet_session}")
        if cookies:
            headers["cookie"] = "; ".join(cookies)

    return headers


def now_ms() -> int:
    return int(time.time() * 1000)


def fetch_json(url: str, params: dict[str, int], headers: dict[str, str]) -> Any:
    query = urlencode(params)
    request = Request(f"{url}?{query}", headers=headers, method="GET")
    with urlopen(request, timeout=30) as response:
        data = response.read().decode("utf-8")
    return json.loads(data)


def fetch_streams(headers: dict[str, str], board_id: int) -> list[Stream]:
    params = {"Board_Id": board_id, "_": now_ms()}
    data = fetch_json(STREAMS_URL, params, headers)

    streams: list[Stream] = []
    for item in data:
        streams.append(
            Stream(
                hsc_pgm_id=item["Hsc_Pgm_Id"],
                board_id=item["Board_Id"],
                stream=(item.get("Stream") or "").strip(),
            )
        )
    return streams


def subjects_from_programme_row(row: dict[str, Any]) -> list[str]:
    subjects: list[str] = []
    for key in ("A", "B", "C", "D", "E", "F", "G", "H"):
        value = row.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            subjects.append(text)
    return subjects


def fetch_programmes(headers: dict[str, str], hsc_pgm_id: int) -> list[dict[str, Any]]:
    params = {"Hsc_Pgm_Id": hsc_pgm_id, "_": now_ms()}
    return fetch_json(PROGRAMMES_URL, params, headers)


def scrape_to_csv(output_path: str = "board_stream_subjects.csv") -> None:
    headers = build_headers()
    rows: list[dict[str, Any]] = []

    for board in boards:
        try:
            streams = fetch_streams(headers, board.id)
        except (HTTPError, URLError, ValueError, TimeoutError) as exc:
            print(f"[WARN] Failed to fetch streams for board {board.id} ({board.name}): {exc}")
            continue

        for stream in streams:
            try:
                programmes = fetch_programmes(headers, stream.hsc_pgm_id)
            except (HTTPError, URLError, ValueError, TimeoutError) as exc:
                print(f"[WARN] Failed to fetch programme for Hsc_Pgm_Id={stream.hsc_pgm_id}: {exc}")
                continue

            for programme in programmes:
                subjects = subjects_from_programme_row(programme)
                rows.append(
                    {
                        "board_id": board.id,
                        "board_name": board.name.strip(),
                        "stream_id": stream.hsc_pgm_id,
                        "stream_name": stream.stream,
                        "index_id": programme.get("Index_Id"),
                        "subjects": " | ".join(subjects),
                    }
                )

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "board_id",
                "board_name",
                "stream_id",
                "stream_name",
                "index_id",
                "subjects",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    scrape_to_csv()
