# PhotosCollector

[![License: MIT](https://img.shields.io/badge/license-GPLv3-blue&style=flat)](https://opensource.org/licenses/MIT)

[![Last commit](https://img.shields.io/github/last-commit/sbancal/PhotosCollector.svg?style=flat&logo=github)](https://github.com/sbancal/PhotosCollector/commits)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/sbancal/PhotosCollector?style=flat&logo=github)](https://github.com/sbancal/PhotosCollector/commits)
[![Github Stars](https://img.shields.io/github/stars/sbancal/PhotosCollector?style=flat&logo=github)](https://github.com/sbancal/PhotosCollector/stargazers)
[![Github Forks](https://img.shields.io/github/forks/sbancal/PhotosCollector?style=flat&logo=github)](https://github.com/sbancal/PhotosCollector/network/members)
[![Github Watchers](https://img.shields.io/github/watchers/sbancal/PhotosCollector?style=flat&logo=github)](https://github.com/sbancal/PhotosCollector)
[![GitHub contributors](https://img.shields.io/github/contributors/sbancal/PhotosCollector?style=flat&logo=github)](https://github.com/sbancal/PhotosCollector/graphs/contributors)

A simple tool to automate photos collection from several sources into a single destination.

- Detects duplicates
- Organizes photos by date
- Renames photos with a unique name
  - `YYYY-MM-DD_HH-MM-SS.extension` for those with a date in their EXIF
  - `0000000.extension` (sequential number) for the others

# Installation

```bash
make install
```

# Usage

```bash
poetry run ./collectphotos.py -s ~/source1 ~/source2 -d ~/destination
```

# License

This project is licensed under the terms of the [MIT license](/LICENSE).
