import type {
  CardsFileResponse,
  CardWithValidation,
  AnkiStatus,
  AddCardResponse,
  FileListResponse,
  Card,
} from '../types';

const API_BASE = '/api';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export async function listCardFiles(): Promise<string[]> {
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
  const response = await fetch(
    `${API_BASE}/cards/${encodeURIComponent(filename)}/${index}`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    }
  );
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
