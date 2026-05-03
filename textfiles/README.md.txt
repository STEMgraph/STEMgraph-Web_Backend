# STEMgraph-API

A FastAPI solution for [STEMgraph](https://github.com/STEMgraph).

## Repository structure

/doc: Documentation  
/bin: Scripts and Binaries

## Overview

![planned use-cases for STEMgraph-API](/doc/useCase.svg "STEMgraph-API Use-Cases")

## Setup

### ... locally for development and testing purposes

- Clone this repository to your local workstation.
- Copy `env-template` as `.env`.
- In the `.env` file, remove all lines after the first blank line.
- Create a GitHub **Personal access token**. A **Fine-grained token** with **Read-only access to public repositories** is recommended.
- In the `.env` file, enter the access token as the value for the `GITHUB_PAT`environment variable.
- Run `docker compose up --build`.

The API is now up and running at `http://localhost:8000/docs`.
