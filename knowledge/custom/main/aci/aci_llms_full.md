# ACI (AI Code Interpreter) - Complete Documentation

**Source:** https://www.aci.dev/docs/llms-full.txt  
**Category:** ACI Tool Interface  
**Crawled:** 2025-06-09T19:20:51.308874  

---

# OAuth2 White-label
Source: https://aci.dev/docs/advanced/oauth2-whitelabel

How to white-label the OAuth2 flow for OAuth2-based apps

You can use your own **OAuth2 Client** instead of ACI.dev's default OAuth2 client when configuring `App` with `oauth2` authentication method.

<Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/oauth2-whitelabel-toggle.png" alt="Custom OAuth2 App Configuration Illustration" />
</Frame>

## Why provide your own OAuth2 client?

**Branding & White-labeling**

* Your name and logo appear on OAuth2 consent screens
* Delivers a white-labelled experience, free from third-party branding
* Builds user trust by presenting a consistent, recognizable interface

**Control & Security**

* Full control over OAuth2 settings (token lifetimes, scopes, redirect URIs, etc.)
* Easier integration with your own internal systems or policies

## How to configure your own OAuth2 client?

<Steps>
 <Step title="Create an OAuth2 client in the App provider's dev portal">
 For example, if you are configuring `GMAIL`, you need to create an OAuth2 client in the google cloud console.
 </Step>

 <Step title="Configure OAuth2 scopes in your OAuth2 client">
 Most OAuth2 app providers have fine-grained control over the scopes of the OAuth2 client. You need to configure the scopes for your OAuth2 client to match the scopes the app requires.

 <Warning>
 Please make sure you have configured `All` listed scopes on the popup window.
 </Warning>

 <Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/oauth2-whitelabel-scopes.png" />
 </Frame>
 </Step>

 <Step title="Set redirect URL in your OAuth2 client">
 The redirect URL is the URL that the oauth2 provider will redirect to after the user has authenticated.
 You have two options for setting the redirect URL:

 * (Simple) Use ACI.dev's default redirect URL
 * (Advanced) Use your own redirect URL, e.g., `https://your-domain.com/oauth2/callback`

 <Note>
 **When will you need to use the second option?**

 Some OAuth2 providers—such as Google—display the domain of the redirect URL during the authorization flow. This means that if your users are redirected to our platform’s domain, it will appear in the authorization screen, potentially exposing our brand instead of yours.

 To preserve your brand identity throughout the OAuth2 flow, you need to use you own redirect URL.
 Then, configure your backend to forward requests from your own redirect URL to ACI.dev's redirect endpoint. This way, the domain shown to the end user during authorization remains your own, maintaining a seamless white-labeled experience
 </Note>

 <Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/oauth2-whitelabel-redirect-url.png" />
 </Frame>

 <Warning>
 If you use your own redirect URL, make sure you have configured your backend to forward requests from your own redirect URL to ACI.dev's redirect endpoint so ACI.dev can finish the account linking process.
 </Warning>
 </Step>

 <Step title="Copy the OAuth2 client ID and secret">
 Copy & paste the OAuth2 `client id` and `client secret` from the OAuth2 client you created.

 <Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/oauth2-whitelabel-client-id-secret.png" />
 </Frame>
 </Step>
</Steps>

<Warning>
 **You cannot change the OAuth2 client after setup.**

 If you need to update it, you must **delete and reconfigure the app** from scratch.
</Warning>

# Overview
Source: https://aci.dev/docs/agent-examples/overview

See examples of AI agents built with ACI.dev

