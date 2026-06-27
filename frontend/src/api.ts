import type { ReportDetail, ReportSummary, ResearchResponse } from "./types";

const backendHelp = "无法连接后端服务。请先在项目根目录运行：python -m uvicorn app.main:app --app-dir backend --port 8000";

async function fetchApi(input: RequestInfo | URL, init?: RequestInit) {
  try {
    return await fetch(input, init);
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(backendHelp);
    }
    throw error;
  }
}

async function responseError(response: Response) {
  const detail = await response.text().catch(() => "");
  const suffix = detail ? `：${detail.slice(0, 180)}` : "";
  return new Error(`研究任务失败：HTTP ${response.status}${suffix}`);
}

export async function runResearch(query: string, useMockSearch: boolean): Promise<ResearchResponse> {
  const response = await fetchApi("/api/research", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, use_mock_search: useMockSearch })
  });

  if (!response.ok) {
    throw await responseError(response);
  }

  return response.json() as Promise<ResearchResponse>;
}

export type ResearchStreamEvent =
  | { event: "step"; step: string; message: string }
  | { event: "final"; payload: ResearchResponse }
  | { event: "error"; message: string };

export async function streamResearch(
  query: string,
  useMockSearch: boolean,
  onEvent: (event: ResearchStreamEvent) => void,
): Promise<ResearchResponse> {
  const response = await fetchApi("/api/research/events", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, use_mock_search: useMockSearch })
  });

  if (!response.ok || !response.body) {
    return runResearch(query, useMockSearch);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finalPayload: ResearchResponse | null = null;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.trim()) continue;
      const event = JSON.parse(line) as ResearchStreamEvent;
      onEvent(event);
      if (event.event === "error") {
        throw new Error(event.message);
      }
      if (event.event === "final") {
        finalPayload = event.payload;
      }
    }
  }

  if (!finalPayload) {
    throw new Error("研究事件流未返回最终结果");
  }
  return finalPayload;
}

export async function listReports(): Promise<ReportSummary[]> {
  const response = await fetchApi("/api/reports");
  if (!response.ok) {
    throw await responseError(response);
  }
  const payload = await response.json() as { reports: ReportSummary[] };
  return payload.reports;
}

export async function getReport(reportId: string): Promise<ReportDetail> {
  const response = await fetchApi(`/api/reports/${reportId}`);
  if (!response.ok) {
    throw await responseError(response);
  }
  return response.json() as Promise<ReportDetail>;
}

export async function deleteReport(reportId: string): Promise<void> {
  const response = await fetchApi(`/api/reports/${reportId}`, { method: "DELETE" });
  if (!response.ok) {
    throw await responseError(response);
  }
}
