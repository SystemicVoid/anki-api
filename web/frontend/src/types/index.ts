export interface Card {
  front: string;
  back: string;
  context: string;
  tags: string[];
  source: string;
  deck: string;
  model: string;
  anki_id?: number | null;
  status: string;
  added_at?: string | null;
}

export interface ValidationWarning {
  message: string;
  severity: 'error' | 'warning' | 'info';
}

export interface CardWithValidation {
  card: Card;
  warnings: ValidationWarning[];
  index: number;
  total: number;
}

export interface CardsFileResponse {
  filename: string;
  cards: CardWithValidation[];
  total: number;
}

export interface AnkiStatus {
  connected: boolean;
  error?: string;
}

export interface AddCardResponse {
  success: boolean;
  note_id?: number;
  error?: string;
}

export interface FileStat {
  filename: string;
  total_cards: number;
  added_cards: number;
  skipped_cards: number;
  pending_cards: number;
}

export interface FileListResponse {
  files: FileStat[];
}

export type ReviewAction = 'approve' | 'edit' | 'skip' | 'quit';

export interface GenerationMessage {
  type: 'status' | 'text' | 'tool' | 'complete' | 'error';
  data: {
    message?: string;
    content?: string;
    name?: string;
    input?: any;
    filename?: string;
    step?: string;
  };
  timestamp: string;
}
