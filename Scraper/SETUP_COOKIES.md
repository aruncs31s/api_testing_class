# Setup Instructions for pg_scraper.py

## Setting Up Cookies

The scraper requires two cookies from the Cloudflare-protected website. Set them as environment variables before running the script:

### Method 1: Using .env file (Recommended)
Create a `.env` file in the project root:

```bash
CF_CLEARANCE=he_HJ15Ictg72GSw51Ln2vUBFHrHcFuT4iV2kSXXyP0-1776425764-1.2.1.1-aNx4zzCD6wV2Tywg7BtgoT5uZ1tFrkkGjyqgNw4MXDIp5YYHVTY.bMoN57CWCbGDEJYeJC0WFASUjDLbGq7CU2yS2d.EDASHpjV5c4PtvqHRbuVdjcO3MTAb_Y_SdYgmmXu0g4U1YRiyFf4TtFfEzTwVgCB7splfq2VakGwl6OutPFstzIEE0SUnzJOCEHMWHf15teTapxelpK_W.l40_fLCY_IJiRERZXah01suDv3ixt_3kdNEP2JLzdve0A34wnNIxBNCMFZxLZQoE6jAaSBnlQZWN9VFjFha9kFJNY3E8jm1FNBZdzWrqliNzNS4glMbWh8W9x3me7P_5el1gg
ASPNET_SESSIONID=lxhkwgzsjrbtr3h1y545bkhv
```

Then update the `.env` loading in the script to use `python-dotenv`.

### Method 2: Inline Export
```bash
export CF_CLEARANCE="he_HJ15Ictg72GSw51Ln2vUBFHrHcFuT4iV2kSXXyP0-1776425764-1.2.1.1-aNx4zzCD6wV2Tywg7BtgoT5uZ1tFrkkGjyqgNw4MXDIp5YYHVTY.bMoN57CWCbGDEJYeJC0WFASUjDLbGq7CU2yS2d.EDASHpjV5c4PtvqHRbuVdjcO3MTAb_Y_SdYgmmXu0g4U1YRiyFf4TtFfEzTwVgCB7splfq2VakGwl6OutPFstzIEE0SUnzJOCEHMWHf15teTapxelpK_W.l40_fLCY_IJiRERZXah01suDv3ixt_3kdNEP2JLzdve0A34wnNIxBNCMFZxLZQoE6jAaSBnlQZWN9VFjFha9kFJNY3E8jm1FNBZdzWrqliNzNS4glMbWh8W9x3me7P_5el1gg"
export ASPNET_SESSIONID="lxhkwgzsjrbtr3h1y545bkhv"
python pg_scraper.py
```

## Output Files

The script generates 4 CSV files:

1. **hierarchy.csv** - University | Programme | Grade Point Scale | Course Studied
2. **universities.csv** - ID | University Name (DISTINCT)
3. **programs.csv** - ID | Programme Name | University ID
4. **courses.csv** - Course Name | Programme ID

## Important Notes

- **CF_CLEARANCE** cookie may expire frequently - you'll need to update it from the browser's DevTools
- Extract cookies from Network tab → BindUGProgramme request → Cookies
- The scraper handles rate limiting with 30-second timeouts
- Empty responses (no combinations) are normal and handled gracefully
