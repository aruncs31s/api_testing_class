import csv
import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

CF_CLEARANCE = os.getenv("CF_CLEARANCE", "")
ASPNET_SESSIONID = os.getenv("ASPNET_SESSIONID", "")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("pg_scraper")


BASE_URL = "https://services.cmscollege.ac.in/PGAdmission/PGAdmission"
PROGRAMMES_URL = f"{BASE_URL}/BindUGProgramme"
COMBINATIONS_URL = f"{BASE_URL}/BindCourseCombinations"
COURSE_DETAILS_URL = f"{BASE_URL}/getCourseDetails"


BASE_HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json; charset=utf-8",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://services.cmscollege.ac.in/PGAdmission/PGAdmission/Application_New_PG",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:149.0) Gecko/20100101 Firefox/149.0",
}


universities = [
    (1, "MG UNIVERSITY"),
    (2, "CALICUT UNIVERSITY"),
    (3, "KANNUR UNIVERSITY"),
    (4, "KERALA UNIVERSITY"),
    (5, "AMRITA VISHWA VIDYAPEETHAM"),
    (6, "MANGLORE UNIVERSITY"),
    (7, "Bharathiar University"),
    (8, "BANGALORE UNIVERSITY"),
    (9, "ANDHRA UNIVERSITY"),
    (10, "MADRAS UNIVERSITY"),
    (11, "Christ (Deemed to be University), Bengaluru"),
    (12, "UNIVERSITY OF DELHI"),
    (13, "Ranchi University"),
    (14, "SRM University"),
    (15, "IGNOU-"),
    (16, "KOTTA UNIVERSITY"),
    (17, "MADRAS CHRISTIAN COLLEGE"),
    (18, "MANONMANIAM SUNDARANAR UNIVERSITY"),
    (19, "MADURAI KAMARAJ UNIVERSITY"),
    (21, "MYSORE UNIVERSITY"),
    (22, "MANIPAL ACADEMY OF HIGHER EDUCATION"),
    (23, "GURU GOBIND SINGH INDRAPRASTHA UNIVERSITY, DELHI"),
    (24, "Kerala Technological University"),
    (25, "Jamal Mohamed College"),
    (27, "LOYOLA COLLEGE, CHENNAI"),
    (28, "BHARATHIDASAN UNIVERSITY"),
    (29, "The maharaja sayajiroa university of baroda"),
    (30, "THE ENGLISH AND FOREIGN LANGUAGES UNIVERSITY"),
    (31, "PANJAB UNIVERSITY,CHANDIGARH"),
    (32, "University of Mumbai"),
    (33, "RASHTRASANT TUKADOJI MAHARAJ NAGPUR UNIVERSITY"),
    (34, "Maharshi Dayanand University"),
    (35, "Gujarat University"),
    (36, "Bengaluru city University"),
    (37, "SARDAR PATEL UNIVERSITY"),
    (38, "Lucknow university"),
    (39, "Pondicherry University"),
    (40, "Azim Premji University"),
    (41, "Garden City University"),
    (42, "Amity University Maharashtra"),
    (43, "Rabindranath Tagore University"),
    (44, "CHINMAYA VISHWAVIDYAPEETH, Deemed to be University"),
    (45, "Jain Deemed-to-be University"),
    (46, "Bangalore North University"),
    (47, "Parul University"),
    (48, "THE UNIVERSITY OF BURDWAN"),
    (49, "Yenepoya deemed to be university"),
    (50, "ANNA UNIVERSITY"),
    (51, "Savitribai Phule Pune University"),
    (52, "Maulana Abul Kalam Azad University of Technology, West Bengal"),
    (53, "St. Joseph's University BENGALURU"),
]


@dataclass
class Programme:
    ug_pgm_id: int
    uni_id: int
    programme: str
    model: str | None


@dataclass
class CourseCombination:
    comb_id: int
    ug_pgm_id: int
    name: str
    grade_scale: str
    university: str
    sub_a: str | None
    sub_b: str | None
    sub_c: str | None
    sub_d: str | None
    sub_e: str | None
    sub_f: str | None
    sub_g: str | None
    sub_h: str | None
    sub_i: str | None


