# Vue + FastAPI Template

This template should help get you started developing with a static Vue 3 web application built with Vite and styled with Vuetify.

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Type Support for `.vue` Imports in TS

TypeScript cannot handle type information for `.vue` imports by default, so we replace the `tsc` CLI with `vue-tsc` for type checking. In editors, we need [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) to make the TypeScript language service aware of `.vue` types.

## Customize configuration

See [Vite Configuration Reference](https://vitejs.dev/config/).

## Project Setup

### Step 1 - Create new Repo

Create a new project in Github. You can either reference this template repo, or create an empty repository and clone this template repo. To clone, follow this process:

```bash
git clone git@github.com:JoelYoung01/VueStaticSiteTemplate.git <project_name_here>
cd <project_name_here>
git init
git add .
git commit -m "Initial Commit"
git remote add origin <new_repo_url>
git push -u origin main
```

### Step 2 - Setup Environment

Copy `.envtemplate` to a new file, `.env`, and fill out applicable values

Setup the backend by creating a venv.

```bash
# Add venv
py -m venv venv
```

When using VSCode, you should have the option to set this venv as your default python interpreter. If the option did not pop up, you can set this opening the cmd palette `Ctrl` + `Shift` + `P` and typing `Python: Select Interpreter` or something similar.

> When setting your venv python as your default interpreter, you will have to reload VSCode before your terminals switch to using that python instance.

Once your venv is active, `echo $env:VIRTUAL_ENV` should return your venv's path.

### Step 3 - Install Dependencies

Install dependencies

```bash
# Install Vite Deps
pnpm i

# Activate venv (only if not already active)
./venv/Scripts/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Run / Build / Deploy

#### Compile and Hot-Reload for Development

```bash
# Run Vite Dev Server
pnpm dev

# Run FastAPI Dev Server
fastapi dev api/main.py
```

#### Type-Check, Compile and Minify for Production

```bash
pnpm build
```

#### Lint with [ESLint](https://eslint.org/)

```bash
pnpm lint
```

## S3 Deployment

This repo comes with a GitHub Action that will deploy the site to an S3 bucket. To set this up, you'll need to add the following environment variables and secrets to your GitHub repository:

Environment Variables

- `APP_NAME` _lower-snake-case_
- `APP_TITLE` _Display Name_

Secrets:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `S3_BUCKET`

The actions are set up to deploy to 3 environments; dev, stage, and prod. It is recommended to set up S3_BUCKET environment secret per environment.
