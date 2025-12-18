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
- Create a folder called `secrets` in your local working directory.
- Create a GitHub **Personal access token**. A **Fine-grained token** with **Read-only access to public repositories** is recommended.
- Store the token as plain text in `secrets/github.pat`.
- Run `docker compose up --build`.

The API is now up and running at `http://localhost:8080/docs`.