def build_headers() -> dict[str, str]:
    logger.info("Step: Build request headers")
    headers = dict(BASE_HEADERS)

    cf_clearance = CF_CLEARANCE.strip()
    aspnet_session = ASPNET_SESSIONID.strip()

    cookies: list[str] = []
    if cf_clearance:
        cookies.append(f"cf_clearance={cf_clearance}")
    if aspnet_session:
        cookies.append(f"ASP.NET_SessionId={aspnet_session}")
    if cookies:
        headers["cookie"] = "; ".join(cookies)
        logger.info(
            "Step: Cookie header prepared (cf_clearance=%s, ASP.NET_SessionId=%s)",
            "set" if bool(cf_clearance) else "missing",
            "set" if bool(aspnet_session) else "missing",
        )
    else:
        logger.warning("Step: No cookies set; Cloudflare protected endpoints may fail")

    return headers


def now_ms() -> int:
    return int(time.time() * 1000)


def fetch_json(url: str, params: dict[str, Any], headers: dict[str, str]) -> Any:
    endpoint = url.rsplit("/", 1)[-1]
    logger.info("Step: HTTP GET %s params=%s", endpoint, params)
    started = time.perf_counter()
    query = urlencode(params, safe="+")
    request = Request(f"{url}?{query}", headers=headers, method="GET")
    with urlopen(request, timeout=30) as response:
        data = response.read().decode("utf-8")
    elapsed = time.perf_counter() - started
    logger.info(
        "Step: HTTP response %s bytes=%d elapsed=%.2fs",
        endpoint,
        len(data),
        elapsed,
    )
    return json.loads(data)


def fetch_programmes(
    headers: dict[str, str], uni_id: int, university: str
) -> list[Programme]:
    logger.info(
        "Step: Fetch programmes for university='%s' (uni_id=%s)", university, uni_id
    )
    params = {"University": university.replace(" ", "+"), "_": now_ms()}
    data = fetch_json(PROGRAMMES_URL, params, headers)

    if not isinstance(data, list):
        logger.warning(
            "Step: Unexpected programmes payload type for '%s': %s",
            university,
            type(data).__name__,
        )
        return []

    programmes: list[Programme] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        ug_pgm_id = item.get("UG_Pgm_Id")
        api_uni_id = item.get("Uni_Id")
        if not isinstance(ug_pgm_id, int) or not isinstance(api_uni_id, int):
            continue

        programme_name = str(item.get("Programme", "")).strip()
        if not programme_name:
            continue

        programmes.append(
            Programme(
                ug_pgm_id=ug_pgm_id,
                uni_id=api_uni_id,
                programme=programme_name,
                model=item.get("Model"),
            )
        )
    logger.info(
        "Step: Programmes fetched for university='%s' count=%d",
        university,
        len(programmes),
    )
    return programmes


def get_available_grade_scales() -> list[str]:
    configured = os.getenv("GRADE_SCALES", "").strip()
    if configured:
        scales: list[str] = []
        seen: set[str] = set()
        for item in configured.split(","):
            value = item.strip()
            if not value:
                continue
            normalized = value.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            scales.append(value)
        if scales:
            logger.info("Step: Grade scales from GRADE_SCALES=%s", scales)
            return scales

        # Common values observed from the live portal's grade scale dropdown.
        default_scales = ["4", "6", "10", "Mark"]
        logger.info("Step: Grade scales default=%s", default_scales)
        return default_scales


