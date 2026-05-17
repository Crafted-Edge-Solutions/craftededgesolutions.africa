# Shared Agent Context

This directory serves as a centralized, version-controlled workspace for various agents and processes within the Crafted Edge Solutions project. It facilitates collaboration, shared memory, and access to common resources.

## Purpose

This space is intended to hold:
-   **Memory & Logs:** Persistent storage for agent interactions, logs, and session history.
-   **Knowledge Base:** Curated documents, project specifics, client briefs, and data for AI models to draw context from.
-   **Task Management:** Staging areas for tasks, progress tracking, and coordination among agents.
-   **Artifacts:** Storage for generated outputs such as blog drafts, code snippets, or summaries.
-   **Configuration:** Shared configuration parameters relevant to agent operations.

## Usage

Agents and processes should be configured to read from and write to this directory as needed for their functions. All content within this directory is managed by Git, ensuring version history and cross-device synchronization.

## Structure

-   `memory/`: For persistent memory, logs, or conversation history.
-   `knowledge_base/`: For curated documents, project specifics, client briefs, or data for AI models.
-   `current_tasks/`: To potentially stage tasks, track progress, or for agents to coordinate on shared goals.
-   `artifacts/`: To store generated outputs (e.g., blog drafts, code snippets, summaries).
-   `config/`: Potentially for shared configuration parameters if agents need to align on certain settings.

## Version Control

All changes within this directory are tracked by Git. It is recommended to commit changes regularly to maintain a clear history and facilitate synchronization across different environments.
