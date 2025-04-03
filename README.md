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
 ├── index.html # Main landing page 
 ├── blog/ # Blog posts
 ├── conferences/ # Conference pages 
 ├── css/ # Stylesheets 
 ├── images/ # Images used on the website 
 ├── js/ # JavaScript files 
 ├── feed.xml # RSS feed 
 ├── code-of-conduct/ # Code of Conduct in multiple languages 
 └── cdn-cgi/ # Cloudflare scripts

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