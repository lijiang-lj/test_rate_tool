#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { Octokit } from "@octokit/rest";
import { ProxyAgent } from "proxy-agent";

const token = process.env.GITHUB_TOKEN;
if (!token) {
  throw new Error("GITHUB_TOKEN environment variable is required");
}

// Build proxy agent from environment. Respects HTTPS_PROXY/HTTP_PROXY/ALL_PROXY and NO_PROXY automatically.
const agent = new ProxyAgent();

// Initialize Octokit with proxy agent
const octokit = new Octokit({
  auth: token,
  request: { agent }
});

// Create MCP server
const server = new McpServer({
  name: "github-mcp-server",
  version: "0.1.0"
});

// Helper: safe JSON stringify
function toPretty(obj: any): string {
  try {
    return JSON.stringify(obj, null, 2);
  } catch {
    return String(obj);
  }
}

// Helper: base64 encode content
function toBase64(text: string): string {
  return Buffer.from(text, "utf-8").toString("base64");
}

// Helper: get file SHA if exists
async function getFileSha(owner: string, repo: string, path: string, ref?: string): Promise<string | undefined> {
  try {
    const res = await octokit.repos.getContent({ owner, repo, path, ref });
    // If it's a file, its data object has sha
    const data: any = res.data as any;
    if (data && typeof data === "object" && "sha" in data) {
      return data.sha as string;
    }
    return undefined;
  } catch (err: any) {
    // Not found is fine for create case
    if (err?.status === 404) return undefined;
    throw err;
  }
}

// Tool: list repositories
server.tool(
  "list_repos",
  {
    org: z.string().optional().describe("Organization name. If provided, list repos for this org; otherwise list for the authenticated user."),
    visibility: z.enum(["all", "public", "private"]).optional().default("all"),
    perPage: z.number().min(1).max(100).optional().default(30),
    page: z.number().min(1).optional().default(1)
  },
  async (args) => {
    const { org, visibility = "all", perPage = 30, page = 1 } = args;
    try {
      if (org) {
        const type = visibility === "all" ? "all" : visibility; // maps to listForOrg type
        const res = await octokit.repos.listForOrg({ org, type, per_page: perPage, page });
        return {
          content: [{ type: "text", text: toPretty(res.data) }]
        };
      } else {
        const res = await octokit.repos.listForAuthenticatedUser({ visibility, per_page: perPage, page });
        return {
          content: [{ type: "text", text: toPretty(res.data) }]
        };
      }
    } catch (error: any) {
      return {
        content: [{ type: "text", text: `list_repos error: ${error?.message ?? String(error)}` }],
        isError: true
      };
    }
  }
);

// Tool: get file contents
server.tool(
  "get_file",
  {
    owner: z.string(),
    repo: z.string(),
    path: z.string(),
    ref: z.string().optional().describe("Branch, tag, or commit SHA")
  },
  async (args) => {
    const { owner, repo, path, ref } = args;
    try {
      const res = await octokit.repos.getContent({ owner, repo, path, ref });
      const data: any = res.data as any;
      if (Array.isArray(data)) {
        return {
          content: [{ type: "text", text: "Requested path is a directory. Use a file path." }],
          isError: true
        };
      }
      if (data.type !== "file") {
        return {
          content: [{ type: "text", text: `Requested path is not a file: type=${data.type}` }],
          isError: true
        };
      }
      const decoded = Buffer.from(data.content, "base64").toString("utf-8");
      return {
        content: [{ type: "text", text: decoded }]
      };
    } catch (error: any) {
      return {
        content: [{ type: "text", text: `get_file error: ${error?.message ?? String(error)}` }],
        isError: true
      };
    }
  }
);

// Tool: create issue
server.tool(
  "create_issue",
  {
    owner: z.string(),
    repo: z.string(),
    title: z.string(),
    body: z.string().optional(),
    labels: z.array(z.string()).optional(),
    assignees: z.array(z.string()).optional()
  },
  async (args) => {
    const { owner, repo, title, body, labels, assignees } = args;
    try {
      const res = await octokit.issues.create({ owner, repo, title, body, labels, assignees });
      return {
        content: [{ type: "text", text: toPretty(res.data) }]
      };
    } catch (error: any) {
      return {
        content: [{ type: "text", text: `create_issue error: ${error?.message ?? String(error)}` }],
        isError: true
      };
    }
  }
);