Please see the [Agent Examples <Icon icon="up-right-from-square" />](https://github.com/aipotheosis-labs/aci-agents) repo for examples of AI agents built with ACI.dev.

# Introduction
Source: https://aci.dev/docs/agent-playground/introduction

A playground to test you ACI.dev setup

<Warning>Agent Playground is a beta feature and not recommended for production use. Expect limited stability and possible changes.</Warning>

The Agent Playground provides a no-code environment where you can test AI agents performing tasks on behalf of users. This playground allows you to test how your agent will interact with various functions and applications without writing any code.

<Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/agent-playground-snapshot.webp" alt="Agent Playground" />
</Frame>

<Warning>The agent playground operates in a stateless manner and we don't store any conversation history on the server side. Conversation history is cleared when you close the tab.</Warning>

### Using the Playground

<Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/agent-playground-concept.png" alt="Agent Playground Concept" />
</Frame>

To use the Agent Playground, you need to configure the following settings:

1. Select an existing Agent from the dropdown menu. (You can create and manage agents in the `Agents` tab)

2. Select `Apps` you want to test. (Only apps that have been enabled for your selected agent will appear in this list)

3. Select a Linked Account Owner ID. (The agent will only have access to linked accounts from this owner)

4. Select `Functions` you want to test. (Only functions of selected apps will show up in dropdown) This allows you to control exactly which tool are available during testing.

#### Play with the agent

Once you've configured your settings, you can interact with the agent through a chat interface:
e.g., "star github repo aipotheosis-labs/aci", "what is the top news today?"

# Create App Configuration
Source: https://aci.dev/docs/api-reference/app-configurations/create-app-configuration

post /v1/app-configurations
Create an app configuration for a project

# Delete App Configuration
Source: https://aci.dev/docs/api-reference/app-configurations/delete-app-configuration

delete /v1/app-configurations/{app_name}
Delete an app configuration by app name
Warning: This will delete the app configuration from the project,
associated linked accounts, and then the app configuration record itself.

# Get App Configuration
Source: https://aci.dev/docs/api-reference/app-configurations/get-app-configuration

get /v1/app-configurations/{app_name}
Get an app configuration by app name

# List App Configurations
Source: https://aci.dev/docs/api-reference/app-configurations/list-app-configurations

get /v1/app-configurations
List all app configurations for a project, with optionally filters

# Update App Configuration
Source: https://aci.dev/docs/api-reference/app-configurations/update-app-configuration

patch /v1/app-configurations/{app_name}
Update an app configuration by app name.
If a field is not included in the request body, it will not be changed.

# Get App Details
Source: https://aci.dev/docs/api-reference/apps/get-app-details

get /v1/apps/{app_name}
Returns an application (name, description, and functions).

# Search Apps
Source: https://aci.dev/docs/api-reference/apps/search-apps

get /v1/apps/
Search for Apps.
Intented to be used by agents to search for apps based on natural language intent.

# Execute
Source: https://aci.dev/docs/api-reference/functions/execute

post /v1/functions/{function_name}/execute

# Get Function Definition
Source: https://aci.dev/docs/api-reference/functions/get-function-definition

get /v1/functions/{function_name}/definition
Return the function definition that can be used directly by LLM.
The actual content depends on the intended model (inference provider, e.g., OpenAI, Anthropic, etc.) and the function itself.

# Search Functions
Source: https://aci.dev/docs/api-reference/functions/search-functions

get /v1/functions/
Returns the basic information of a list of functions.

# Delete Linked Account
Source: https://aci.dev/docs/api-reference/linked-accounts/delete-linked-account

delete /v1/linked-accounts/{linked_account_id}
Delete a linked account by its id.

# Get Linked Account
Source: https://aci.dev/docs/api-reference/linked-accounts/get-linked-account

get /v1/linked-accounts/{linked_account_id}
Get a linked account by its id.
- linked_account_id uniquely identifies a linked account across the platform.

# Link Oauth2 Account
Source: https://aci.dev/docs/api-reference/linked-accounts/link-oauth2-account

get /v1/linked-accounts/oauth2
Start an OAuth2 account linking process.
It will return a redirect url (as a string, instead of RedirectResponse) to the OAuth2 provider's authorization endpoint.

# Linked Accounts Oauth2 Callback
Source: https://aci.dev/docs/api-reference/linked-accounts/linked-accounts-oauth2-callback

get /v1/linked-accounts/oauth2/callback
Callback endpoint for OAuth2 account linking.
- A linked account (with necessary credentials from the OAuth2 provider) will be created in the database.

# List Linked Accounts
Source: https://aci.dev/docs/api-reference/linked-accounts/list-linked-accounts

get /v1/linked-accounts
List all linked accounts.
- Optionally filter by app_name and linked_account_owner_id.
- app_name + linked_account_owner_id can uniquely identify a linked account.
- This can be an alternatively way to GET /linked-accounts/{linked_account_id} for getting a specific linked account.

# Overview
Source: https://aci.dev/docs/api-reference/overview

The ACI.dev API powers the ACI.dev platform and SDK.

<Note>
 Most of the time, you won’t need to interact with the API directly. Instead, you should use our offerrings through either [platform](platform.aci.dev) or [SDK](https://github.com/aipotheosis-labs/aci-python-sdk).
</Note>

<Note>
 Our [SDK](https://github.com/aipotheosis-labs/aci-python-sdk) interacts with these APIs under the hood, but provide additional agent-centric features specifically designed for LLM-based agents.
</Note>

## Authentication

For programmatic access, the API supports API key-based authentication. You can generate an API key by creating an agent on [ACI.dev platform](platform.aci.dev).
You can then provide this API key to SDK environment variable or set it in `X-API-KEY` header if you are calling API directly.

<Card title="Sign up to ACI.dev" icon="lock-open" href="https://platform.aci.dev/" />

# Agent
Source: https://aci.dev/docs/core-concepts/agent

An Agent is a logical actor within a project that accesses the platform

<Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/agents.png" alt="Agent Concept Illustration" />
</Frame>

* Represents a specific context or purpose for accessing the platform
* Has its own API key for authentication
* Can be restricted to use only specific `Apps` (select from the list of `Configured Apps`) within the `Project`
* Can have `Custom Instructions` for how to (and how not to) use `Functions`
* Allows for a natural multi-agent architecture within a single `Project`

<Note>
 Agents are designed to support multi-agent systems. Each agent can have its own set of allowed `Apps` and `Custom Instructions`, enabling specialized behaviors. For simple use cases, you can use the default agent created for your `Project`.
</Note>

## Agent Level Access Control

For each `App` you configured, you can specify if you want to allow the agent to access that `App`.

<Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/agent-allowed-apps.png" alt="Agent Concept Illustration" />
</Frame>

## Custom Instructions

You can specify a `Custom Instruction` per `Function` for the `Agents` to follow. e.g.,:

* `GMAIL__SEND_EMAIL`: "Don't send emails to people outside my organization"
* `BRAVE_SEARCH__WEB_SEARCH`: "Only allowed to search the web for the following topics: \[...]"
* `GITHUB__STAR_REPOSITORY`: "Don't star repositories that are not related to AI"

<Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/custom-instructions.png" alt="Agent Concept Illustration" />
</Frame>

# App
Source: https://aci.dev/docs/core-concepts/app

An App represents an integration with an external service or platform (like GitHub, Google, Slack, etc.) that exposes a set of functions for AI agents to use.

<Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/apps.png" alt="App Concept Illustration" />
</Frame>

## Each App:

* Has a unique name across the platform (e.g., `GITHUB`, `SLACK`, `BRAVE_SEARCH`)
* Contains a collection of related functions usable by AI agents that interact with the external service
* Supports one or more security schemes (OAuth2, API Key, etc.) for authentication
* Has metadata including description, logo, version, provider information, and categories

# App Configuration
Source: https://aci.dev/docs/core-concepts/app-configuration

You need to create an App Configuration before your AI agents can use an App.

An `App Configuration` is created when you configure an `App` under a `Project`. It is a project-specific integration setting for a third-party service (an App) in the ACI platform. It represents:

<Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/app-configuration-popup.png" alt="App Configuration Concept Illustration" />
</Frame>

* **Integration Record**: The formal relationship between your Project and a specific App (like GitHub, Google Calendar, etc.)
* **Authentication Strategy**: The selected security scheme (`OAuth2`, `API Key`, `No Auth`) used for authenticating with the App
* **Security Overrides**: Custom authentication parameters that override default App settings (e.g., client IDs, secrets)
* **Function Access Control**: Which specific functions from the App are enabled for use in your Project
* **Linked Accounts Management**: Serves as the parent configuration for all individual user accounts connected to this App

<Note>
 You **MUST** create an `App Configuration` before your AI agents can use an `App`. Each `Project` can have one configuration per `App`, allowing you to control which `Apps` and `Functions` are accessible within that `Project`.
</Note>

Each Project can configure multiple Apps, but only one configuration per App is allowed to maintain simplicity. App Configurations are prerequisites for using any third-party service with your AI agents and are managed through the ACI Developer Portal.

## Authentication Types

Each App may support one or more authentication types. You need to select one that works for your use case when creating an `App Configuration`.

All the `Linked Accounts` under the `App Configuration` will use the same authentication type.

* **OAuth2**: The most common authentication type for third-party services, e.g.: Gmail
 <Note>
 For OAuth2-based apps, you can use your own OAuth2 client instead of ACI.dev's default OAuth2 client. Please refer to [OAuth2 White-label](/advanced/oauth2-whitelabel) for more details.
 </Note>
* **API Key**: A simple authentication method that uses an API key to authenticate requests, e.g.: Brave 
* **No Auth**: Some apps do not require additional authentication, e.g.: Arxiv, Hackernews

# Function (Tool)
Source: https://aci.dev/docs/core-concepts/function

A Function is a callable operation that belongs to an App

Function in our platform is equivalent to the concept of `Function` or `Tool` in function/tool calling.
Functions are logically grouped by the App they belong to.

<Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/functions.png" alt="Function Concept Illustration" />
</Frame>

## Each Function:

* Have a unique name across the platform, typically in the format `APP_NAME__FUNCTION_NAME` (e.g., "GITHUB\_\_STAR\_REPOSITORY")
* Is compatible with function calling schema of OpenAI, Anthropic etc
* Define the parameters they accept and the response they return
* Handle the communication with external services
* Inherit the authentication configuration from the App

<Note>
 Functions are the building blocks that AI agents use to interact with external services. Each function has a specific purpose, such as creating a GitHub repository or sending a Slack message.
</Note>

# Linked Account
Source: https://aci.dev/docs/core-concepts/linked-account

A Linked Account represents a connection to an external service (App) for a specific end-user

* Associates authentication credentials with a specific `App` in your `Project`
* Stores security credentials (OAuth tokens, API keys, etc.) securely
* Enables your agents to perform actions on behalf of specific end-users
* Can be enabled, disabled, or deleted as needed
* Is identified by a unique combination of `Project`, `App`, and `Linked Account Owner ID`

<Note>
 When you link an account (like connecting to GitHub via OAuth2, or Brave Search via API Key), the platform securely stores the credentials needed to access that service. Your agents can then use these credentials to perform actions on behalf of that end-user.
</Note>

<Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/link-account.png" alt="Linked Account Concept Illustration" />
</Frame>

## What is Linked Account Owner ID?

* The `Linked Account Owner ID` is a unique identifier for the end-user that is used to link the `Linked Account` to the end-user.
* You determine the `Linked Account Owner ID` value. It can be a user ID from your system, an email address, or any other identifier that helps you track which end-user the linked account belongs to.
* When executing functions, you must provide this ID so the platform knows which credentials to use. It enables your agents to act on behalf of specific users when executing functions.

<Note>
 Note that the `Linked Account Owner ID` itself can NOT uniquely identify a `Linked Account`.
 A single `Linked Account Owner ID` can be associated with multiple `Linked Accounts`, for example, one account for `GITHUB` and one account for `GMAIL`, both linked to the same end-user.

 However, within a single `App`, the `Linked Account Owner ID` must be unique.
</Note>

<AccordionGroup>
 <Accordion title="If Your Product Have Multiple End-Users" icon="users">
 * If your agentic application have multiple end-users, you can create a `Linked Account` for each end-user per `App` (configured).
 * Each `Linked Account` then represents a specific end-user's connection/authentication to a specific `App`.
 * Ideally, you'll need to create a `Linked Account` for each end-user per `App`. (And use the same `Linked Account Owner ID` for the same end-user.)
 </Accordion>

 <Accordion title="If Your Product Have a Single End-User" icon="user">
 If your agentic application have a single end-user, or you are building the agent for your own use, you probably only need a single `Linked Account` per `App`, and in that case, you can use any value for the `Linked Account Owner ID`.
 </Accordion>
</AccordionGroup>

## Tutorials

<AccordionGroup>
 <Accordion title="Linking OAuth2 Account" icon="user">
 * If you are linking an OAuth2 account for yourself, you can just click `Start OAuth2 Flow` button, and follow the authorization flow to link your account.
 * If you don't have access to the account, you can click `Copy OAuth2 URL` button, and send the URL to the end-user to complete the authorization flow.
 * A `Linked Account` under this `App` and `Owner ID` will be created after authorization is complete.

 <Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/link-account-oauth2.png" alt="Linked Account OAuth2 Illustration" />
 </Frame>
 </Accordion>

 <Accordion title="Linking API Key Account" icon="user">
 * The API key is specific to the `App`, for example, if you are linking an account for `BRAVE_SEARCH`, a brave search API key will be needed.
 * Depending on your product, you can either provide the API key yourself or collect it from the end-user.

 <Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/link-account-api-key.png" alt="Linked Account API Key Illustration" />
 </Frame>
 </Accordion>

 <Accordion title="Linking No Auth Account" icon="user">
 * Some apps don't require authentication, for example, web scraping apps such as `HACKERNEWS`, `ARXIV`, or Apps provided by ACI.dev (`AGENT_SECRETS_MANAGER`)

 <Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/link-account-no-auth.png" alt="Linked Account No Auth Illustration" />
 </Frame>
 </Accordion>
</AccordionGroup>

# Project
Source: https://aci.dev/docs/core-concepts/project

A Project is a logical container for isolating and managing resources.

<Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/project.png" alt="Project Concept Illustration" />
</Frame>

* Owned by either a user or an organization
* Contains **configured** `Apps`, `Agents` (and their API Keys), and `Linked Accounts`
* Serves as a boundary for resource management and permissions

<Note>
 A `Project` is your workspace within the platform. It's where you configure `Apps`, create and manage `Agents` (and their API Keys), and manage `Linked Accounts`. Each `Project` has its own resources and settings, allowing you to create isolated environments for different use cases or clients.
</Note>

# Overview
Source: https://aci.dev/docs/introduction/overview

Welcome to the ACI.dev developer documentation

<img className="block dark:hidden" src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/hero-light.svg" alt="Hero Light" width="800" />

<img className="hidden dark:block" src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/hero-dark.svg" alt="Hero Dark" width="800" />

## What is ACI.dev?

ACI.dev is an tool-calling and unified MCP server platform created by Aipolabs that helps developers connect AI agents to applications like Zendesk, Slack, Gmail, or their own internal tools, manage AI agent actions, and discover workflows.

## What can you do with ACI.dev?

<CardGroup cols={1}>
 <Card title="Integrate B2B SaaS tools">
 Add a host of B2B SaaS tools easily to your agentic worker through our pre-built integrations. Immediately ready to use with our built-in authenticated tool-calling.
 </Card>

 <Card title="Handle end-user authentication">
 Allow your users to securely connect to their own accounts with services like Gmail and Slack for agentic workers to perform actions on their behalf.
 </Card>

 <Card title="Guardrail API executions by instruction filters">
 Improve agentic worker reliability by using natural language to set flexible filters that block API execution if an agent is making an API request beyond its intended purposes.
 </Card>

 <Card title="Discover agentic workflows">
 Allow agents to dynamically discover applications and APIs to use for its tasks to improve agent tool-calling performance without clogging your context window.
 </Card>
</CardGroup>

## Develop AI Agent Workers in Minutes

Try ACI.dev now and simplify the hardest parts of developing AI agents.

<CardGroup cols={2}>
 <Card title="Quickstart Guide" icon="rocket" href="/introduction/quickstart">
 Start building your agentic worker with ACI.dev immediately.
 </Card>

 <Card title="Reference APIs" icon="code" href="/api-reference/overview">
 View API references and documentation.
 </Card>

 <Card title="Python SDK" icon="screwdriver-wrench" href="https://github.com/aipotheosis-labs/aci-python-sdk">
 Check out our Python SDK directly.
 </Card>

 <Card title="Developer Portal" icon="stars" href="https://platform.aci.dev">
 Manage your agentic worker integrations through our developer portal.
 </Card>
</CardGroup>

# Quickstart
Source: https://aci.dev/docs/introduction/quickstart

Power Your First AI Agent with ACI.dev

This guide walk you through building an AI agent with function calling capability with ACI.dev

# Sign up to the Platform

* [platform.aci.dev <Icon icon="up-right-from-square" />](https://platform.aci.dev) .
* We'll create a default `project` and default `agent` for you when you first log in to the platform.

# Configure Your First App for Your AI Agent to Use

<Steps>
 <Step title="Configure Github in App Store">
 Navigate to `App Store` and find [GITHUB <Icon icon="up-right-from-square" />](https://platform.aci.dev/apps/GITHUB).
 Then click on `Configure App` button to set up the app for your project.

 <Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/github_configure_app.png" alt="GitHub configuration" />
 </Frame>
 </Step>

 <Step title="Link your Github account">
 * Navigate to `App Configurations` and find [GITHUB App Configuration <Icon icon="up-right-from-square" />](https://platform.aci.dev/appconfig/GITHUB). Then click on `Add Account` button to link your Github account.

 <Note>
 `linked account owner id` is the ID of the owner of the linked account. It's up to you to decide which ID to use—it can be the unique end-user ID from your system. Or If you're building an agent for yourself, you can choose any name you prefer. Later, you'll need to provide this `linked account owner id` in your code to execute functions on behalf of the user.
 </Note>

 <Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/github_link_account.png" />
 </Frame>

 * Click `Start OAuth2 Flow` button to start the OAuth2 flow and link your Github account under the project.
 </Step>

 <Step title="Allow Your Agents to Access GITHUB">
 <Note>
 * We took an opinionated approach to acommodate a multi-agent architecture. You can create multiple agents within the project, and each agent has its own API key and apps that they are allowed to use.
 * We created a default agent for you when you first log in to the platform.
 </Note>

 Navigate to the project setting page: [Manage Project <Icon icon="up-right-from-square" />](https://platform.aci.dev/project-setting). Then click the `Edit` button under `ALLOWED APPS` column of the agent to allow access to the `GITHUB` app.

 <Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/agent_allowed_apps.png" />
 </Frame>
 </Step>

 <Step title="Grab the API key">
 Each `Agent` is assigned an API key, which you can use to send requests to our platform—either via raw HTTP requests or our SDK. Later, you'll need to include this API key in your code.

 <Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/platform/agent_api_key.png" />
 </Frame>
 </Step>
</Steps>

# Code Example

The ACI Python SDK requires Python 3.10+.
The example below uses `uv` for package installation, but you can use `pip` or any other package manager of your choice.

The full example code is available at the end of this guide.

<Steps>
 <Step title="Install ACI Python SDK">
 * Install the ACI Python SDK

 ```bash bash
 uv add aci-sdk
 ```

 * To run the example, you'll also need to install other required packages.

 ```bash bash
 uv add openai python-dotenv
 ```
 </Step>

 <Step title="Provide the API key to the SDK">
 You'll need both the ACI API key and the OpenAI API key to run the example in this section. Create a .env file in the root of your project and add the following:

 ```bash .env
 ACI_API_KEY=your_aci_api_key
 OPENAI_API_KEY=your_openai_api_key
 ```
 </Step>

 <Step title="Create ACI Client and OpenAI Client">
 ```python python 3.10+
 from dotenv import load_dotenv
 from aci import ACI
 from openai import OpenAI

 load_dotenv()

 aci = ACI()
 openai = OpenAI()
 ```
 </Step>

 <Step title="Get the Function Definition">
 ```python python 3.10+
 github_star_repo_function = aci.functions.get_definition("GITHUB__STAR_REPOSITORY")
 ```
 </Step>

 <Step title="Append the Function Definition to the LLM Request">
 ```python python 3.10+
 response = openai.chat.completions.create(
 model="gpt-4o-2024-08-06",
 messages=[
 {
 "role": "system",
 "content": "You are a helpful assistant with access to a variety of tools.",
 },
 {
 "role": "user",
 "content": "Star the aipotheosis-labs/aci githubrepository for me",
 },
 ],
 tools=[github_star_repo_function],
 tool_choice="required", # force the model to generate a tool call for demo purposes
 )
 ```
 </Step>

 <Step title="Handle the Tool Call Response and Execute the Function via ACI.dev">
 <Warning>
 Replace `<LINKED_ACCOUNT_OWNER_ID>` with the `linked account owner id` you used when linking your Github account.
 </Warning>

 ```python python 3.10+ {11}
 tool_call = (
 response.choices[0].message.tool_calls[0]
 if response.choices[0].message.tool_calls
 else None
 )

 if tool_call:
 result = aci.handle_function_call(
 tool_call.function.name,
 json.loads(tool_call.function.arguments),
 linked_account_owner_id=<LINKED_ACCOUNT_OWNER_ID>
 )
 ```
 </Step>

 <Step title="Full Runnable Code">
 Here is the complete runnable code for the example above, you can copy and paste it into a file and run it.

 <Warning>
 * Remember to provide api keys in the `.env` file.
 * Replace `<LINKED_ACCOUNT_OWNER_ID>` with the `linked account owner id` you used when linking your Github account.
 </Warning>

 ```python python 3.10+ {42}
 import json
 from dotenv import load_dotenv
 from openai import OpenAI
 from aci import ACI
 load_dotenv()

 openai = OpenAI()
 aci = ACI()

 def main() -> None:
 # For a list of all supported apps and functions, please go to the platform.aci.dev
 print("Getting function definition for GITHUB__STAR_REPOSITORY")
 github_star_repo_function = aci.functions.get_definition("GITHUB__STAR_REPOSITORY")

 print("Sending request to OpenAI")
 response = openai.chat.completions.create(
 model="gpt-4o-2024-08-06",
 messages=[
 {
 "role": "system",
 "content": "You are a helpful assistant with access to a variety of tools.",
 },
 {
 "role": "user",
 "content": "Star the aipotheosis-labs/aci github repository for me",
 },
 ],
 tools=[github_star_repo_function],
 tool_choice="required", # force the model to generate a tool call for demo purposes
 )
 tool_call = (
 response.choices[0].message.tool_calls[0]
 if response.choices[0].message.tool_calls
 else None
 )

 if tool_call:
 print("Handling function call")
 result = aci.handle_function_call(
 tool_call.function.name,
 json.loads(tool_call.function.arguments),
 linked_account_owner_id=<LINKED_ACCOUNT_OWNER_ID>,
 )
 print(result)

 if __name__ == "__main__":
 main()

 ```
 </Step>
</Steps>

# Advanced Usage

For more advanced usage, please refer to the examples in our [ACI Agents Repository <Icon icon="up-right-from-square" />](https://github.com/aipotheosis-labs/aci-agents/tree/main).

# Apps MCP Server
Source: https://aci.dev/docs/mcp-servers/apps-server

Expose functions from specific apps that you pre-select

## Overview

The `Apps MCP Server` provides direct access to functions (tools) from specific app(s) you select. Unlike most MCP servers that are bound to a single app, this server allows you to combine multiple apps in one server.

## Benefits

* **Multi-App Support** - Include functions from multiple apps in a single MCP server
* **Direct Function Access** - Functions appear directly in the LLM's tool list without discovery steps (Which usually have better performance if your usecase is very specific)
* **Selective Inclusion** - Only include the Apps whose functions you want to expose
* **Reduced Server Management** - No need to run multiple MCP servers for different apps
* **Familiar Pattern** - Similar to traditional MCP server concept but with multi-app capability

## How It Works

The Apps MCP Server directly exposes the functions (tools) from the apps you specify with the `--apps` parameter. When an MCP client interacts with this server, all functions from the specified apps will be available in its tool list.

This approach differs from the `Unified MCP Server` in that there's no dynamic discovery process - all function (tool) definitions are directly available to MCP clients.

<Note>
 Unlike most MCP servers that are limited to a single app, the `Apps MCP Server` allows you to combine functions from multiple apps in a single server, reducing the number of servers you need to manage.
</Note>

## Prerequisites

Before using the `Apps MCP Server`, you need to complete several setup steps on the ACI.dev platform.

<Steps>
 <Step title="Get your ACI.dev API Key">
 You'll need an API key from one of your ACI.dev agents. Find this in your [project setting <Icon icon="up-right-from-square" />](https://platform.aci.dev/project-setting)
 </Step>

 <Step title="Configure Apps">
 Navigate to the [App Store <Icon icon="up-right-from-square" />](https://platform.aci.dev/apps) to configure the apps you want to use with your MCP servers.

 <Note>
 For more details on what is an app and how to configure it, please refer to the [App](../core-concepts/app) section.
 </Note>
 </Step>

 <Step title="Set Allowed Apps">
 In your [Project Setting <Icon icon="up-right-from-square" />](https://platform.aci.dev/project-setting), enable the apps you want your agent to access by adding them to the `Allowed Apps` list.

 <Note>
 For more details on how and why to set allowed apps, please refer to the [Agent](../core-concepts/agent) section.
 </Note>
 </Step>

 <Step title="Link Accounts For Each App">
 For each app you want to use, you'll need to link end-user (or your own) accounts. During account linking, you'll specify a `linked-account-owner-id` which you'll later provide when starting the MCP servers.

 <Note>
 For more details on how to link accounts and what `linked-account-owner-id` is, please refer to the [Linked Accounts](../core-concepts/linked-account) section.
 </Note>
 </Step>

 <Step title="Install the Package">
 ```bash
 # Install uv if you don't have it already
 curl -sSf https://install.pypa.io/get-pip.py | python3 -
 pip install uv
 ```
 </Step>
</Steps>

## Integration with MCP Clients

<Note>
 * Replace the `<LINKED_ACCOUNT_OWNER_ID>` and `<YOUR_ACI_API_KEY>` below with the `linked-account-owner-id` of your linked accounts and your ACI.dev API key respectively.
 * Replace `<APP_1>,<APP_2>,...` with the apps you set as allowed for your agent in the [Project Setting <Icon icon="up-right-from-square" />](https://platform.aci.dev/project-setting).
</Note>

<AccordionGroup>
 <Accordion title="Cursor & Windsurf" icon="code">
 <Note>
 Make sure you hit the refresh button on the MCP settings page after entering your own API key and Owner ID.

 <Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/cursor-unified-mcp.png" alt="Cursor Unified MCP" />
 </Frame>
 </Note>

 ```json mcp.json
 {
 "mcpServers": {
 "aci-mcp-apps": {
 "command": "uvx",
 "args": ["aci-mcp", "apps-server", "--apps", "<APP_1>,<APP_2>,...", "--linked-account-owner-id", "<LINKED_ACCOUNT_OWNER_ID>"],
 "env": {
 "ACI_API_KEY": "<ACI_API_KEY>"
 }
 }
 }
 }
 ```
 </Accordion>

 <Accordion title="Claude Desktop" icon="message-bot">
 <Note>
 Make sure to restart the Claude Desktop app after adding the MCP server configuration.
 </Note>

 ```json claude_desktop_config.json
 {
 "mcpServers": {
 "aci-mcp-unified": {
 "command": "bash",
 "args": [
 "-c",
 "ACI_API_KEY=<YOUR_ACI_API_KEY> uvx aci-mcp apps-server --apps <APP_1>,<APP_2>,... --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID>"
 ]
 }
 }
 }
 ```
 </Accordion>

 <Accordion title="Running Locally" icon="rectangle-terminal">
 ```bash terminal
 # Set API key
 export ACI_API_KEY=<YOUR_ACI_API_KEY>

 # Option 1: Run in stdio mode (default)
 uvx aci-mcp apps-server --apps "<APP_1>,<APP_2>,..." --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID>

 # Option 2: Run in sse mode
 uvx aci-mcp apps-server --apps "<APP_1>,<APP_2>,..." --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID> --transport sse --port 8000
 ```
 </Accordion>
</AccordionGroup>

## Commandline Arguments

<AccordionGroup>
 <Accordion title="[Required] --apps">
 The `apps` argument is used to specify the apps you want to use with your MCP server. E.g., `--apps GMAIL,BRAVE,GITHUB` means that the MCP server will only access and expose the functions (tools) from `GMAIL`, `BRAVE` and `GITHUB` apps.

 <Note>
 The apps must be configured and enabled first.
 </Note>
 </Accordion>

 <Accordion title="[Required] --linked-account-owner-id">
 The `linked-account-owner-id` is the owner ID of the linked accounts you want to use for the function execution. E.g., `--linked-account-owner-id johndoe` means that the function execution (e.g, `GMAIL__SEND_EMAIL`) will be done on behalf of the linked account of `GMAIL` app with owner ID `johndoe`.
 </Accordion>

 <Accordion title="[Optional] --transport">
 The `transport` argument is used to specify the transport protocol to use for the MCP server.
 The default transport is `stdio`.
 </Accordion>

 <Accordion title="[Optional] --port">
 The `port` argument is used to specify the port to listen on for the MCP server if the `--transport` is set to `sse`.
 The default port is `8000`.
 </Accordion>
</AccordionGroup>

```bash help
$ uvx aci-mcp apps-server --help
Usage: aci-mcp apps-server [OPTIONS]

 Start the apps-specific MCP server to access tools under specific apps.

Options:
 --apps TEXT comma separated list of apps of which to use
 the functions [required]
 --linked-account-owner-id TEXT the owner id of the linked accounts to use
 for the tool calls. You'll need to create
 the linked accounts on platform.aci.dev
 [required]
 --transport [stdio|sse] Transport type
 --port INTEGER Port to listen on for SSE
 --help Show this message and exit.
```

# Introduction
Source: https://aci.dev/docs/mcp-servers/introduction

Introduction to ACI.dev MCP Servers

## Overview

Apart from using ACI.dev's Apps/Functions (tools) directly via LLM function (tool) calls, we also provide two types of Model Context Protocol (MCP) servers that allow your MCP clients to access all Apps/Functions (tools) available on ACI.dev platform.
The codebase is open source and can be found here: [aci-mcp <Icon icon="up-right-from-square" />](https://github.com/aipotheosis-labs/aci-mcp).

## Two Types of MCP Servers

* **Apps MCP Server**: This server is similar to most of the existing MCP servers out there, where it exposes a set of functions from a specific app (e.g., Gmail, Github, etc.). However, our `Apps MCP Server` allows you to include multiple apps in a single server.

 <Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/apps-mcp-server-diagram.svg" alt="Apps MCP Server" />
 </Frame>
* **Unified MCP Server**: This server is a dynamic server that provides two **meta** functions (tools) - `ACI_SEARCH_FUNCTIONS` and `ACI_EXECUTE_FUNCTION` to dynamically discover and execute **ANY** functions (tools) available on ACI.dev platform.

 <Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/unified-mcp-server-diagram.svg" alt="Unified MCP Server" />
 </Frame>

## Comparison

* **When to use the Apps MCP Server?**
 * When you know exactly what apps the LLM/Agent needs in advance.
 * When the number of apps, and therefore the associated functions, needed is relatively small.
 <Note>
 There is no definitive answer to `what number of functions (tools) is too many?`, but the more functions (tools) you add to the model's context window, the lower the performance of the LLM function calling.
 </Note>

* **When to use the Unified MCP Server?**
 * When you don't know exactly what apps the LLM/Agent needs in advance.
 * When the number of apps and therefore the associated functions needed is large.
 * When you want all future apps added to ACI.dev to be discoverable by your LLM/Agent without having to update the MCP command.

## Next Steps

Choose the MCP server that best fits your needs and follow the instructions in the respective sections to set it up.

<CardGroup cols={2}>
 <Card title="Unified MCP Server" icon="circle-nodes" href="/mcp-servers/unified-server">
 A unified, dynamic MCP server that provides two meta functions (tools) to discover and execute ANY functions (tools) available on ACI.dev platform.
 </Card>

 <Card title="Apps MCP Server" icon="puzzle-piece" href="/mcp-servers/apps-server">
 A traditional MCP server that directly exposes functions from specific apps that you pre-select, allowing multiple apps to be included in a single server.
 </Card>
</CardGroup>

# Unified MCP Server
Source: https://aci.dev/docs/mcp-servers/unified-server

Unified, Dynamic Function (Tool) Discovery and Execution

## Overview

The Unified MCP Server provides a smart, scalable approach to function calling by exposing just two meta functions (tools) that can:

1. Dynamically discover the right functions (tools) based on user intent
2. Execute any function on the ACI.dev platform retrieved from the search results

## How It Works

The `Unified MCP Server` exposes two meta-functions:

1. `ACI_SEARCH_FUNCTIONS` - Discovers functions based on your intent/needs
2. `ACI_EXECUTE_FUNCTION` - Executes any function discovered by the 
<Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/unified-mcp-architecture.png" alt="Unified MCP Server Flow" />
</Frame>

This approach allows LLMs to first search for the right tool based on the user's needs and then execute it, without needing to list all available functions upfront.

## Benefits

* **Reduced Context Window Usage** - Instead of loading hundreds of function definitions into your LLM's context window, the unified server keeps it minimal with just two functions (tools)
* **Dynamic Discovery** - The server intelligently finds the most relevant tools for your specific task
* **Complete Function Coverage** - Access to ALL functions on the ACI.dev platform without configuration changes
* **Simplified Integration** - No need to manage multiple MCP servers for different apps or groups of functions (tools)

## Prerequisites

Before using the `Unified MCP Server`, you need to complete several setup steps on the ACI.dev platform.

<Steps>
 <Step title="Get your ACI.dev API Key">
 You'll need an API key from one of your ACI.dev agents. Find this in your [project setting <Icon icon="up-right-from-square" />](https://platform.aci.dev/project-setting)
 </Step>

 <Step title="Configure Apps">
 Navigate to the [App Store <Icon icon="up-right-from-square" />](https://platform.aci.dev/apps) to configure the apps you want to use with your MCP servers.

 <Note>
 For more details on what is an app and how to configure it, please refer to the [App](../core-concepts/app) section.
 </Note>
 </Step>

 <Step title="Set Allowed Apps">
 In your [Project Setting <Icon icon="up-right-from-square" />](https://platform.aci.dev/project-setting), enable the apps you want your agent to access by adding them to the `Allowed Apps` list.

 <Note>
 For more details on how and why to set allowed apps, please refer to the [Agent](../core-concepts/agent) section.
 </Note>
 </Step>

 <Step title="Link Accounts For Each App">
 For each app you want to use, you'll need to link end-user (or your own) accounts. During account linking, you'll specify a `linked-account-owner-id` which you'll later provide when starting the MCP servers.

 <Note>
 For more details on how to link accounts and what `linked-account-owner-id` is, please refer to the [Linked Accounts](../core-concepts/linked-account) section.
 </Note>
 </Step>

 <Step title="Install the Package">
 ```bash
 # Install uv if you don't have it already
 curl -sSf https://install.pypa.io/get-pip.py | python3 -
 pip install uv
 ```
 </Step>
</Steps>

## Integration with MCP Clients

For a more reliable experience when using the **Unified MCP Server**, we recommend using the prompt below at the start of your conversation (feel free to modify it to your liking):

```json prompt
You are a helpful assistant with access to a unlimited number of tools via two meta functions:
- ACI_SEARCH_FUNCTIONS
- ACI_EXECUTE_FUNCTION

You can use ACI_SEARCH_FUNCTIONS to find relevant, executable functionss that can help you with your task.
Once you have identified the function you need to use, you can use ACI_EXECUTE_FUNCTION to execute the function provided you have the correct input arguments.
```

<Note>
 Replace the `<LINKED_ACCOUNT_OWNER_ID>` and `<YOUR_ACI_API_KEY>` below with the `linked-account-owner-id` of your linked accounts and your ACI.dev API key respectively.
</Note>

<AccordionGroup>
 <Accordion title="Cursor & Windsurf" icon="code">
 <Note>
 Make sure you hit the refresh button on the MCP settings page after entering your own API key and Owner ID.

 <Frame>
 <img src="https://mintlify.s3.us-west-1.amazonaws.com/aipotheosislabs-60d5bdcb/images/cursor-unified-mcp.png" alt="Cursor Unified MCP" />
 </Frame>
 </Note>

 ```json mcp.json
 {
 "mcpServers": {
 "aci-mcp-unified": {
 "command": "uvx",
 "args": ["aci-mcp", "unified-server", "--linked-account-owner-id", "<LINKED_ACCOUNT_OWNER_ID>", "--allowed-apps-only"],
 "env": {
 "ACI_API_KEY": "<YOUR_ACI_API_KEY>"
 }
 }
 }
 }
 ```
 </Accordion>

 <Accordion title="Claude Desktop" icon="message-bot">
 <Note>
 Make sure to restart the Claude Desktop app after adding the MCP server configuration.
 </Note>

 ```json claude_desktop_config.json
 {
 "mcpServers": {
 "aci-mcp-unified": {
 "command": "bash",
 "args": [
 "-c",
 "ACI_API_KEY=<YOUR_ACI_API_KEY> uvx aci-mcp unified-server --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID> --allowed-apps-only"
 ]
 }
 }
 }
 ```
 </Accordion>

 <Accordion title="Running Locally" icon="rectangle-terminal">
 ```bash terminal
 # Set API key
 export ACI_API_KEY=<YOUR_ACI_API_KEY>

 # Option 1: Run in stdio mode (default)
 uvx aci-mcp unified-server --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID> --allowed-apps-only

 # Option 2: Run in sse mode
 uvx aci-mcp unified-server --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID> --allowed-apps-only --transport sse --port 8000
 ```
 </Accordion>
</AccordionGroup>

## Commandline Arguments

<AccordionGroup>
 <Accordion title="[Optional] --allowed-apps-only">
 The `allowed-apps-only` flag is used to limit the apps/functions (tools) search (via `ACI_SEARCH_FUNCTIONS`) to only the allowed apps that are accessible to this agent (which is identified by the `ACI_API_KEY`). If not provided, the `ACI_SEARCH_FUNCTIONS` will be conducted on all apps/functions available on the ACI.dev platform.
 </Accordion>

 <Accordion title="[Required] --linked-account-owner-id">
 The `linked-account-owner-id` is the owner ID of the linked accounts you want to use for the function execution. E.g., `--linked-account-owner-id johndoe` means that the function execution (e.g, `GMAIL__SEND_EMAIL`) will be done on behalf of the linked account of `GMAIL` app with owner ID `johndoe`.
 </Accordion>

 <Accordion title="[Optional] --transport">
 The `transport` argument is used to specify the transport protocol to use for the MCP server.
 The default transport is `stdio`.
 </Accordion>

 <Accordion title="[Optional] --port">
 The `port` argument is used to specify the port to listen on for the MCP server if the `--transport` is set to `sse`.
 The default port is `8000`.
 </Accordion>
</AccordionGroup>

```bash help
$ uvx aci-mcp unified-server --help
Usage: aci-mcp unified-server [OPTIONS]

 Start the unified MCP server with unlimited tool access.

Options:
 --allowed-apps-only Limit the functions (tools) search to only
 the allowed apps that are accessible to this
 agent. (identified by ACI_API_KEY)
 --linked-account-owner-id TEXT the owner id of the linked account to use
 for the tool calls [required]
 --transport [stdio|sse] Transport type
 --port INTEGER Port to listen on for SSE
 --help Show this message and exit.
```

# Custom Functions (Tools)
Source: https://aci.dev/docs/sdk/custom-functions

You can use your local functions for function (tool) calling along with the functions (tools) provided by ACI.dev

The [ACI SDK <Icon icon="up-right-from-square" />](https://github.com/aipotheosis-labs/aci-python-sdk) provides a utility function to convert your local functions to the format required by different LLM providers. (e.g. OpenAI, Anthropic, etc.)

For details, please refer to the [Custom Functions <Icon icon="up-right-from-square" />](https://github.com/aipotheosis-labs/aci-python-sdk?tab=readme-ov-file#to_json_schema)

# Introduction
Source: https://aci.dev/docs/sdk/intro

The [ACI Python SDK <Icon icon="up-right-from-square" />](https://github.com/aipotheosis-labs/aci-python-sdk) offers a convenient way to access the ACI REST API from any Python 3.10+ application.

In most cases, you should use the SDK to interact with our system programmatically unless you have a specific reason to call the API directly.

Both the SDK and API are currently in beta, so breaking changes may occur.

<Note>
 SDKs for additional languages are coming soon. If you're interested in contributing to our open-source SDKs, please [reach out <Icon icon="envelope" />](mailto:support@aipolabs.xyz)!
</Note>

## Usage

**ACI.dev** is built with **agent-first** principles. Although you can call each of the APIs and use the SDK any way you prefer in your application, we strongly recommend trying the [Agent-centric <Icon icon="up-right-from-square" />](https://github.com/aipotheosis-labs/aci-python-sdk?tab=readme-ov-file#agent-centric-features) features and taking a look at the [agent examples <Icon icon="up-right-from-square" />](https://github.com/aipotheosis-labs/aci-agents/tree/main) to get the most out of the platform and to enable the full potential and vision of future agentic applications.

<Note>
 For complete and up-to-date documentation, please check out the [SDK repository <Icon icon="up-right-from-square" />](https://github.com/aipotheosis-labs/aci-python-sdk).
</Note>

# Meta Functions (Tools)
Source: https://aci.dev/docs/sdk/metafunctions

Designed with an LLM-centric approach

Beyond the standard wrapper around the ACI.dev APIs,, the SDK provides a suite of features and helper functions to make it easier and more seamless to use functions in LLM powered agentic applications. This is our vision and the recommended way of trying out the SDK in agentic applications.

One key feature is the set of meta function schemas we provide.
Essentially, they are just the json schema version of some of the backend APIs of ACI.dev. They are provided so that your LLM/Agent can utlize some of the features of ACI.dev directly via [function (tool) calling <Icon icon="up-right-from-square" />](https://platform.openai.com/docs/guides/function-calling).

```python
from aci.meta_functions import ACISearchFunctions, ACIExecuteFunction
```

These meta functions differ from the direct function (tool) calls you might typically execute—such as **GITHUB\_\_LIST\_STARGAZERS** — in that they are specifically tailored for use by large language models (LLMs) to interact with ACI.dev backend APIs.

<Note>
 Technically, you can also write your own meta functions around the ACI.dev backend APIs. After getting the input arguments generated by the LLM for the meta functions, you can use the SDK to send the request to the backend APIs with the input arguments.
</Note>

## ACI\_SEARCH\_FUNCTIONS

* It's the json schema version of the `/v1/functions` endpoint and `aci.functions.search` function in SDK.
* It's used to search for available functions (e.g. `GITHUB__STAR_REPOSITORY`, `GMAIL__SEND_EMAIL`, `BRAVE_SEARCH__WEB_SEARCH`) in ACI.dev.

## ACI\_EXECUTE\_FUNCTION

* It's the json schema version of the `/v1/functions/{function_name}/execute` endpoint and `aci.functions.execute` function in SDK.
* It's used to execute a function (e.g. `GITHUB__STAR_REPOSITORY`, `GMAIL__SEND_EMAIL`, `BRAVE_SEARCH__WEB_SEARCH`) in ACI.dev.

## Schemas

<CodeGroup>
 ```python ACI_SEARCH_FUNCTIONS
 from aci.meta_functions import ACISearchFunctions
 from aci.enums import FunctionDefinitionFormat

 # OpenAI (The Chat Completion API)
 print(ACISearchFunctions.to_json_schema(format=FunctionDefinitionFormat.OPENAI))

 """
 {
 "type": "function",
 "function": {
 "name": "ACI_SEARCH_FUNCTIONS",
 "description": "This function allows you to find relevant executable functions and their schemas that can help complete your tasks.",
 "parameters": {
 "type": "object",
 "properties": {
 "intent": {
 "type": "string",
 "description": "Use this to find relevant functions you might need. Returned results of this function will be sorted by relevance to the intent."
 },
 "limit": {
 "type": "integer",
 "default": 100,
 "description": "The maximum number of functions to return from the search per response.",
 "minimum": 1
 },
 "offset": {
 "type": "integer",
 "default": 0,
 "minimum": 0,
 "description": "Pagination offset."
 }
 },
 "required": [],
 "additionalProperties": false
 }
 }
 }
 """
 ```

 ```python ACI_EXECUTE_FUNCTION
 from aci.meta_functions import ACIExecuteFunction
 from aci.enums import FunctionDefinitionFormat

 # OpenAI (The Chat Completion API)
 print(ACIExecuteFunction.to_json_schema(format=FunctionDefinitionFormat.OPENAI))

 """
 {
 "type": "function",
 "function": {
 "name": "ACI_EXECUTE_FUNCTION",
 "description": "Execute a specific retrieved function. Provide the executable function name, and the required function parameters for that function based on function definition retrieved.",
 "parameters": {
 "type": "object",
 "properties": {
 "function_name": {
 "type": "string",
 "description": "The name of the function to execute"
 },
 "function_arguments": {
 "type": "object",
 "description": "A dictionary containing key-value pairs of input parameters required by the specified function. The parameter names and types must match those defined in the function definition previously retrieved. If the function requires no parameters, provide an empty object.",
 "additionalProperties": true
 }
 },
 "required": ["function_name", "function_arguments"],
 "additionalProperties": false
 }
 }
 }
 """
 ```
</CodeGroup>

Together with our **Unified Function Calling Handler**, it offer a powerful, self-discovery mechanism for LLM-driven applications, enabling them to autonomously select, interpret, and execute functions based on the context of a given task or conversation.

```
# unified function calling handler
result = client.handle_function_call(
 tool_call.function.name,
 json.loads(tool_call.function.arguments),
 linked_account_owner_id="john_doe",
 allowed_apps_only=True,
 format=FunctionDefinitionFormat.OPENAI
)
```

<Note>
 For examples of how to use the meta functions, please refer to the [SDK repository <Icon icon="up-right-from-square" />](https://github.com/aipotheosis-labs/aci-python-sdk/tree/main?tab=readme-ov-file#agent-centric-features).
</Note>

# Function (Tool) Use Patterns
Source: https://aci.dev/docs/sdk/tool-use-patterns

Different ways to use the ACI.dev SDK

You can give your AI agent different levels of tool-use autonomy through the meta functions:

* **Pattern 1: Pre-planned Tools**
 * Provide the specific functions (tools) to be used by an LLM.
* **Pattern 2: Dynamic Tool Discovery and Execution**
 * **2.1: Tool List Expansion**
 * Use `ACI_SEARCH_FUNCTIONS` meta function (tool):
 * Search for relevant functions across all apps
 * Add discovered tools directly to the LLM's tool list
 * Allow the LLM to invoke these discovered tools directly by name

 * **2.2: Tool Definition as Text Context Approach**
 * Use `ACI_SEARCH_FUNCTIONS` and `ACI_EXECUTE_FUNCTION` meta functions (tools)
 * Use `ACI_SEARCH_FUNCTIONS` to retrieve tool definitions
 * Present those definitions to the LLM as **text content** instead of adding them to the LLM's tool list
 * The LLM uses `ACI_EXECUTE_FUNCTION` to execute these tools **indirectly**

## Pre-planned

This is the most straright forward use case. You can directly find the functions you want to use on the developer portal, retrieve the function definitions, and append them to your LLM API call. This way your agents will only use the tools you have selected and provided, it would not attempt to find and use other tools.

```python
brave_search_function_definition = aci.functions.get_definition("BRAVE_SEARCH__WEB_SEARCH")

response = openai.chat.completions.create(
 model="gpt-4o-mini",
 messages=[
 {
 "role": "system",
 "content": "You are a helpful assistant with access to a variety of tools.",
 },
 {
 "role": "user",
 "content": "What is ACI.dev by Aipolabs?",
 },
 ],
 tools=[brave_search_function_definition],
)
tool_call = (
 response.choices[0].message.tool_calls[0]
 if response.choices[0].message.tool_calls
 else None
)

if tool_call:
 result = aci.functions.execute(
 tool_call.function.name,
 json.loads(tool_call.function.arguments),
 linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
 )
```

## Dynamic Tool Discovery and Execution With Tool List Expansion

In this use case, the tools list provided to LLM API calls changes according to the function definitions retrieved by the agent from the ACI.dev using the provided meta functions (tools).

The retrieved function definitions are appended to the available tools list for LLMs to decide when and how to use it in subsequent LLM calls. This leverages the ability of many LLMs to enforce adherence of function-call outputs as much as possible to the provided definition, while still offering the flexibility to essentially access as many different tools as needed by the LLM-powered agent.

The trade-off here is that the developer has to manage tool-list and know when to append or remove tools when making the LLM call.

**Example starting tools lists provided to the LLM**

```python
tools_meta = [
 ACISearchFunctions.to_json_schema(FunctionDefinitionFormat.OPENAI),
]
tools_retrieved = []
```

**Adding retrieved function definitions to the tools\_retrieved list**

```python
if tool_call.function.name == ACISearchFunctions.get_name():
 tools_retrieved.extend(result)
```

**Subsequent tool-calling**

```python
response = openai.chat.completions.create(
 model="gpt-4o",
 messages=[
 {
 "role": "system",
 "content": prompt,
 },
 {
 "role": "user",
 "content": "Can you search online for some information about ACI.dev? Use whichever search tool you find most suitable for the task via the ACI meta functions.",
 },
 ]
 + chat_history,
 tools=tools_meta + tools_retrieved,
 parallel_tool_calls=False,
)
if tool_call:
 print(
 f"{create_headline(f'Function Call: {tool_call.function.name}')} \n arguments: {tool_call.function.arguments}"
 )

 result = aci.handle_function_call(
 tool_call.function.name,
 json.loads(tool_call.function.arguments),
 linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
 allowed_apps_only=True,
 format=FunctionDefinitionFormat.OPENAI,
 )
```

For a full example, [see here <Icon icon="up-right-from-square" />](https://github.com/aipotheosis-labs/aci-agents/blob/main/examples/openai/agent_with_dynamic_tool_discovery_pattern_1.py).

## Dynamic Tool Discovery and Execution With Tool Definition as Text Content

In this use case, the tools list provided to the LLM is static, which are just the two meta functions `ACI_SEARCH_FUNCTIONS` and `ACI_EXECUTE_FUNCTION`.

The difference between this and the previous pattern is that retrieved function definitions are provided to the LLM directly as text content instead of being added to the tools list.
The LLM then has to decide whether to call the `ACI_EXECUTE_FUNCTION` to actually execute an API call.

By using the meta functions (tools) this way, the developer does not have to manage the tools list, but the accuracy of tool use can decrease.

**Example tools list provided to LLM**

```python
tools_meta = [
 ACISearchFunctions.to_json_schema(FunctionDefinitionFormat.OPENAI),
 ACIExecuteFunction.to_json_schema(FunctionDefinitionFormat.OPENAI),
]
```

**Tool-calling through LLM**

```python
response = openai.chat.completions.create(
 model="gpt-4o",
 messages=[
 {
 "role": "system",
 "content": prompt,
 },
 {
 "role": "user",
 "content": "Can you search online for some information about ACI.dev? Use whichever search tool you find most suitable for the task via the ACI meta functions.",
 },
 ]
 + chat_history,
 tools=tools_meta,
 parallel_tool_calls=False,
)

tool_call = (
 response.choices[0].message.tool_calls[0]
 if response.choices[0].message.tool_calls
 else None
)

if tool_call:
 result = aci.handle_function_call(
 tool_call.function.name,
 json.loads(tool_call.function.arguments),
 linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
 allowed_apps_only=True,
 format=FunctionDefinitionFormat.OPENAI,
 )
```

For a full example, [see here <Icon icon="up-right-from-square" />](https://github.com/aipotheosis-labs/aci-agents/blob/main/examples/openai/agent_with_dynamic_tool_discovery_pattern_2.py).

---

*This document was automatically crawled and processed for Agent Zero's knowledge base.*
