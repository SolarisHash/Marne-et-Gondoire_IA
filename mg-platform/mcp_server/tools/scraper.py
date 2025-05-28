import subprocess
import sys
import os

def launch_scraper(spider: str, url: str = None) -> dict:
    """
    Lance un spider Scrapy par son nom. Optionnellement, un URL de départ peut être passé.
    """
    cmd = [sys.executable, '-m', 'scrapy', 'crawl', spider]
    if url:
        cmd += ['-a', f'start_url={url}']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=os.path.dirname(__file__))
    return {"pid": proc.pid}
