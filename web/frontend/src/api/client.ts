import type {
  AddCardResponse,
  AnkiStatus,
  Card,
  CardsFileResponse,
  CardWithValidation,
  FileBrowserResponse,
  FileListResponse,
  FileNode,
  FileStat,
} from '../types';

const API_BASE = '/api';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export async function listCardFiles(): Promise<FileStat[]> {
  const response = await fetch(`${API_BASE}/cards/files`);
  const data = await handleResponse<FileListResponse>(response);
  return data.files;
}

export async function loadCards(filename: string): Promise<CardsFileResponse> {
  const response = await fetch(`${API_BASE}/cards/${encodeURIComponent(filename)}`);
  return handleResponse<CardsFileResponse>(response);
}

export async function updateCard(
  filename: string,
  index: number,
  updates: Partial<Pick<Card, 'front' | 'back' | 'context' | 'tags'>>
): Promise<CardWithValidation> {
  const response = await fetch(`${API_BASE}/cards/${encodeURIComponent(filename)}/${index}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  });
  return handleResponse<CardWithValidation>(response);
}

export async function pingAnki(): Promise<AnkiStatus> {
  const response = await fetch(`${API_BASE}/anki/ping`);
  return handleResponse<AnkiStatus>(response);
}

export async function addCardToAnki(card: Card): Promise<AddCardResponse> {
  const response = await fetch(`${API_BASE}/anki/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(card),
  });
  return handleResponse<AddCardResponse>(response);
}

export async function approveCard(filename: string, index: number): Promise<CardWithValidation> {
  const response = await fetch(
    `${API_BASE}/cards/${encodeURIComponent(filename)}/${index}/approve`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    }
  );
  return handleResponse<CardWithValidation>(response);
}

export async function skipCard(filename: string, index: number): Promise<CardWithValidation> {
  const response = await fetch(`${API_BASE}/cards/${encodeURIComponent(filename)}/${index}/skip`, {
    method: 'POST',
  });
  return handleResponse<CardWithValidation>(response);
}

export async function browseFiles(
  path: string = '',
  mode: 'project' | 'system' = 'project',
  dirType: 'scraped' | 'cards' = 'scraped'
): Promise<FileBrowserResponse> {
  const params = new URLSearchParams({ path, mode });
  if (mode === 'project') {
    params.append('dir_type', dirType);
  }
  const response = await fetch(`${API_BASE}/files/browse?${params}`);
  return handleResponse<FileBrowserResponse>(response);
}

export async function getRecentFiles(limit: number = 10): Promise<FileNode[]> {
  const response = await fetch(`${API_BASE}/files/recent?limit=${limit}`);
  return handleResponse<FileNode[]>(response);
}
