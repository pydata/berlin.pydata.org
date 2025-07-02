# PyData Berlin Website

This is the official website for the PyData Berlin community. It provides information about meetups, conferences, and other activities related to the PyData ecosystem in Berlin.

## Table of Contents

- [About](#about)
- [Features](#features)
- [Project Structure](#project-structure)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## About

PyData Berlin is a community of users and developers of open-source data tools, focusing on Python, Julia, and R. The website serves as a hub for information about meetups, conferences, and other events.

## Features

- Information about past and upcoming PyData Berlin conferences.
- Links to the PyData Berlin Meetup group and other related communities.
- Blog posts and updates about the community.
- Social media links for staying connected.

## Project Structure
```
├── index.html          # Main landing page
├── blog/              # Blog posts
├── conferences/       # Conference pages
├── css/              # Stylesheets
├── images/           # Images used on the website
├── js/               # JavaScript files
├── scripts/          # Python scripts for content generation
├── feed.xml          # RSS feed
├── code-of-conduct/  # Code of Conduct in multiple languages
└── cdn-cgi/          # Cloudflare scripts
```

### Scripts Directory

The `/scripts` directory contains Python utilities for generating conference content:

- **`generate_sessions.py`** - Generates individual HTML pages for conference sessions from JSON data
- **`generate_social_cards.py`** - Creates social media card images for each session with speaker photos and session details
- **`models.py`** - Pydantic models for type-safe data handling
- **`templates/`** - Jinja2 templates for HTML generation

These scripts use Python with `uv` as the package manager. To run them:

```bash
cd scripts
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install pydantic markdown jinja2 pillow requests pyyaml
python generate_sessions.py
python generate_social_cards.py
```

## Development

### Prerequisites

To set up the project locally, ensure you have the following installed:

- [Ruby](https://www.ruby-lang.org) (version >= 2.7.0)
- [Bundler](https://bundler.io) (to manage Ruby gems)
- [Jekyll](https://jekyllrb.com) (static site generator)

See [here](https://jekyllrb.com/docs/installation/#requirements) to install all 3 together. 

To run the website locally you just need to first install the dependencies
```bash
bundle install
```
and then start the sever
```bash
bundle exec jekyll serve
```


## Contributing
We welcome contributions! Please follow these steps:

* Fork the repository.
* Create a new branch for your feature or bugfix.
* Commit your changes and push the branch.
* Open a pull request.

### License
This project is licensed under the MIT License.