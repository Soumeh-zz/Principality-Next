from argparse import ArgumentError
from pathlib import Path
from hashlib import sha256
from typing import List, Set, Tuple

class Overseer():
    _magic_bytes = 131072

    def __init__(self, location: Path = Path(), patterns: List[str] = ['*.*']):
        self._watched_files = []
        self._old_hashes = {}
        # make sure location is Path type
        if isinstance(location, Path): self.location = location
        elif isinstance(location, str): self.location = Path(location)
        else: raise ArgumentError("location must be a path to a directory")

        if not isinstance(patterns, list): patterns = [patterns]

        self._patterns = patterns
        # run check once to generate hashes for comparison
        self.changes()

    def changes(self) -> Tuple[Set[Path], Set[Path], Set[Path]]:
        hashes = {}
        changed = set()

        # get every file in directory
        files = []
        for pattern in self._patterns:
            [files.append(f) for f in self.location.glob(pattern) if f.is_file()]
        for file in files:
            # hash the file and store it temporarily
            hash = sha256()
            memview = memoryview(bytearray(self._magic_bytes))
            with open(file, 'rb', buffering=0) as f:
                for n in iter(lambda: f.readinto(memview), 0): hash.update(memview[:n])
            hashes[file] = hash.hexdigest()

            # mark the file as 'changed' if the new hash differs from the last saved hash
            if self._old_hashes.get(file) and self._old_hashes.get(file) != hashes[file]:
                changed.add(file)

        # add and subtract old and new hashes to mark files as 'added' or 'removed'
        added = set(hashes.keys()) - set(self._old_hashes.keys())
        removed = set(self._old_hashes.keys()) - set(hashes.keys())
        for r in removed:
            del self._old_hashes[r]

        # finalize
        self._old_hashes = hashes
        return (changed, added, removed)