def fetch_course_combinations(
    headers: dict[str, str], ug_pgm_id: int, grade_scale: str, university: str
) -> list[dict[str, Any]]:
    logger.info(
        "Step: Fetch combinations ug_pgm_id=%s grade_scale=%s university='%s'",
        ug_pgm_id,
        grade_scale,
        university,
    )
    params = {
        "UG_Pgm_Id": ug_pgm_id,
        "Grade_Scale": grade_scale,
        "University": university.replace(" ", "+"),
        "_": now_ms(),
    }
    try:
        data = fetch_json(COMBINATIONS_URL, params, headers)
        if isinstance(data, list):
            normalized_rows = [row for row in data if isinstance(row, dict)]
            logger.info(
                "Step: Combinations received ug_pgm_id=%s grade_scale=%s count=%d",
                ug_pgm_id,
                grade_scale,
                len(normalized_rows),
            )
            return normalized_rows

        # API sometimes returns a single object instead of a list.
        if isinstance(data, dict):
            logger.info(
                "Step: Single combination object received ug_pgm_id=%s grade_scale=%s",
                ug_pgm_id,
                grade_scale,
            )
            return [data]

        logger.warning(
            "Step: Unexpected combinations payload type ug_pgm_id=%s grade_scale=%s type=%s",
            ug_pgm_id,
            grade_scale,
            type(data).__name__,
        )
        return []
    except (HTTPError, URLError, ValueError, TimeoutError) as exc:
        logger.warning(
            "Step: Combinations request failed ug_pgm_id=%s grade_scale=%s university='%s' error=%s",
            ug_pgm_id,
            grade_scale,
            university,
            exc,
        )
        return []


def fetch_course_details(
    headers: dict[str, str], comb_id: int
) -> dict[str, Any] | None:
    logger.info("Step: Fetch course details comb_id=%s", comb_id)
    params = {"Comb_Id": comb_id, "_": now_ms()}
    try:
        details = fetch_json(COURSE_DETAILS_URL, params, headers)
        logger.info(
            "Step: Course details fetched comb_id=%s type=%s",
            comb_id,
            type(details).__name__,
        )
        return details
    except (HTTPError, URLError, ValueError, TimeoutError) as exc:
        logger.warning(
            "Step: Course details request failed comb_id=%s error=%s", comb_id, exc
        )
        return None


def extract_subjects_from_combination(row: dict[str, Any]) -> list[str]:
    subjects: list[str] = []
    for key in (
        "Sub_A",
        "Sub_B",
        "Sub_C",
        "Sub_D",
        "Sub_E",
        "Sub_F",
        "Sub_G",
        "Sub_H",
        "Sub_I",
    ):
        value = row.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text and text.lower() != "null":
            subjects.append(text)
    logger.debug("Step: Extracted subjects count=%d", len(subjects))
    return subjects


def get_grade_scale_from_combination(comb: dict[str, Any]) -> str:
    grade_scale = comb.get("Grade_Scale")
    if grade_scale:
        return str(grade_scale)
    return ""