// Tool: create or update file commit
server.tool(
  "create_commit",
  {
    owner: z.string(),
    repo: z.string(),
    path: z.string(),
    message: z.string(),
    content: z.string().describe("File content as UTF-8 text; will be base64 encoded"),
    branch: z.string().optional(),
    sha: z.string().optional().describe("Current file sha if updating; if omitted will be fetched automatically")
  },
  async (args) => {
    const { owner, repo, path, message, content, branch, sha } = args;
    try {
      const currentSha = sha ?? (await getFileSha(owner, repo, path, branch));
      const res = await octokit.repos.createOrUpdateFileContents({
        owner,
        repo,
        path,
        message,
        content: toBase64(content),
        branch,
        sha: currentSha
      });
      return {
        content: [{ type: "text", text: toPretty(res.data) }]
      };
    } catch (error: any) {
      return {
        content: [{ type: "text", text: `create_commit error: ${error?.message ?? String(error)}` }],
        isError: true
      };
    }
  }
);

// Tool: create pull request
server.tool(
  "create_pull_request",
  {
    owner: z.string(),
    repo: z.string(),
    head: z.string().describe("Branch name or repo:branch"),
    base: z.string().describe("Target branch"),
    title: z.string(),
    body: z.string().optional(),
    closes: z.number().optional().describe("If provided, PR body will include 'Closes #<number>'")
  },
  async (args) => {
    const { owner, repo, head, base, title, body, closes } = args;
    try {
      const bodyText = closes ? `${body ?? ""}\n\nCloses #${closes}`.trim() : body;
      const res = await octokit.pulls.create({ owner, repo, head, base, title, body: bodyText });
      return {
        content: [{ type: "text", text: toPretty(res.data) }]
      };
    } catch (error: any) {
      return {
        content: [{ type: "text", text: `create_pull_request error: ${error?.message ?? String(error)}` }],
        isError: true
      };
    }
  }
);

/**
 * Tool: dispatch workflow
 */
server.tool(
  "run_workflow_dispatch",
  {
    owner: z.string(),
    repo: z.string(),
    workflow_id: z.string().describe("Workflow file name or numeric ID"),
    ref: z.string().default("main"),
    inputs: z.record(z.any()).optional()
  },
  async (args) => {
    try {
      const res = await octokit.actions.createWorkflowDispatch({
        owner: args.owner,
        repo: args.repo,
        workflow_id: args.workflow_id as any,
        ref: args.ref,
        inputs: args.inputs
      });
      return {
        content: [{ type: "text", text: toPretty({ status: res.status }) }]
      };
    } catch (error: any) {
      return {
        content: [{ type: "text", text: `run_workflow_dispatch error: ${error?.message ?? String(error)}` }],
        isError: true
      };
    }
  }
);

/**
 * Tool: list workflow runs
 */
server.tool(
  "list_workflow_runs",
  {
    owner: z.string(),
    repo: z.string(),
    workflow_id: z.string(),
    status: z.enum(["completed", "in_progress", "queued"]).optional(),
    perPage: z.number().min(1).max(100).default(10),
    page: z.number().min(1).default(1)
  },
  async (args) => {
    try {
      const res = await octokit.actions.listWorkflowRuns({
        owner: args.owner,
        repo: args.repo,
        workflow_id: args.workflow_id as any,
        status: args.status,
        per_page: args.perPage,
        page: args.page
      });
      return {
        content: [{ type: "text", text: toPretty(res.data) }]
      };
    } catch (error: any) {
      return {
        content: [{ type: "text", text: `list_workflow_runs error: ${error?.message ?? String(error)}` }],
        isError: true
      };
    }
  }
);

// Connect transport
const transport = new StdioServerTransport();
await server.connect(transport);
console.error("GitHub MCP server running on stdio");