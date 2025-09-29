import requests
import re
import hashlib
import os

useragent = "books-downloader-python101/1.0"

print("Books Downloader - short version")
print("1 Kotobati  2 Gutenberg  3 OpenLibrary  4 direct_url  0 quit")

while True:
    c = input("choice: ").strip()
    if c == "0":
        print("bye")
        break
    if c == "1":
        q = input("query: ").strip()
        if not q:
            print("empty")
            continue
        r = requests.get("https://www.kotobati.com/search/result", params={"s": q}, headers={"user-agent": useragent}, timeout=20)
        html = r.text
        m = re.findall(r'href="/book/(\d+)[^>]*>\s*([^<]+)', html)
        if not m:
            print("no results")
            continue
        id0 = m[0][0]
        token = None
        try:
            html2 = requests.get(f"https://www.kotobati.com/book/{id0}", headers={"user-agent": useragent}, timeout=20).text
            token = html2.split(' <a href="/book/reading/')[1][:36]
        except Exception:
            pass
        if not token:
            print("no download token")
            continue
        url = f"https://www.kotobati.com/book/download/{token}"
        fname = "book.pdf"
        try:
            with requests.get(url, stream=True, timeout=180) as rr:
                rr.raise_for_status()
                with open(fname, "wb") as f:
                    for ch in rr.iter_content(8192):
                        if ch:
                            f.write(ch)
            print("saved", os.path.abspath(fname))
        except Exception as e:
            print("download err", e)
    elif c == "2":
        q = input("query: ").strip()
        if not q:
            print("empty")
            continue
        try:
            html = requests.get("https://www.gutenberg.org/ebooks/search/", params={"query": q}, headers={"user-agent": useragent}, timeout=20).text
            m = re.search(r'href="(/ebooks/\d+)"', html)
            if not m:
                print("no results")
                continue
            page = "https://www.gutenberg.org" + m.group(1)
            pagehtml = requests.get(page, headers={"user-agent": useragent}, timeout=20).text
            m2 = re.search(r'href="(https://www.gutenberg.org/files/\d+/\d+-0.txt)"', pagehtml)
            if not m2:
                m2 = re.search(r'href="(https://www.gutenberg.org/files/\d+/\d+\.pdf)"', pagehtml)
            if not m2:
                print("no download link")
                continue
            url = m2.group(1)
            fname = url.split('/')[-1]
            with requests.get(url, stream=True, timeout=60) as rr:
                rr.raise_for_status()
                with open(fname, 'wb') as f:
                    for ch in rr.iter_content(8192):
                        if ch:
                            f.write(ch)
            print("saved", os.path.abspath(fname))
        except Exception as e:
            print("err", e)
    elif c == "3":
        q = input("query: ").strip()
        if not q:
            print("empty")
            continue
        try:
            j = requests.get("https://openlibrary.org/search.json", params={"q": q}, headers={"user-agent": useragent}, timeout=20).json()
            docs = j.get('docs', [])
            if not docs:
                print('no results')
                continue
            olid = docs[0].get('edition_key', [None])[0] or docs[0].get('key', '').split('/')[-1]
            if not olid:
                print('no id')
                continue
            try:
                d = requests.get(f"https://openlibrary.org/books/{olid}.json", headers={"user-agent": useragent}, timeout=20).json()
                oca = d.get('ocaid')
                if oca:
                    url = f"https://archive.org/download/{oca}/{oca}.pdf"
                    fname = 'book_open.pdf'
                    with requests.get(url, stream=True, timeout=60) as rr:
                        rr.raise_for_status()
                        with open(fname, 'wb') as f:
                            for ch in rr.iter_content(8192):
                                if ch:
                                    f.write(ch)
                    print('saved', os.path.abspath(fname))
                    continue
            except Exception:
                pass
            print('could not get file')
        except Exception as e:
            print('err', e)
    elif c == "4":
        url = input('url: ').strip()
        if not url:
            print('empty')
            continue
        fname = url.split('/')[-1] or 'download'
        try:
            with requests.get(url, stream=True, timeout=60) as rr:
                rr.raise_for_status()
                with open(fname, 'wb') as f:
                    for ch in rr.iter_content(8192):
                        if ch:
                            f.write(ch)
            print('saved', os.path.abspath(fname))
        except Exception as e:
            print('err', e)
    else:
        print('unknown')
