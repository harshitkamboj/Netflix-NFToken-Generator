# Netflix NFToken Generator

Simple Python script that shows how a Netflix `NFToken` link is generated from a valid Netflix session cookie.

The script reads the cookie from `input.txt`, sends the required request to Netflix, and prints the `nftoken` login link in the console.

It also includes comments in the code so the request flow is easier to understand for anyone reading or modifying it.

## Discord

- Discord server: https://discord.gg/DYJFE9nu5X

## Features

- Simple local script with no extra UI
- Reads cookie from `input.txt`
- Auto-creates `input.txt` if it is missing
- Supports raw cookie string, Netscape cookie format, and JSON cookie input
- Prints the full Netflix `nftoken` link in console
- Includes inline comments explaining each step of the flow

## Requirements

Install the required module:

```bash
pip install requests
```

## Quick Start

1. Clone the repo:

```bash
git clone https://github.com/harshitkamboj/Netflix-NFToken-Generator.git
cd Netflix-NFToken-Generator
```

2. Install requirements:

```bash
pip install requests
```

3. Run the script once:

```bash
python nf-token-generator.py
```

4. If `input.txt` does not exist, the script will create it automatically
5. Paste your Netflix cookie into `input.txt`
6. Run again:

```bash
python nf-token-generator.py
```

7. The console will print:

```text
https://www.netflix.com/?nftoken=...
```

## Input Example

### Raw Cookie String

```text
NetflixId=xxx; SecureNetflixId=xxx; nfvdid=xxx
```

### Netscape Cookie Format

```text
.netflix.com	TRUE	/	TRUE	1234567890	NetflixId	xxx
.netflix.com	TRUE	/	TRUE	1234567890	SecureNetflixId	xxx
.netflix.com	TRUE	/	TRUE	1234567890	nfvdid	xxx
```

### JSON Format

```json
{
  "NetflixId": "xxx",
  "SecureNetflixId": "xxx",
  "nfvdid": "xxx"
}
```

## How It Works

1. The script reads cookie data from `input.txt`
2. It extracts the required Netflix session cookies
3. It builds the `Cookie` header
4. It sends a request to Netflix's `createAutoLoginToken` GraphQL operation
5. It reads the returned token from `data.createAutoLoginToken`
6. It prints the final Netflix login link using `?nftoken=...`

## Files

```text
nf-token-generator.py   # main script
input.txt               # cookie input file
README.md               # project guide
```

## Notes

- Use only cookies/accounts you are authorized to test
- A valid Netflix session cookie is required
- If the cookie is invalid or expired, Netflix will return an error instead of an `NFToken`

## Contact

- GitHub: https://github.com/harshitkamboj
- Repository: https://github.com/harshitkamboj/Netflix-NFToken-Generator
- Website: https://harshitkamboj.in
- Discord username: `illuminatis69`
- Discord server: https://discord.gg/DYJFE9nu5X

## Disclaimer

Educational use only. Use only on accounts and cookies you are authorized to test.