def scrape():
    logger.info("Step: Scrape started")
    headers = build_headers()
    grade_scales = get_available_grade_scales()
    logger.info("Step: Total universities configured=%d", len(universities))

    unique_universities: dict[str, int] = {}
    unique_programs: dict[tuple[str, int], int] = {}  # Key is (prog_name, uni_id)

    hierarchy_rows: list[dict[str, Any]] = []
    university_rows: list[dict[str, Any]] = []
    program_rows: list[dict[str, Any]] = []
    course_rows: list[dict[str, Any]] = []
    seen_hierarchy: set[tuple[str, str, str, str]] = set()
    seen_courses: set[tuple[str, int]] = set()

    uni_counter = 1
    prog_counter = 1

    for uni_id, university in universities:
        logger.info("Step: University start uni_id=%s name='%s'", uni_id, university)
        try:
            programmes = fetch_programmes(headers, uni_id, university)
        except (HTTPError, URLError, ValueError, TimeoutError) as exc:
            logger.warning(
                "Step: Failed to fetch programmes for university='%s' error=%s",
                university,
                exc,
            )
            continue

        if university not in unique_universities:
            unique_universities[university] = uni_counter
            university_rows.append({"id": uni_counter, "name": university})
            logger.info(
                "Step: University mapped csv_id=%d name='%s'", uni_counter, university
            )
            uni_counter += 1

        uni_counter_id = unique_universities[university]
        logger.info(
            "Step: University programmes ready university='%s' count=%d",
            university,
            len(programmes),
        )

        for programme in programmes:
            prog_name = programme.programme
            prog_key = (prog_name, uni_counter_id)  # Make key unique per university

            if prog_key in unique_programs:
                prog_id = unique_programs[prog_key]
            else:
                unique_programs[prog_key] = prog_counter
                program_rows.append(
                    {
                        "id": prog_counter,
                        "name": prog_name,
                        "university_id": uni_counter_id,
                    }
                )
                prog_id = prog_counter
                logger.info(
                    "Step: Program mapped program_id=%d university_id=%d name='%s'",
                    prog_id,
                    uni_counter_id,
                    prog_name,
                )
                prog_counter += 1

            for grade_scale in grade_scales:
                combinations = fetch_course_combinations(
                    headers, programme.ug_pgm_id, grade_scale, university
                )

                if not combinations:
                    logger.info(
                        "Step: No combinations ug_pgm_id=%s grade_scale=%s university='%s'",
                        programme.ug_pgm_id,
                        grade_scale,
                        university,
                    )

                for comb in combinations:
                    comb_id = comb.get("Comb_Id", 0)
                    if not comb_id or comb_id == 0:
                        logger.debug(
                            "Step: Skip combination without valid Comb_Id for ug_pgm_id=%s grade_scale=%s",
                            programme.ug_pgm_id,
                            grade_scale,
                        )
                        continue

                    logger.info(
                        "Step: Process combination comb_id=%s program_id=%s grade_scale_input=%s",
                        comb_id,
                        prog_id,
                        grade_scale,
                    )

                    grade_scale_from_api = get_grade_scale_from_combination(comb)
                    if not grade_scale_from_api:
                        grade_scale_from_api = grade_scale

                    subjects = extract_subjects_from_combination(comb)
                    if not subjects:
                        details = fetch_course_details(headers, comb_id)
                        if isinstance(details, dict):
                            subjects = extract_subjects_from_combination(details)
                            if not grade_scale_from_api:
                                grade_scale_from_api = (
                                    get_grade_scale_from_combination(details)
                                    or grade_scale
                                )
                            logger.info(
                                "Step: Subject fallback from details comb_id=%s subjects_count=%d",
                                comb_id,
                                len(subjects),
                            )

                    subjects_str = " | ".join(subjects) if subjects else ""

                    hierarchy_key = (
                        university,
                        prog_name,
                        grade_scale_from_api,
                        subjects_str,
                    )
                    if hierarchy_key not in seen_hierarchy:
                        seen_hierarchy.add(hierarchy_key)
                        hierarchy_rows.append(
                            {
                                "university": university,
                                "programme": prog_name,
                                "grade_point_scale": grade_scale_from_api,
                                "course_studied": subjects_str,
                            }
                        )
                        logger.info(
                            "Step: Added hierarchy row comb_id=%s grade_scale=%s",
                            comb_id,
                            grade_scale_from_api,
                        )

                    course_name = comb.get("Course", prog_name)
                    if not course_name:
                        course_name = prog_name
                    course_name = str(course_name).strip()
                    if not course_name:
                        course_name = prog_name

                    course_key = (course_name, prog_id)
                    if course_key not in seen_courses:
                        seen_courses.add(course_key)
                        course_rows.append(
                            {
                                "course_name": course_name,
                                "programme_id": prog_id,
                            }
                        )
                        logger.info(
                            "Step: Added course row program_id=%s course_name='%s'",
                            prog_id,
                            course_name,
                        )

    logger.info("Step: Writing hierarchy.csv rows=%d", len(hierarchy_rows))
    with open("hierarchy.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "university",
                "programme",
                "grade_point_scale",
                "course_studied",
            ],
        )
        writer.writeheader()
        writer.writerows(hierarchy_rows)

    logger.info("Step: Writing universities.csv rows=%d", len(university_rows))
    with open("universities.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name"])
        writer.writeheader()
        writer.writerows(university_rows)

    logger.info("Step: Writing programs.csv rows=%d", len(program_rows))
    with open("programs.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "university_id"])
        writer.writeheader()
        writer.writerows(program_rows)

    logger.info("Step: Writing courses.csv rows=%d", len(course_rows))
    with open("courses.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["course_name", "programme_id"])
        writer.writeheader()
        writer.writerows(course_rows)

    logger.info("Step: Scrape completed")

    print(f"Hierarchy: {len(hierarchy_rows)} rows")
    print(f"Universities: {len(university_rows)} rows")
    print(f"Programs: {len(program_rows)} rows")
    print(f"Courses: {len(course_rows)} rows")


if __name__ == "__main__":
    scrape()
