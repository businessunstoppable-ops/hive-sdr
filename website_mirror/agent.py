import subprocess
import os
import shutil
from pathlib import Path
from typing import Dict, Optional
import hashlib

class WebsiteMirrorAgent:
    def __init__(self, base_dir: str = "mirrors"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def mirror_site(self, url: str, exclude_paths: list = None) -> Optional[Path]:
        """
        Mirror a website using httrack.
        Returns path to the mirror directory, or None if failed.
        """
        if exclude_paths is None:
            exclude_paths = ["*/blog/*", "*/wp-json/*", "*/feed/*"]
        # Create a unique directory name based on URL
        safe_name = hashlib.md5(url.encode()).hexdigest()[:8]
        target_dir = self.base_dir / safe_name
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir()
        # Build exclude rules
        exclude_rules = [f"-{path}" for path in exclude_paths]
        include_rule = "+*"
        cmd = [
            "httrack", url,
            "-O", str(target_dir),
            "-v",
            *exclude_rules,
            include_rule,
            "--mirror",
            "--robots=0",       # ignore robots.txt
            "--depth=2",        # limit depth to avoid infinite crawl
            "--max-rate=100000", # 100KB/s polite crawling
            "--ext-depth=2",
            "--disable-extensions",
            "--ignore-links"
        ]
        try:
            subprocess.run(cmd, check=True, timeout=300, capture_output=True)
            return target_dir
        except subprocess.CalledProcessError as e:
            print(f"HTTrack error: {e.stderr.decode()}")
            return None
        except Exception as e:
            print(f"Mirroring failed: {e}")
            return None

    def extract_text_from_mirror(self, mirror_path: Path) -> str:
        """Extract all text from HTML files in the mirror."""
        texts = []
        for html_file in mirror_path.rglob("*.html"):
            if html_file.stat().st_size > 1024*1024:  # skip files > 1MB
                continue
            try:
                with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Very basic text extraction (remove tags)
                    import re
                    text = re.sub(r'<[^>]+>', ' ', content)
                    text = re.sub(r'\s+', ' ', text)
                    texts.append(text)
            except:
                continue
        return " ".join(texts)[:10000]  # limit for AI
